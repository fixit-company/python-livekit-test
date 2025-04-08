from flask import Flask, request, jsonify
import openai
import os
from dotenv import load_dotenv
import io
import tempfile
import subprocess
import json

app = Flask(__name__)

# Загружаем переменные окружения из корневой директории
load_dotenv(dotenv_path=os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env'))

# Получаем API ключ из переменных окружения
openai.api_key = os.getenv("OPENAI_API_KEY")

# Максимальная допустимая длина аудио в секундах
MAX_AUDIO_LENGTH = int(os.getenv("MAX_AUDIO_LENGTH", "10"))

# Примерная скорость речи (слов в минуту)
WORDS_PER_MINUTE = 150

def estimate_audio_duration(text):
    """Оценивает длительность аудио на основе количества слов"""
    # Простой подсчет слов (можно улучшить, учитывая знаки препинания и другие факторы)
    word_count = len(text.split())
    # Конвертируем слова в минуту в секунды
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
    """Генерирует аудио с помощью OpenAI TTS и возвращает его длительность в секундах"""
    try:
        response = openai.audio.speech.create(
            model="tts-1",
            voice="ash",
            input=text
        )
        
        # Сохраняем аудио во временный файл
        with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as temp_file:
            temp_file.write(response.content)
            temp_file_path = temp_file.name

        # Используем ffprobe для получения длительности
        cmd = [
            'ffprobe',
            '-v', 'quiet',
            '-print_format', 'json',
            '-show_format',
            temp_file_path
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        duration = float(json.loads(result.stdout)['format']['duration'])
        
        # Удаляем временный файл
        os.unlink(temp_file_path)
        
        return duration
    except Exception as e:
        app.logger.error(f"Error generating TTS audio: {e}")
        # В случае ошибки возвращаем оценку на основе количества слов
        return estimate_audio_duration(text)

@app.route('/validate_audio_length', methods=['POST'])
def validate_audio_length():
    data = request.json
    text = data.get('text', '')
    
    app.logger.info(f"Максимальная допустимая длительность аудио: {MAX_AUDIO_LENGTH} секунд")
    
    # Получаем реальную длительность аудио через TTS
    actual_duration = get_audio_duration_with_tts(text)
    app.logger.info(f"Длительность сгенерированного аудио: {actual_duration:.2f} секунд")
    
    # Если длина превышает максимальную, сокращаем текст
    if actual_duration > MAX_AUDIO_LENGTH:
        app.logger.info(f"Аудио превышает допустимую длительность на {actual_duration - MAX_AUDIO_LENGTH:.2f} секунд")
        
        # Вычисляем необходимый коэффициент сокращения
        target_ratio = MAX_AUDIO_LENGTH / actual_duration
        app.logger.info(f"Необходимо сократить текст в {1/target_ratio:.2f} раз")
        
        # Сокращаем текст с помощью GPT
        modified_text = shorten_text_with_gpt(text, target_ratio)
        
        # Проверяем длительность сокращенного текста
        new_duration = get_audio_duration_with_tts(modified_text)
        app.logger.info(f"Длительность после первого сокращения: {new_duration:.2f} секунд")
        
        # Если текст всё ещё слишком длинный, пробуем ещё раз сократить
        if new_duration > MAX_AUDIO_LENGTH:
            app.logger.info(f"Требуется дополнительное сокращение, превышение на {new_duration - MAX_AUDIO_LENGTH:.2f} секунд")
            modified_text = shorten_text_with_gpt(modified_text, MAX_AUDIO_LENGTH / new_duration)
            new_duration = get_audio_duration_with_tts(modified_text)
            app.logger.info(f"Финальная длительность: {new_duration:.2f} секунд")
        
        return jsonify({
            'modified': True,
            'text': modified_text,
            'original_duration': actual_duration,
            'new_duration': new_duration,
            'max_allowed_duration': MAX_AUDIO_LENGTH
        })
    
    # Если длина в пределах нормы, возвращаем исходный текст
    app.logger.info(f"Длительность в пределах нормы, текст не требует сокращения")
    return jsonify({
        'modified': False,
        'text': text,
        'duration': actual_duration,
        'max_allowed_duration': MAX_AUDIO_LENGTH
    })

if __name__ == '__main__':
    # Получаем порт из переменных окружения или используем порт по умолчанию
    port = int(os.getenv("API_PORT", "5000"))
    app.run(debug=True, host='0.0.0.0', port=port) 