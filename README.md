# Voice Assistant с проверкой длительности аудио

Голосовой ассистент с функцией автоматического сокращения длинных ответов для обеспечения оптимальной длительности аудио.

## Особенности

- 🎙️ Голосовой интерфейс на базе LiveKit
- 🤖 GPT-4 для генерации ответов
- ⚡ Автоматическое сокращение длинных ответов
- 🔊 OpenAI TTS для преобразования текста в речь
- 📊 Точный контроль длительности аудио
- 🌐 Веб-интерфейс на Next.js

## Структура проекта

```
project/
├── api/                    # Backend на Python Flask
│   ├── app.py             # Основной API сервер
│   ├── venv/             # Виртуальное окружение для API
│   └── requirements.txt    # Зависимости API: Flask, OpenAI
├── voice-assistant-frontend/   # Frontend на Next.js
│   ├── components/        # React компоненты
│   ├── hooks/            # Кастомные React хуки
│   └── app/              # Next.js страницы
└── voice-pipeline-agent-python/  # LiveKit агент
    ├── agent.py          # Логика голосового агента
    ├── venv/            # Виртуальное окружение для агента
    └── requirements.txt   # Зависимости агента: LiveKit, OpenAI, Deepgram
```

## Установка

### Требования

- Python 3.8+
- Node.js 18+
- FFmpeg
- OpenAI API ключ
- LiveKit API ключи

### Backend (API)

API сервер использует Flask и OpenAI для валидации длительности аудио.

```bash
# Создаем отдельное виртуальное окружение для API
cd api
python -m venv venv
source venv/bin/activate  # На Windows: venv\Scripts\activate
pip install -r requirements.txt  # Установка Flask и других зависимостей API
```



Создайте `.env` файл:
```env
OPENAI_API_KEY=your_key_here
MAX_AUDIO_LENGTH=15  # Максимальная длительность аудио в секундах
```

### Frontend

```bash
cd voice-assistant-frontend
npm install
# или
pnpm install
```

Создайте `.env.local`:
```env
LIVEKIT_API_KEY=your_key_here
LIVEKIT_API_SECRET=your_secret_here
LIVEKIT_URL=your_url_here
```

### Voice Agent

Voice Agent использует LiveKit для голосового взаимодействия и имеет свой набор зависимостей.

```bash
# Создаем отдельное виртуальное окружение для агента
cd voice-pipeline-agent-python
python -m venv venv
source venv/bin/activate  # На Windows: venv\Scripts\activate
pip install -r requirements.txt  # Установка LiveKit и других зависимостей агента
```



Создайте `.env.local`:
```env
LIVEKIT_API_KEY=your_key_here
LIVEKIT_API_SECRET=your_secret_here
LIVEKIT_URL=your_url_here
OPENAI_API_KEY=your_key_here
AUDIO_LENGTH_API_URL=http://localhost:5000/validate_audio_length
```

## Запуск

1. Запустите API сервер:
```bash
cd api
source venv/bin/activate  # На Windows: venv\Scripts\activate
flask run
```

2. Запустите Frontend:
```bash
cd voice-assistant-frontend
npm run dev
# или
pnpm dev
```

3. Запустите Voice Agent:
```bash
cd voice-pipeline-agent-python
source venv/bin/activate  # На Windows: venv\Scripts\activate
python agent.py dev
```

## Как это работает

1. Пользователь говорит с ассистентом через веб-интерфейс
2. Voice Agent преобразует речь в текст и генерирует ответ через GPT
3. Перед озвучиванием ответа проверяется его длительность через API сервер
4. Если ответ слишком длинный, он автоматически сокращается с сохранением смысла
5. Сокращенный текст преобразуется в речь и воспроизводится

## Конфигурация

### Максимальная длительность аудио

Установите максимальную длительность в секундах в `.env` файле API:
```env
MAX_AUDIO_LENGTH=15
```

