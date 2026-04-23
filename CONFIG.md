# Configuration Guide for INTELLI AI

## Quick Start

Create a `.env` file in the project root:

```env
# Required: At least one AI provider
GROQ_API_KEY=gsk_your_groq_key
GEMINI_API_KEY=your_gemini_key
OLLAMA_BASE_URL=http://localhost:11434
```

## AI Models

Available models per provider:

| Provider | Model | Best For |
|----------|-------|---------|
| Groq | llama-3.3-70b-versatile | Fast & capable |
| Groq | mixtral-8x7b-32768 | Coding |
| Gemini | gemini-2.0-flash | Reasoning |
| Ollama | llama3 | Offline |

## Voice Settings

```python
WAKE_WORDS = ["INTELLI", "Computer"]
TTS_VOICE = "en-US-JennyNeural"
LANGUAGE = "en-US"
```

## UI Customization

```python
THEME = "dark"  # or "light"
PARTICLES = True
ANIMATIONS = True
```

## Performance

```python
MAX_TOKENS = 2048
TEMPERATURE = 0.7
STREAMING = True
```