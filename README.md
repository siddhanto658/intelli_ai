# INTELLI AI Assistant

A Python-based AI voice assistant with features like voice recognition, WhatsApp integration, weather updates, YouTube control, and more.

## Features

- **AI Chat**: Conversational AI powered by Groq (Llama) or Gemini
- **Voice Recognition**: Listen and respond to voice commands
- **WhatsApp Integration**: Send messages, make calls, and video calls
- **Weather Updates**: Get current weather and temperature
- **YouTube Control**: Play videos and search on YouTube
- **Google Search**: Search the web using voice commands
- **News Reader**: Read latest news headlines
- **Application Launcher**: Open installed applications
- **Screenshot**: Capture screen screenshots
- **Speed Test**: Check internet download and upload speed

## Prerequisites

- Python 3.10+
- pip
- Microphone

## Installation

1. **Clone the repository**
```bash
git clone <repo-url>
cd INTELLI_AI
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Setup API Keys**

Create a `.env` file:
```env
GROQ_API_KEY=your_groq_api_key_here
GEMINI_API_KEY=your_gemini_api_key_here
NEWS_API_KEY=your_worldnews_api_key_here
```

Get free API keys:
- **Groq**: https://console.groq.com/keys (14,400 requests/day FREE!)
- **Gemini**: https://makersuite.google.com/app/apikey
- **World News API**: https://worldnewsapi.com/

## Usage

```bash
# Run the app
python run.py
```

Then open your browser to http://localhost:8000

## Tech Stack

- Python 3.10+
- Eel (Desktop web app framework)
- Speech Recognition
- Groq API / Gemini API
- Edge TTS (Text-to-Speech)

## Project Structure

```
INTELLI_AI/
├── run.py              # Main entry point
├── main.py            # Eel app
├── command.py         # Voice commands
├── features.py        # Feature implementations
├── config.py         # Configuration
├── db.py             # Database operations
├── NewsRead.py       # News reading
├── www/              # Web UI
│   ├── index.html
│   ├── main.js
│   ├── controller.js
│   └── style.css
├── intelli/          # AI Brain Module
│   ├── core/
│   └── handlers/
└── .env              # API keys
```

## License

MIT License
