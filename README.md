# INTELLI AI - Next-Gen Voice Assistant

<div align="center">

![INTELLI AI](www/assets/img/iNTELLI%20AI.png)

**Your Intelligent Desktop Companion** | *Powered by Groq, Gemini & Ollama*

[Features](#-features) • [Setup](#-setup) • [API Keys](#-api-keys) • [Contributors](#-contributors)

</div>

---

## 🎯 Overview

INTELLI is a next-generation voice-controlled AI desktop assistant with real-time speech recognition, multi-model AI support (Groq/Gemini/Ollama), conversation memory, and a modern glass-morphism UI.

### What's New in v3.0
- **Hybrid AI Brain** - Switch between Groq (fast), Gemini (smarter), Ollama (offline)
- **Speech Recognition** - Real-time voice-to-text withVosk engine
- **Text-to-Speech** - Edge-TTS for natural voice output
- **Conversation Memory** - RAG-powered long-term memory system
- **9 AI Models** - llama-3.3, mixtral, gemini-2.0-flash, and more

---

## ⚡ Features

| Category | Features |
|----------|----------|
| **Voice** | Wake word detection, Voice commands, Real-time STT, Natural TTS |
| **AI Models** | Groq (llama, mixtral), Gemini, Ollama (local) |
| **Search** | Web search, YouTube, News feed |
| **Math** | Wolfram Alpha integration |
| **Apps** | Open/control applications via voice |
| **Memory** | Conversation history, RAG retrieval |
| **UI** | Glass-morphism, Particle effects, Streaming responses |

---

## 🚀 Quick Setup

### 1. Clone & Install
```bash
git clone https://github.com/siddhanto658/intelli_ai.git
cd intelli_ai
pip install -r requirements.txt
```

### 2. Configure API Keys
Copy `.env.example` to `.env` and add your keys:

```env
# AI Providers (choose at least one)
GROQ_API_KEY=your_groq_key          # https://console.groq.com
GEMINI_API_KEY=your_gemini_key      # https://aistudio.google.com/app
OLLAMA_BASE_URL=http://localhost:11434  # Local Ollama

# Optional Services
NEWS_API_KEY=your_news_key
WOLFRAM_ALPHA_APPID=your_wolfram_id
```

### 3. Run
```bash
# Windows
run.bat

# Linux/Mac
bash install.sh
python run.py
```

---

## 📁 Project Structure

```
INTELLI_AI/
├── main.py                 # Eel web interface
├── run.py                 # Entry point
├── command.py             # Voice command processor
├── requirements.txt       # Python dependencies
├── CONFIG.md             # Configuration guide
│
├── www/                   # Web UI
│   ├── index.html        # Main interface
│   ├── main.js          # Frontend logic
│   ├── style.css        # Glass-morphism styles
│   └── assets/          # Images, audio
│
└── intelli/
    └── core/            # AI Brain
        ├── brain.py     # Multi-model AI (Groq/Gemini/Ollama)
        ├── speech.py    # TTS engine
        ├── memory.py   # Conversation memory
        └── config.py   # Configuration
```

---

## 🔑 API Keys Required

| Service | Required | Free Tier | Links |
|---------|----------|-----------|-------|
| Groq | ✅ | 14,400 req/day | [console.groq.com](https://console.groq.com) |
| Gemini | ✅ | Generous free | [aistudio.google.com](https://aistudio.google.com) |
| Ollama | Optional | Unlimited local | [ollama.com](https://ollama.com) |
| News API | Optional | 1,000 req/day | [worldnewsapi.com](https://worldnewsapi.com) |
| Wolfram | Optional | Limited | [developer.wolframalpha.com](https://developer.wolframalpha.com) |

---

## 🎤 Voice Commands

| Command | Action |
|---------|--------|
| "INTELLI" / "Computer" | Wake word - activates assistant |
| "Search for..." | Web search |
| "Play [song]" | YouTube search |
| "What's the news?" | World news summary |
| "Calculate..." | Math with Wolfram |
| "Open [app]" | Launch application |
| "Remember that..." | Store in memory |
| "What do you remember?" | Retrieve memory |

---

## 🔧 Configuration

Edit `intelli/core/config.py` or `.env`:

```python
# AI Model Settings
AI_MODEL = "llama-3.3-70b-versatile"  # or "mixtral", "gemini-2.0-flash"
TEMPERATURE = 0.7
MAX_TOKENS = 2048

# Voice Settings
WAKE_WORDS = ["INTELLI", "Computer"]
TTS_VOICE = "en-US-JennyNeural"
```

---

## 👥 Contributors

| Name | Role | GitHub |
|------|------|-------|
| **Soumyajeet Pradhan** | AI Brain & Integration | @soumyajitpradhan3373 |
| **Prabhanshu Dash** | Voice Recognition | @PrabhanshuDash |
| **Subid Sunder Barick** | UI/UX Design | @Subid-int |
| **Suman Bhuyan** | Core Engine | @bhuniyasuman448-gif |
| **Siddhanto Goswami** | Project Lead | @siddhanto658 |

---

## 📄 License

MIT License - See LICENSE file

---

<div align="center">

**Made with ❤️ by Team INTELLI**

[⭐ Star](https://github.com/siddhanto658/intelli_ai) • 
[🐛 Report Issue](https://github.com/siddhanto658/intelli_ai/issues)

</div>