# Contributor Guidelines - INTELLI AI

## Team Members

| Roll No. | Name | Responsibility |
|----------|------|----------------|
| 1 | Soumyajeet Pradhan | AI Brain Integration (Groq, Gemini, Ollama) |
| 2 | Prabhanshu Dash | Voice Recognition (STT, Vosk) |
| 3 | Subid Sunder Barick | UI/UX Design, Frontend |
| 4 | Suman Bhuyan | Core Engine, Memory System |
| 5 | Siddhanto Goswami | Project Lead, Backend |

---

## Project Structure

```
INTELLI_AI/
├── main.py              - Eel web server
├── run.py               - Application entry
├── command.py           - Voice command processor
├── www/                 - Web UI
│   ├── index.html       - Main interface
│   ├── main.js         - Frontend logic
│   ├── style.css       - Glass-morphism styles
│   └── assets/         - Images, audio
├── intelli/            - Core modules
│   └── core/
│       ├── brain.py     - AI model integration
│       ├── speech.py   - Text-to-speech
│       ├── memory.py   - Conversation memory
│       └── config.py    - Configuration
├── docs/               - Project documentation
├── tests/              - Unit tests
└── requirements.txt    - Python dependencies
```

---

## Development Setup

### Prerequisites
- Python 3.10+
- Git
- API keys (Groq, Gemini, Ollama)

### Setup Commands
```bash
# Clone
git clone https://github.com/siddhanto658/intelli_ai.git
cd intelli_ai

# Create venv
python -m venv venv

# Activate (Windows)
venv\Scripts\activate

# Activate (Linux/Mac)
source venv/bin/activate

# Install
pip install -r requirements.txt
```

---

## Coding Standards

### Python
- Follow PEP 8
- Use type hints where possible
- Document functions with docstrings

### JavaScript
- Use ES6+ features
- Keep code modular

---

## Git Workflow

### Making Changes
```bash
# Create branch
git checkout -b feature/your-feature

# Make changes
# ...

# Commit
git add .
git commit -m "feat: Add new feature"

# Push
git push origin feature/your-feature
```

### Merge to Main
```bash
# Pull latest
git pull origin main

# Resolve any conflicts

# Push
git push origin main
```

---

## Testing

### Run Tests
```bash
pytest tests/
```

---

## Communication

- Weekly meetings
- GitHub Issues for bugs
- Discord for quick discussions

---

## License

MIT License