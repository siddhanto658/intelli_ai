"""
Dictionary API Handler
Uses Free Dictionary API (free, no key required)
Endpoint: https://api.dictionaryapi.dev/api/v2/entries/en/{word}
"""
import requests
import logging
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)


class DictionaryAPI:
    """Free Dictionary API integration."""
    
    BASE_URL = "https://api.dictionaryapi.dev/api/v2/entries/en"
    
    @staticmethod
    def define(word: str) -> Optional[str]:
        """Get definition of a word."""
        try:
            url = f"{DictionaryAPI.BASE_URL}/{word.strip().lower()}"
            response = requests.get(url, timeout=5)
            
            if response.status_code != 200:
                return None
            
            data = response.json()
            if not data or not isinstance(data, list):
                return None
            
            # Parse first meaning
            entry = data[0]
            if 'meanings' not in entry or not entry['meanings']:
                return None
            
            meaning = entry['meanings'][0]
            if 'definitions' not in meaning or not meaning['definitions']:
                return None
            
            definition = meaning['definitions'][0].get('definition', '')
            part_of_speech = meaning.get('partOfSpeech', '')
            
            result = f"{part_of_speech}: {definition}" if part_of_speech else definition
            
            # Add example if available
            example = meaning['definitions'][0].get('example')
            if example:
                result += f" Example: {example}"
            
            return result
            
        except Exception as e:
            logger.error(f"Dictionary API error: {e}")
            return None
    
    @staticmethod
    def get_phonetic(word: str) -> Optional[str]:
        """Get phonetic pronunciation."""
        try:
            url = f"{DictionaryAPI.BASE_URL}/{word.strip().lower()}"
            response = requests.get(url, timeout=5)
            
            if response.status_code != 200:
                return None
            
            data = response.json()
            if not data:
                return None
            
            entry = data[0]
            
            # Get phonetic from entry or phonetics list
            phonetic = entry.get('phonetic')
            if not phonetic and entry.get('phonetics'):
                for p in entry['phonetics']:
                    if p.get('text'):
                        phonetic = p.get('text')
                        break
            
            return phonetic
            
        except Exception as e:
            logger.error(f"Dictionary phonetic error: {e}")
            return None


def get_definition(word: str) -> Optional[str]:
    """Quick function to get definition."""
    return DictionaryAPI.define(word)


# Test
if __name__ == "__main__":
    print("Testing Dictionary API...")
    print(define("hello"))
    print(define("artificial intelligence"))