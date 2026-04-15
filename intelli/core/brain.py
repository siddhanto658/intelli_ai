import json
import logging
import os
import time
import requests
import google.generativeai as genai
from typing import List, Dict, Any
from intelli.core.config import get_settings

logger = logging.getLogger(__name__)

class HybridBrain:
    def __init__(self):
        self.settings = get_settings()
        self.history: List[Dict[str, str]] = []
        
        # Primary: Gemini
        self._gemini_ready = False
        if not self.settings.use_local_llm and self.settings.gemini_api_key:
            try:
                genai.configure(api_key=self.settings.gemini_api_key)
                self.gemini_model = genai.GenerativeModel('gemini-2.0-flash')
                self.chat_session = self.gemini_model.start_chat(history=[])
                self._gemini_ready = True
            except Exception as e:
                logger.warning(f"Gemini init failed: {e}")

        # Fallback: Groq (free, 14400 req/day, no SDK needed)
        self._groq_api_key = os.getenv("GROQ_API_KEY", "").strip()
        self._groq_model = "llama-3.3-70b-versatile"
        self._groq_history: List[Dict[str, str]] = []

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
        full_prompt = f"{system_prompt}\nUser: {prompt}" if system_prompt else prompt
        
        if self.settings.use_local_llm:
            return self._call_ollama(full_prompt)
        
        # Try Gemini first
        if self._gemini_ready:
            result = self._call_gemini(full_prompt)
            if result is not None:
                return result
        
        # Fallback to Groq
        groq_prompt = full_prompt
        if system_prompt and not self._groq_history:
            # Inject system prompt as first message
            self._groq_history.append({"role": "system", "content": system_prompt})
            groq_prompt = prompt  # System context already added
        
        return self._call_groq(groq_prompt)

    def generate_image_prompt(self, user_request: str) -> str:
        prompt = f"Extract a concise english prompt for an image generation AI from the following user request. Just reply with the prompt string, nothing else: {user_request}"
        return self.generate_response(prompt).strip('\"\'')
