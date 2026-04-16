import json
import logging
import os
import time
import queue
import threading
import requests
from typing import List, Dict, Any, Callable, Optional, Generator
from intelli.core.config import get_settings

# Try new google.genai SDK first, fallback to deprecated
try:
    import google.genai as genai
    _USING_NEW_SDK = True
except ImportError:
    try:
        import google.generativeai as genai
        _USING_NEW_SDK = False
    except ImportError:
        genai = None
        _USING_NEW_SDK = None
        logging.warning("Google AI SDK not found. Install with: pip install google-genai")

logger = logging.getLogger(__name__)

# Language detection patterns
LANGUAGE_PATTERNS = {
    "hi": ["namaste", "kaise", "kya", "haan", "nahi", "acha", "bahut", "kitna", "kaun", "kaha", "kab", "kyun", "yeh", "woh", "ap", "tum", "main", "hai", "tha", "thi", "the", "hain", "ho", "ga", "gi", "ge", "raha", "rahi", "rahe", "kar", "ki", "ka", "ke", "se", "ko", "me", "mein", "pe", "par", "ke", "ka", "ki", "ke", "na", "aur", "ya", "yaa", "le", "de", "ja", "aa", "oo", "ee"],
    "ta": ["vanakkam", "epdi", "ena", "amma", "poitu", "varen", "nan", "unaku", "enaku", "sellum", "pannu", "saami", "thunivu", "mudiyum", "illai", "naan", "unga", "enga", "ava", "ivu", "ava", "ellam", "nanri"],
    "te": ["namaste", "ela", "ento", "le", "nenu", "me", "ni", "okati", "iku", "ledu", "kastam", "chudu", "ra"],
    "bn": ["namaskar", "ki", "kobe", "kemon", "achhe", "ha", "na", "eka", "duti", "tinti", "char", "pache", "amra", "apni", "tumi"],
    "mr": ["namaste", "kase", "kay", "ha", "nastar", "he", "mi", "tu", "amhi", "aplyala", "kuthla"],
    "gu": ["namaste", "kem", "cho", "to", "hu", "tame", "ama", "ek", "bb", "tri", "char", "pan", "ke", "ni"],
    "kn": ["namaste", "helu", "enu", "yaava", "illa", "hogu", "bendu", "ondu", "idu", "avu", "nivu", "nanu"],
    "ml": ["namaste", "ente", "athan", "njan", "ningal", "ningane", "ennu", "alla", "ath", "ivide", "avide"],
    "pa": ["sat shri akaal", "ki", "haan", "nhi", "ki", "tussi", "main", "tu", "eh", "uh", "ke", "da", "di", "de"],
    "or": ["namaste", "kebi", "kintu", "kahinki", "e", "be", "ra", "re", "ku", "ke", "ka", "ki"],
}

LANGUAGE_NAMES = {
    "en": "English", "hi": "Hindi", "ta": "Tamil", "te": "Telugu", 
    "bn": "Bengali", "mr": "Marathi", "gu": "Gujarati", "kn": "Kannada",
    "ml": "Malayalam", "pa": "Punjabi", "or": "Odia"
}


class ConversationMemory:
    """Persistent conversation memory using SQLite."""
    
    def __init__(self, db_path: str = "INTELLI.db"):
        self.db_path = db_path
        self._init_db()
    
    def _init_db(self):
        """Initialize database tables."""
        import sqlite3
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS conversation_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    role TEXT NOT NULL,
                    content TEXT NOT NULL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    session_id TEXT
                )
            ''')
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_session ON conversation_history(session_id)
            ''')
            conn.commit()
            conn.close()
            logger.info("Conversation memory initialized")
        except Exception as e:
            logger.error(f"Failed to init conversation memory: {e}")
    
    def add_message(self, role: str, content: str, session_id: str = "default"):
        """Add a message to history."""
        import sqlite3
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute(
                'INSERT INTO conversation_history (role, content, session_id) VALUES (?, ?, ?)',
                (role, content, session_id)
            )
            conn.commit()
            conn.close()
        except Exception as e:
            logger.error(f"Failed to add message: {e}")
    
    def get_recent(self, limit: int = 20, session_id: str = "default") -> List[Dict[str, str]]:
        """Get recent messages."""
        import sqlite3
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute(
                '''SELECT role, content FROM conversation_history 
                   WHERE session_id = ? 
                   ORDER BY timestamp DESC LIMIT ?''',
                (session_id, limit)
            )
            rows = cursor.fetchall()
            conn.close()
            return [{"role": r[0], "content": r[1]} for r in reversed(rows)]
        except Exception as e:
            logger.error(f"Failed to get messages: {e}")
            return []
    
    def clear(self, session_id: str = "default"):
        """Clear conversation history."""
        import sqlite3
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('DELETE FROM conversation_history WHERE session_id = ?', (session_id,))
            conn.commit()
            conn.close()
        except Exception as e:
            logger.error(f"Failed to clear messages: {e}")
    
    def get_conversation_for_ai(self, limit: int = 10) -> str:
        """Get formatted conversation for AI context."""
        messages = self.get_recent(limit * 2)
        if not messages:
            return ""
        
        formatted = []
        for msg in messages[-limit:]:
            role = "User" if msg["role"] == "user" else "Assistant"
            formatted.append(f"{role}: {msg['content']}")
        
        return "\n".join(formatted)


class HybridBrain:
    def __init__(self):
        self.settings = get_settings()
        self._preferred_model = "groq"
        self._groq_model = "llama-3.3-70b-versatile"
        
        # Groq API
        self._groq_api_key = os.getenv("GROQ_API_KEY", "").strip()
        self._groq_history: List[Dict[str, str]] = []
        
        # Gemini Backup
        self._gemini_ready = False
        self._using_new_sdk = _USING_NEW_SDK
        if not self.settings.use_local_llm and self.settings.gemini_api_key and self.settings.gemini_api_key != "your_gemini_api_key_here":
            if genai is not None:
                try:
                    if _USING_NEW_SDK:
                        genai.configure(api_key=self.settings.gemini_api_key)
                        self.gemini_client = genai.Client()
                        self._gemini_model = "gemini-2.0-flash"
                    else:
                        genai.configure(api_key=self.settings.gemini_api_key)
                        self.gemini_model = genai.GenerativeModel('gemini-2.0-flash')
                        self.chat_session = self.gemini_model.start_chat(history=[])
                    self._gemini_ready = True
                    logger.info("Gemini AI initialized as backup")
                except Exception as e:
                    logger.warning(f"Gemini backup init failed: {e}")
        
        # Conversation memory
        self.memory = ConversationMemory()
        
        if self._groq_api_key:
            logger.info("Groq API - PRIMARY AI configured")
        if self._gemini_ready:
            logger.info("Gemini API - BACKUP AI configured")
        if not self._groq_api_key and not self._gemini_ready:
            logger.warning("No AI API keys found!")

    def detect_language(self, text: str) -> str:
        text_lower = text.lower()
        scores = {}
        for lang, patterns in LANGUAGE_PATTERNS.items():
            score = sum(1 for word in patterns if word in text_lower)
            if score > 0:
                scores[lang] = score
        if not scores or max(scores.values()) < 2:
            return "en"
        return max(scores, key=scores.get)

    def preprocess_multilingual(self, text: str) -> str:
        detected_lang = self.detect_language(text)
        if detected_lang == "en":
            return text
        logger.info(f"Detected language: {LANGUAGE_NAMES.get(detected_lang, detected_lang)}")
        
        if detected_lang == "hi":
            text = text.replace("gaan bajao", "play song").replace("youtube khole", "open youtube")
            text = text.replace("chrome khole", "open chrome").replace("kitna baj rahe hain", "what is the time")
            text = text.replace("screenshot lo", "take screenshot").replace("system band karo", "shutdown system")
        elif detected_lang == "ta":
            text = text.replace("paatu podu", "play song").replace("youtube vaangi", "open youtube")
            text = text.replace("chrome vaangi", "open chrome")
        elif detected_lang == "te":
            text = text.replace("youtube vaadni", "open youtube").replace("chrome vaadni", "open chrome")
        
        return text

    def set_preferred_model(self, model: str, groq_model: str = None):
        self._preferred_model = model
        if groq_model:
            self._groq_model = groq_model
        logger.info(f"AI model preference set to: {model}")

    def clear_history(self):
        """Clear conversation history."""
        self._groq_history = []
        self.memory.clear()
        logger.info("Conversation history cleared")

    # ---------- Streaming Response Generator ----------
    def generate_stream(self, prompt: str, on_token: Callable[[str], None], system_prompt: str = "") -> str:
        """
        Generate streaming response with callback for each token.
        Returns the complete response when done.
        """
        from intelli.core.thread_safe import stop_listening
        processed_prompt = self.preprocess_multilingual(prompt)
        
        # Add context from memory
        context = self.memory.get_conversation_for_ai(limit=6)
        if context:
            full_prompt = f"Previous conversation:\n{context}\n\nCurrent request: {processed_prompt}"
        else:
            full_prompt = processed_prompt
        
        full_response = []
        
        # Check for stop
        if stop_listening.is_set:
            return ""
        
        # Groq Streaming
        if self._groq_api_key:
            try:
                self._groq_history.append({"role": "user", "content": full_prompt})
                messages = self._groq_history[-10:]
                
                headers = {
                    "Authorization": f"Bearer {self._groq_api_key}",
                    "Content-Type": "application/json"
                }
                payload = {
                    "model": self._groq_model,
                    "messages": messages,
                    "temperature": 0.7,
                    "max_tokens": 1024,
                    "stream": True
                }
                
                response = requests.post(
                    "https://api.groq.com/openai/v1/chat/completions",
                    headers=headers,
                    json=payload,
                    stream=True,
                    timeout=60
                )
                response.raise_for_status()
                
                for line in response.iter_lines():
                    if stop_listening.is_set:
                        break
                    if line:
                        line_text = line.decode('utf-8')
                        if line_text.startswith('data: '):
                            data = line_text[6:]
                            if data.strip() == '[DONE]':
                                break
                            try:
                                json_data = json.loads(data)
                                if 'choices' in json_data and len(json_data['choices']) > 0:
                                    delta = json_data['choices'][0].get('delta', {})
                                    if 'content' in delta:
                                        token = delta['content']
                                        full_response.append(token)
                                        on_token(token)
                            except json.JSONDecodeError:
                                continue
                
                if not stop_listening.is_set:
                    assistant_msg = ''.join(full_response)
                    self._groq_history.append({"role": "assistant", "content": assistant_msg})
                    self.memory.add_message("user", prompt)
                    self.memory.add_message("assistant", assistant_msg)
                    return assistant_msg
                
            except Exception as e:
                logger.error(f"Groq streaming error: {e}")
        
        # Fallback to Gemini non-streaming
        if self._gemini_ready:
            result = self._call_gemini(full_prompt)
            if result:
                for char in result:
                    if stop_listening.is_set:
                        break
                    full_response.append(char)
                    on_token(char)
                    time.sleep(0.02)  # Simulate streaming
                
                assistant_msg = ''.join(full_response)
                if not stop_listening.is_set:
                    self.memory.add_message("user", prompt)
                    self.memory.add_message("assistant", assistant_msg)
                    return assistant_msg
        
        return ''.join(full_response)

    # ---------- Streaming with offline fallback ----------
    def generate_stream(self, prompt: str, on_token: Callable[[str], None], system_prompt: str = "") -> str:
        """Generate streaming response with offline fallback."""
        from intelli.core.thread_safe import stop_listening
        processed_prompt = self.preprocess_multilingual(prompt)
        
        # Add context from memory
        context = self.memory.get_conversation_for_ai(limit=6)
        if context:
            full_prompt = f"Previous conversation:\n{context}\n\nCurrent request: {processed_prompt}"
        else:
            full_prompt = processed_prompt
        
        full_response = []
        
        if stop_listening.is_set:
            return ""
        
        # Try streaming APIs first
        if self._groq_api_key:
            try:
                self._groq_history.append({"role": "user", "content": full_prompt})
                messages = self._groq_history[-10:]
                
                headers = {
                    "Authorization": f"Bearer {self._groq_api_key}",
                    "Content-Type": "application/json"
                }
                payload = {
                    "model": self._groq_model,
                    "messages": messages,
                    "temperature": 0.7,
                    "max_tokens": 1024,
                    "stream": True
                }
                
                response = requests.post(
                    "https://api.groq.com/openai/v1/chat/completions",
                    headers=headers,
                    json=payload,
                    stream=True,
                    timeout=60
                )
                response.raise_for_status()
                
                for line in response.iter_lines():
                    if stop_listening.is_set:
                        break
                    if line:
                        line_text = line.decode('utf-8')
                        if line_text.startswith('data: '):
                            data = line_text[6:]
                            if data.strip() == '[DONE]':
                                break
                            try:
                                json_data = json.loads(data)
                                if 'choices' in json_data and len(json_data['choices']) > 0:
                                    delta = json_data['choices'][0].get('delta', {})
                                    if 'content' in delta:
                                        token = delta['content']
                                        full_response.append(token)
                                        on_token(token)
                            except json.JSONDecodeError:
                                continue
                
                if not stop_listening.is_set:
                    assistant_msg = ''.join(full_response)
                    self._groq_history.append({"role": "assistant", "content": assistant_msg})
                    self.memory.add_message("user", prompt)
                    self.memory.add_message("assistant", assistant_msg)
                    return assistant_msg
                
            except Exception as e:
                logger.error(f"Groq streaming error: {e}")
        
        # Try Gemini
        if self._gemini_ready:
            result = self._call_gemini(full_prompt)
            if result:
                for char in result:
                    if stop_listening.is_set:
                        break
                    full_response.append(char)
                    on_token(char)
                    time.sleep(0.02)
                
                assistant_msg = ''.join(full_response)
                if not stop_listening.is_set:
                    self.memory.add_message("user", prompt)
                    self.memory.add_message("assistant", assistant_msg)
                    return assistant_msg
        
        # Offline fallback
        offline = self._get_offline_response(processed_prompt)
        if offline:
            for char in offline:
                if stop_listening.is_set:
                    break
                full_response.append(char)
                on_token(char)
                time.sleep(0.02)
        
        return ''.join(full_response)

    # ---------- Non-streaming fallback ----------
    def generate_response(self, prompt: str, system_prompt: str = "") -> str:
        processed_prompt = self.preprocess_multilingual(prompt)
        
        if self.settings.use_local_llm or self._preferred_model == "local":
            return self._call_ollama(processed_prompt)
        
        if self._groq_api_key:
            result = self._call_groq(processed_prompt)
            if result and "encountered an error" not in result.lower() and "both my brains" not in result.lower():
                return result
            logger.warning("Groq failed, trying Gemini backup...")
        
        if self._gemini_ready:
            result = self._call_gemini(processed_prompt)
            if result is not None:
                return result
        
        # Try offline response for common queries
        offline = self._get_offline_response(processed_prompt)
        if offline:
            logger.info("Using offline response")
            return offline
        
        return "Sorry, I'm having trouble connecting to my AI brain. Please try again."

    # ---------- Offline Fallback Responses ----------
    OFFLINE_RESPONSES = {
        "hello": ["Hello! How can I help you today?", "Hi there! What can I do for you?", "Hey! I'm here to help."],
        "hi": ["Hi! How can I assist you?", "Hello! What would you like to know?", "Hey there! Ready to help."],
        "how are you": ["I'm doing great, thank you for asking!", "I'm doing well! Ready to help you.", "Fantastic! How can I help you today?"],
        "what is your name": ["I'm INTELLI, your AI assistant.", "I'm called INTELLI!", "I'm INTELLI, here to help you."],
        "what can you do": ["I can answer questions, help with tasks, search the web, play music, and much more!", "I can open apps, search the web, tell you news, and chat with you!", "I can help with many things - just ask!"],
        "thanks": ["You're welcome!", "Happy to help!", "Anytime!"],
        "thank you": ["You're welcome!", "My pleasure!", "Happy to help!"],
        "bye": ["Goodbye! Have a great day!", "Bye! Come back soon!", "See you later!"],
        "goodbye": ["Goodbye! Have a great day!", "Bye for now!", "Take care!"],
        "time": ["I can tell you the time, just ask!", "Let me know what city you're in and I can check the time.", "What time zone are you in?"],
        "weather": ["I can check the weather for you if you tell me your location.", "What's your city? I'll check the weather.", "I can look up weather - just tell me where you are."],
        "joke": ["Why don't scientists trust atoms? Because they make up everything!", "What do you call a fake pepper? A salt shaker!", "I tried to write a chemistry joke, but I couldn't get a reaction."],
        "help": ["I can help with many things! Try asking me to open apps, search the web, tell news, play music, or just chat!", "Just tell me what you need - I can open apps, search, tell time, and more!", "I respond to voice or text commands. Try saying 'open notepad' or 'what is the weather'."],
    }

    def _get_offline_response(self, prompt: str) -> Optional[str]:
        """Get a canned response for common queries when offline."""
        prompt_lower = prompt.lower().strip()
        
        for key, responses in self.OFFLINE_RESPONSES.items():
            if key in prompt_lower:
                import random
                return random.choice(responses)
        
        return None

    def _call_ollama(self, prompt: str) -> str:
        try:
            payload = {
                "model": self.settings.local_llm_model,
                "prompt": prompt,
                "stream": False
            }
            response = requests.post(self.settings.local_llm_url, json=payload, timeout=30)
            response.raise_for_status()
            return response.json().get("response", "No response from local model.")
        except Exception as e:
            logger.error(f"Local LLM Error: {e}")
            return "Sorry, my local brain encountered an error."

    def _call_gemini(self, prompt: str) -> Optional[str]:
        if not self._gemini_ready:
            return None
        try:
            if self._using_new_sdk:
                response = self.gemini_client.models.generate_content(
                    model=self._gemini_model,
                    contents=prompt
                )
                return response.text
            else:
                if not hasattr(self, 'chat_session'):
                    self.chat_session = self.gemini_model.start_chat(history=[])
                response = self.chat_session.send_message(prompt)
                return response.text
        except Exception as e:
            logger.error(f"Gemini API Error: {e}")
            return None

    def _call_groq(self, prompt: str) -> str:
        if not self._groq_api_key:
            return "API key not configured."
        try:
            self._groq_history.append({"role": "user", "content": prompt})
            messages = self._groq_history[-10:]
            
            headers = {"Authorization": f"Bearer {self._groq_api_key}", "Content-Type": "application/json"}
            payload = {
                "model": self._groq_model,
                "messages": messages,
                "temperature": 0.7,
                "max_tokens": 1024
            }
            
            response = requests.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers=headers,
                json=payload,
                timeout=30
            )
            response.raise_for_status()
            
            result = response.json()
            assistant_msg = result["choices"][0]["message"]["content"]
            self._groq_history.append({"role": "assistant", "content": assistant_msg})
            self.memory.add_message("user", prompt)
            self.memory.add_message("assistant", assistant_msg)
            return assistant_msg
        except Exception as e:
            logger.error(f"Groq API Error: {e}")
            return "Sorry, both my brains encountered errors. Please try again."

    def generate_image_prompt(self, user_request: str) -> str:
        prompt = f"Extract a concise english prompt for an image generation AI from: {user_request}"
        return self.generate_response(prompt).strip('"\'')
