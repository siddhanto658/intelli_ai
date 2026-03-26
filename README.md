# INTELLI AI Assistant

A Python-based AI voice assistant with features like voice recognition, WhatsApp integration, weather updates, YouTube control, and more.

## Features

- **Voice Recognition**: Listen and respond to voice commands
- **WhatsApp Integration**: Send messages, make calls, and video calls
- **Weather Updates**: Get current weather and temperature for any location
- **YouTube Control**: Play videos and search on YouTube
- **Application Launcher**: Open installed applications
- **Google Search**: Search the web using voice commands
- **News Reader**: Read latest news headlines
- **Hands-free Mode**: Control using hand gestures
- **Task Management**: Add, view, update, and delete tasks
- **Chatbot**: Conversational AI powered by HuggingChat
- **Screenshot**: Capture screen screenshots
- **Speed Test**: Check internet download and upload speed

## Tech Stack

- Python 3.10+
- Eel (for web-based UI)
- Speech Recognition
- pyttsx3 (Text-to-Speech)
- SQLite (Database)
- PyAutoGUI
- PyWhatKit

## Installation

```bash
pip install eel speech-recognition pyttsx3 pyautogui pywhatkit sqlite3 playsound pvporcupine hugchat
```

## Usage

```bash
python main.py
```

## Project Structure

```
├── main.py          # Main entry point
├── command.py       # Command processing and voice recognition
├── features.py      # Feature implementations
├── config.py        # Configuration
├── helper.py        # Helper functions
├── db.py           # Database operations
├── task.py         # Task management
├── NewsRead.py     # News reading feature
├── HandGesture.py  # Hand gesture control
├── calculate.py    # Calculator feature
├── www/            # Web UI files
└── INTELLI.db      # SQLite database
```

## License

MIT License
