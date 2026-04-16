# INTELLI AI - Voice-Controlled Desktop Assistant

## 🎯 Overview

INTELLI is a voice-controlled AI desktop assistant powered by Groq, featuring wake word detection, streaming responses, and conversation memory.

---

## ⚡ Features

- **Wake Word Detection** - Say "INTELLI" or "Computer" to activate
- **Voice Commands** - Natural language voice input
- **Streaming AI Responses** - Real-time text generation via Groq API
- **Multilingual Support** - English, Hindi, Tamil, Telugu, Bengali, and more
- **Web Search** - Google & YouTube integration
- **News Feed** - World news API integration
- **Math & Science** - Wolfram Alpha for calculations
- **App Control** - Open applications via voice
- **Cross-Platform** - Windows, macOS, Linux support

---

## 🔧 Setup

### 1. Clone & Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure API Keys
Create a `.env` file (copy from `.env.example`):

```env
# AI Brain - Get key at https://console.groq.com/keys
GROQ_API_KEY=your_groq_api_key

# News - Get key at https://worldnewsapi.com/
NEWS_API_KEY=your_news_api_key

# Math/Calculations - Get key at https://developer.wolframalpha.com/
WOLFRAM_ALPHA_API_KEY=your_wolfram_key
```

### 3. Run
```bash
python run.py
```

---

## 📁 Project Structure

```
INTELLI/
├── command.py          # Voice command handler
├── features.py         # Feature implementations
├── run.py             # Main entry point
├── brain.py           # AI brain (deprecated - use intelli/core/brain.py)
├── main.py            # Eel web interface
├── www/               # Web UI (HTML/CSS/JS)
└── intelli/
    └── core/
        ├── brain.py    # AI brain (Groq + memory)
        ├── speech.py   # TTS (edge-tts)
        └── memory/     # RAG memory system
```

---

## 🔑 API Keys Required

| Service | Required | Free Tier |
|---------|----------|-----------|
| Groq | ✅ Yes | 14,400 req/day |
| World News API | ✅ Yes | 1,000 req/day |
| Wolfram Alpha | Optional | Limited |

---

## 👥 Contributors

- **Siddhanto Goswami** - siddhantogoswami7@gmail.com
- **Subid-int** - subidbarick9810@gmail.com

---

## 📄 License

MIT License
