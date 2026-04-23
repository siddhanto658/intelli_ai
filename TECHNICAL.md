# INTELLI AI - Technical Specifications

## System Requirements

### Hardware Requirements
| Component | Minimum | Recommended |
|-----------|---------|-------------|
| Processor | Intel Core i5 | Intel Core i7 |
| RAM | 8 GB | 16 GB |
| Storage | 10 GB SSD | 25 GB SSD |
| Microphone | Built-in | External USB |
| Internet | 10 Mbps | 50 Mbps |

### Software Requirements
| Software | Version |
|----------|---------|
| Python | 3.10+ |
| Windows 10+ / Ubuntu 20.04+ | - |
| Git | 2.30+ |

---

## Installation Guide

### Step 1: Clone Repository
```bash
git clone https://github.com/siddhanto658/intelli_ai.git
cd intelli_ai
```

### Step 2: Create Virtual Environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Configure API Keys
Create `.env` file:
```env
# Required - At least one AI provider
GROQ_API_KEY=your_groq_key_here

# Optional - Additional AI providers
GEMINI_API_KEY=your_gemini_key_here
OLLAMA_BASE_URL=http://localhost:11434

# Optional - Other services
NEWS_API_KEY=your_news_api_key
WOLFRAM_ALPHA_APPID=your_wolfram_id
```

### Step 5: Run Application
```bash
# Windows
run.bat

# Linux/Mac
python run.py
```

---

## Configuration Options

### AI Models Configuration
```python
# In intelli/core/config.py

# Primary AI Model
AI_MODEL = "llama-3.3-70b-versatile"  # Options: llama-3.3-70b, mixtral-8x7b, gemini-2.0-flash

# Temperature (creativity)
TEMPERATURE = 0.7  # 0.0 - 1.0

# Max tokens per response
MAX_TOKENS = 2048
```

### Voice Settings
```python
# Wake words
WAKE_WORDS = ["INTELLI", "Computer"]

# Text-to-Speech voice
TTS_VOICE = "en-US-JennyNeural"

# Speech recognition language
LANGUAGE = "en-US"
```

### UI Customization
```python
# Dark mode
THEME = "dark"

# Enable animations
PARTICLES = True
ANIMATIONS = True

# Chat history
MAX_HISTORY = 50
```

---

## API Keys Setup

### Getting Groq API Key
1. Visit https://console.groq.com
2. Sign up/Login
3. Create API Key
4. Copy to .env file

### Getting Gemini API Key
1. Visit https://aistudio.google.com/app
2. Create API key
3. Copy to .env file

### Getting Ollama (Offline)
1. Visit https://ollama.com
2. Download and install
3. Run `ollama serve`
4. Default URL: http://localhost:11434

---

## Troubleshooting

### Issue: Microphone not detected
```bash
# List audio devices (Linux)
pactl list sources

# Check Windows microphone settings
# Settings > Privacy > Microphone
```

### Issue: API key errors
```bash
# Verify key in .env file
# Check no extra spaces or quotes
```

### Issue: Ollama not connecting
```bash
# Start Ollama service
ollama serve

# Default port is 11434
```

### Issue: Module not found
```bash
# Reinstall requirements
pip install -r requirements.txt
```

---

## File Descriptions

| File | Purpose |
|------|---------|
| `main.py` | Eel web interface |
| `run.py` | Application entry point |
| `command.py` | Voice command processor |
| `brain.py` | AI model integration |
| `speech.py` | Text-to-speech |
| `memory.py` | Conversation memory |
| `www/index.html` | Main UI |
| `www/main.js` | Frontend logic |
| `www/style.css` | Visual styles |

---

## Performance Optimization

1. **Use SSD** for faster loading
2. **Close background apps** during use
3. **Use headphones** for better voice recognition
4. **Stable internet** for cloud AI models

---

## License

MIT License - See LICENSE file