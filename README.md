# Voice Assistant with Audio Duration Check

A voice assistant with automatic shortening of long responses to ensure optimal audio duration.

## Features

- 🎙️ Voice interface based on LiveKit
- 🤖 GPT-4 for response generation
- ⚡ Automatic shortening of long responses
- 🔊 OpenAI TTS for text-to-speech conversion
- 📊 Precise audio duration control
- 🌐 Web interface on Next.js

## Project Structure

```
project/
├── api/                    # Backend on Python Flask
│   ├── app.py             # Main API server
│   ├── venv/             # Virtual environment for API
│   └── requirements.txt    # API dependencies: Flask, OpenAI
├── voice-assistant-frontend/   # Frontend on Next.js
│   ├── components/        # React components
│   ├── hooks/            # Custom React hooks
│   └── app/              # Next.js pages
└── voice-pipeline-agent-python/  # LiveKit agent
    ├── agent.py          # Voice agent logic
    ├── venv/            # Virtual environment for agent
    └── requirements.txt   # Agent dependencies: LiveKit, OpenAI, Deepgram
```

## Installation

### Requirements

- Python 3.8+
- Node.js 18+
- FFmpeg
- OpenAI API key
- LiveKit API keys

### Backend (API)

The API server uses Flask and OpenAI for audio duration validation.

```bash
# Create a separate virtual environment for API
cd api
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt  # Install Flask and other API dependencies
```

Create a `.env` file:
```env
OPENAI_API_KEY=your_key_here
MAX_AUDIO_LENGTH=15  # Maximum audio duration in seconds
```

### Frontend

```bash
cd voice-assistant-frontend
npm install
# or
pnpm install
```

Create `.env.local`:
```env
LIVEKIT_API_KEY=your_key_here
LIVEKIT_API_SECRET=your_secret_here
LIVEKIT_URL=your_url_here
```

### Voice Agent

Voice Agent uses LiveKit for voice interaction and has its own set of dependencies.

```bash
# Create a separate virtual environment for the agent
cd voice-pipeline-agent-python
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt  # Install LiveKit and other agent dependencies
```

Create `.env.local`:
```env
LIVEKIT_API_KEY=your_key_here
LIVEKIT_API_SECRET=your_secret_here
LIVEKIT_URL=your_url_here
OPENAI_API_KEY=your_key_here
AUDIO_LENGTH_API_URL=http://localhost:5000/validate_audio_length
```

## Running the Application

1. Start the API server:
```bash
cd api
source venv/bin/activate  # On Windows: venv\Scripts\activate
flask run
```

2. Start the Frontend:
```bash
cd voice-assistant-frontend
npm run dev
# or
pnpm dev
```

3. Start the Voice Agent:
```bash
cd voice-pipeline-agent-python
source venv/bin/activate  # On Windows: venv\Scripts\activate
python agent.py dev
```

## How It Works

1. User speaks with the assistant through the web interface
2. Voice Agent converts speech to text and generates a response using GPT
3. Before converting to speech, the response duration is checked via the API server
4. If the response is too long, it is automatically shortened while preserving meaning
5. The shortened text is converted to speech and played back

## Configuration

### Maximum Audio Duration

Set the maximum duration in seconds in the API's `.env` file:
```env
MAX_AUDIO_LENGTH=15
```

### TTS Voice Selection

You can change the TTS voice in the agent's `.env` file:
```env
TTS_VOICE=alloy  # Available options: alloy, echo, fable, onyx, nova, shimmer
```

## Troubleshooting

### Text and Audio Synchronization Issues

If you notice that the displayed text doesn't match the audio:
1. Make sure the API server is running and accessible
2. Check that the `AUDIO_LENGTH_API_URL` in the agent's `.env` file is correct
3. Verify that the maximum audio duration is set appropriately

### Virtual Environment Issues

If you encounter dependency-related errors:
1. Make sure you're using the correct virtual environment for each component
2. Verify that all dependencies are installed in the appropriate environment
3. Remember that API and Voice Agent use different virtual environments with different sets of dependencies

## License

MIT

