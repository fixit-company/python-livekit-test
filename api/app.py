from flask import Flask, request, jsonify
import openai
import os
from dotenv import load_dotenv
import io
import tempfile
import subprocess
import json

app = Flask(__name__)

# Load environment variables from root directory
load_dotenv(dotenv_path=os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env'))

# Get API key from environment variables
openai.api_key = os.getenv("OPENAI_API_KEY")

# Maximum allowed audio duration in seconds
MAX_AUDIO_LENGTH = int(os.getenv("MAX_AUDIO_LENGTH", "10"))

# Average speech rate (words per minute)
WORDS_PER_MINUTE = 150

def estimate_audio_duration(text):
    """Estimates audio duration based on word count"""
    # Simple word count (can be improved by considering punctuation and other factors)
    word_count = len(text.split())
    # Convert words per minute to seconds
    duration = (word_count / WORDS_PER_MINUTE) * 60
    return duration

def shorten_text_with_gpt(text, target_length_ratio):
    """Uses GPT to intelligently shorten text while maintaining natural speech patterns"""
    try:
        # Calculate target word count based on MAX_AUDIO_LENGTH and WORDS_PER_MINUTE
        current_words = len(text.split())
        target_words = int(current_words * target_length_ratio)
        
        response = openai.chat.completions.create(
            model="gpt-4",  # or gpt-3.5-turbo for cost efficiency
            messages=[
                {"role": "system", "content": """You are an expert at text summarization with a focus on spoken content. 
Your task is to shorten text while:
- Maintaining the core meaning and context
- Ensuring natural speech flow
- Strictly adhering to word count limits
- Using clear pronunciation-friendly words
- Maintaining a conversational tone suitable for text-to-speech

The text should sound natural when spoken aloud."""},
                {"role": "user", "content": f"""Please shorten the following text to approximately {target_words} words ({target_words/WORDS_PER_MINUTE*60:.1f} seconds of speech at {WORDS_PER_MINUTE} words per minute).

Original text:
{text}

Important:
- Stay as close as possible to {target_words} words
- Maintain natural speech flow
- Keep essential information
- Use clear, easily pronounceable words"""}
            ],
            temperature=0.7,
            max_tokens=1000
        )
        app.logger.info(response.choices[0].message.content)
        return response.choices[0].message.content
    except Exception as e:
        app.logger.error(f"Error shortening text with GPT: {e}")
        # Return original text in case of error
        return text

def get_audio_duration_with_tts(text):
    """Generates audio using OpenAI TTS and returns its duration in seconds"""
    try:
        response = openai.audio.speech.create(
            model="tts-1",
            voice="ash",
            input=text
        )
        
        # Save audio to temporary file
        with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as temp_file:
            temp_file.write(response.content)
            temp_file_path = temp_file.name

        # Use ffprobe to get duration
        cmd = [
            'ffprobe',
            '-v', 'quiet',
            '-print_format', 'json',
            '-show_format',
            temp_file_path
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        duration = float(json.loads(result.stdout)['format']['duration'])
        
        # Delete temporary file
        os.unlink(temp_file_path)
        
        return duration
    except Exception as e:
        app.logger.error(f"Error generating TTS audio: {e}")
        # In case of error, return estimate based on word count
        return estimate_audio_duration(text)

@app.route('/validate_audio_length', methods=['POST'])
def validate_audio_length():
    data = request.json
    text = data.get('text', '')
    
    app.logger.info(f"Maximum allowed audio duration: {MAX_AUDIO_LENGTH} seconds")
    
    # Get actual audio duration through TTS
    actual_duration = get_audio_duration_with_tts(text)
    app.logger.info(f"Generated audio duration: {actual_duration:.2f} seconds")
    
    # If length exceeds maximum, shorten the text
    if actual_duration > MAX_AUDIO_LENGTH:
        app.logger.info(f"Audio exceeds allowed duration by {actual_duration - MAX_AUDIO_LENGTH:.2f} seconds")
        
        # Calculate required shortening ratio
        target_ratio = MAX_AUDIO_LENGTH / actual_duration
        app.logger.info(f"Need to shorten text by {1/target_ratio:.2f} times")
        
        # Shorten text using GPT
        modified_text = shorten_text_with_gpt(text, target_ratio)
        
        # Check duration of shortened text
        new_duration = get_audio_duration_with_tts(modified_text)
        app.logger.info(f"Duration after first shortening: {new_duration:.2f} seconds")
        
        # If text is still too long, try shortening again
        if new_duration > MAX_AUDIO_LENGTH:
            app.logger.info(f"Additional shortening required, exceeds by {new_duration - MAX_AUDIO_LENGTH:.2f} seconds")
            modified_text = shorten_text_with_gpt(modified_text, MAX_AUDIO_LENGTH / new_duration)
            new_duration = get_audio_duration_with_tts(modified_text)
            app.logger.info(f"Final duration: {new_duration:.2f} seconds")
        
        return jsonify({
            'modified': True,
            'text': modified_text,
            'original_duration': actual_duration,
            'new_duration': new_duration,
            'max_allowed_duration': MAX_AUDIO_LENGTH
        })
    
    # If length is within limits, return original text
    app.logger.info(f"Duration is within limits, text doesn't need shortening")
    return jsonify({
        'modified': False,
        'text': text,
        'duration': actual_duration,
        'max_allowed_duration': MAX_AUDIO_LENGTH
    })

if __name__ == '__main__':
    # Get port from environment variables or use default port
    port = int(os.getenv("API_PORT", "5000"))
    app.run(debug=True, host='0.0.0.0', port=port) 