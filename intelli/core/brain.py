import json
import logging
import os
import time
import requests
import google.generativeai as genai
from typing import List, Dict, Any
from intelli.core.config import get_settings

logger = logging.getLogger(__name__)

# Language detection patterns for common Indian languages
LANGUAGE_PATTERNS = {
    "hi": ["namaste", "kaise", "kya", "haan", "nahi", "acha", "bahut", "kitna", "kaun", "kaha", "kab", "kyun", "yeh", "woh", "ap", "tum", "main", "hai", "tha", "thi", "the", "hain", "ho", "ga", "gi", "ge", "raha", "rahi", "rahe", "kar", "ki", "ka", "ke", "se", "ko", "me", "mein", "pe", "par", "ke", "ka", "ki", "ke", "na", "aur", "ya", "yaa", "le", "de", "ja", "aa", "oo", "ee"],
    "ta": ["vanakkam", "epdi", "ena", "amma", "poitu", "varen", "nan", "unaku", "enaku", "sellum", "pannu", "saami", "thunivu", "mudiyum", "illai", "naan", "unga", "enga", "ava", "ivu", "ava", "ellam", "nanri", "thank you"],
    "te": ["namaste", " ela", " ento", " le", "nenu", "me", "ni", "okati", "iku", "ledu", "kastam", "chudu", "ra", "ni", "me", "ka", "ki", "ke", "raa", "amma", "tq"],
    "bn": ["namaskar", "ki", "kobe", "kemon", "achhe", "ha", "na", "eka", "duti", "tinti", "char", "pache", "amra", "apni", "tumi", "se", "ei", "oi", "je", "na", "to", "hole", "kintu", "eba", "oy"],
    "mr": ["namaste", "kase", "kay", "ha", "nastar", "he", "mi", "tu", "amhi", "aplyala", "kuthla", "ka", "chi", "che", "chya", "la", "li", "le", "ne", "ya", "ye", "ra", "ri", "re"],
    "gu": ["namaste", "kem", "cho", "to", "hu", "tame", "ama", "ek", "bb", "tri", "char", "pan", "ke", "ni", "ne", "na", "ma", "la", "li", "le", "ra", "ri", "re"],
    "kn": ["namaste", "helu", "enu", "yaava", "illa", "hogu", "bendu", "ondu", "idu", "avu", "nivu", "nanu", "nam", "tq"],
    "ml": ["namaste", "ente", "athan", "njan", "ningal", "ningane", "ennu", "alla", "ath", "ivide", "avide", "poyi", "vannu", "tq"],
    "pa": ["sat shri akaal", "ki", "haan", "nhi", "ki", "tussi", "main", "tu", "eh", "uh", "ke", "da", "di", "de", "nu", "no", "te", "ti", "to"],
    "ta": ["vanakkam"],
    "or": ["namaste", "kebi", "kintu", "kahinki", "e", "be", "ra", "re", "ku", "ke", "ka", "ki"],
}

# Translation dictionaries (common words for quick translation)
TRANSLATIONS = {
    "hi": {
        "play song": "gaan bajao", "open youtube": "youtube khole", "open chrome": "chrome khole",
        "what is the time": "kitna baj rahe hain", "what is the date": "aaj ki taareekh kya hai",
        "search": "socho", "play": "bajao", "open": "khole", "close": "band karo",
        "take screenshot": "screenshot lo", "shutdown": "system band karo",
        "send message": "message bhejo", "call": "call karo", "video call": "video call karo",
    },
    "ta": {
        "play song": "paatu podu", "open youtube": "youtube vaangi", "open chrome": "chrome vaangi",
        "what is the time": "evla time aguthu", "what is the date": "enna date aguthu",
        "search": "seekama", "play": "podu", "open": "vaangi", "close": "mudi",
        "take screenshot": "screenshot takku", "shutdown": "system mukka",
        "send message": "message send pannu", "call": "call pannu", "video call": "video call pannu",
    },
}

# Language code to name mapping
LANGUAGE_NAMES = {
    "en": "English", "hi": "Hindi", "ta": "Tamil", "te": "Telugu", 
    "bn": "Bengali", "mr": "Marathi", "gu": "Gujarati", "kn": "Kannada",
    "ml": "Malayalam", "pa": "Punjabi", "or": "Odia", "ta": "Tamil"
}

class HybridBrain:
    def __init__(self):
        self.settings = get_settings()
        self.history: List[Dict[str, str]] = []
        self._preferred_model = "groq"  # Default to Groq
        self._groq_model = "llama-3.3-70b-versatile"
        
        # Primary: Groq (free, 14400 req/day)
        self._groq_api_key = os.getenv("GROQ_API_KEY", "").strip()
        self._groq_history: List[Dict[str, str]] = []
        
        # Backup: Gemini
        self._gemini_ready = False
        if not self.settings.use_local_llm and self.settings.gemini_api_key and self.settings.gemini_api_key != "your_gemini_api_key_here":
            try:
                genai.configure(api_key=self.settings.gemini_api_key)
                self.gemini_model = genai.GenerativeModel('gemini-2.0-flash')
                self.chat_session = self.gemini_model.start_chat(history=[])
                self._gemini_ready = True
                logger.info("Gemini AI initialized as backup")
            except Exception as e:
                logger.warning(f"Gemini backup init failed: {e}")

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
            text = text.replace("chrome vaangi", "open chrome").replace("evla time aguthu", "what is the time")
        elif detected_lang == "te":
            text = text.replace("youtube vaadni", "open youtube").replace("chrome vaadni", "open chrome")
        
        return text

    def set_preferred_model(self, model: str, groq_model: str = None):
        """Set preferred AI model from frontend settings."""
        self._preferred_model = model
        if groq_model:
            self._groq_model = groq_model
        logger.info(f"AI model preference set to: {model}")

    # ---------- Ollama (Local) ----------
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

    # ---------- Gemini (Cloud Primary) ----------
    def _call_gemini(self, prompt: str) -> str:
        if not self.chat_session:
            return None  # Signal to try fallback
        
        for attempt in range(2):
            try:
                response = self.chat_session.send_message(prompt)
                return response.text
            except Exception as e:
                error_str = str(e)
                if "429" in error_str or "quota" in error_str.lower():
                    wait_time = (attempt + 1) * 3
                    logger.warning(f"Gemini rate limited (attempt {attempt+1}/2). Waiting {wait_time}s...")
                    time.sleep(wait_time)
                    continue
                else:
                    logger.error(f"Gemini API Error: {e}")
                    return None  # Signal to try fallback
        
        logger.warning("Gemini exhausted, switching to fallback.")
        return None  # Signal to try fallback

    # ---------- Groq (Cloud Fallback - 14,400 req/day FREE) ----------
    def _call_groq(self, prompt: str) -> str:
        if not self._groq_api_key:
            return "My AI brain is rate limited and no backup is configured. Please add a free Groq API key to your .env file."
        
        try:
            # Maintain conversation history for context
            self._groq_history.append({"role": "user", "content": prompt})
            
            # Keep only last 10 messages to avoid token limits
            messages = self._groq_history[-10:]
            
            headers = {
                "Authorization": f"Bearer {self._groq_api_key}",
                "Content-Type": "application/json"
            }
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
            return assistant_msg
            
        except Exception as e:
            logger.error(f"Groq API Error: {e}")
            return "Sorry, both my primary and backup brain encountered errors. Please try again in a moment."

    # ---------- Main Entry Point ----------
    def generate_response(self, prompt: str, system_prompt: str = "") -> str:
        processed_prompt = self.preprocess_multilingual(prompt)
        full_prompt = f"{system_prompt}\nUser: {processed_prompt}" if system_prompt else processed_prompt
        
        # Handle local LLM
        if self.settings.use_local_llm or self._preferred_model == "local":
            return self._call_ollama(full_prompt)
        
        # PRIMARY: Groq first
        if self._groq_api_key:
            groq_prompt = full_prompt
            if system_prompt and not self._groq_history:
                self._groq_history.append({"role": "system", "content": system_prompt})
                groq_prompt = prompt
            result = self._call_groq(groq_prompt)
            if result and "encountered an error" not in result.lower() and "rate limited" not in result.lower():
                return result
            logger.warning("Groq failed, trying Gemini backup...")
        
        # BACKUP: Gemini
        if self._gemini_ready:
            result = self._call_gemini(full_prompt)
            if result is not None:
                return result
        
        return "Sorry, I'm having trouble connecting to my AI brain. Please try again."

    def generate_image_prompt(self, user_request: str) -> str:
        prompt = f"Extract a concise english prompt for an image generation AI from the following user request. Just reply with the prompt string, nothing else: {user_request}"
        return self.generate_response(prompt).strip('\"\'')
