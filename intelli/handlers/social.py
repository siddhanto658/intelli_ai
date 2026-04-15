from typing import Callable, Optional
from intelli.core.brain import HybridBrain
from intelli.core.memory import MemoryManager

class SocialHandlers:
    def __init__(
        self,
        speak: Callable[[str], None],
        takecommand: Callable[[], str],
        permission_checker: Callable[[str], bool],
        brain: Optional[HybridBrain] = None,
        memory: Optional[MemoryManager] = None,
    ):
        self.speak = speak
        self.takecommand = takecommand
        self.permission_checker = permission_checker
        self.brain = brain
        self.memory = memory



    def handle_chat_fallback(self, query: str) -> bool:
        if not self.brain:
            self.speak("My AI brain is currently disconnected.")
            return True
            
        system_prompt = "You are INTELLI, a personal AI companion. Be concise, friendly, helpful, and energetic."
        if self.memory:
            facts = self.memory.recall("user_preferences")
            if facts:
                system_prompt += f"\nKnown facts about user: {', '.join(facts)}"
                
        response = self.brain.generate_response(query, system_prompt=system_prompt)
        self.speak(response)
        return True

