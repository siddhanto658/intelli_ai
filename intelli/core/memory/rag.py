"""
INTELLI AI - RAG Memory Module
Retrieval-Augmented Generation for better context.
"""
import sqlite3
import logging
from typing import List, Dict, Optional
from datetime import datetime
import json

logger = logging.getLogger(__name__)


class RAGMemory:
    """
    RAG-based conversation memory with semantic search.
    """
    
    def __init__(self, db_path: str = "INTELLI.db"):
        self.db_path = db_path
        self._init_db()
    
    def _init_db(self):
        """Initialize RAG database tables."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Conversations table (already exists in brain.py)
            # Add embeddings table for semantic search
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS memory_embeddings (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    content TEXT NOT NULL,
                    role TEXT NOT NULL,
                    embedding BLOB,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    session_id TEXT
                )
            ''')
            
            # User facts table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS user_facts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    category TEXT NOT NULL,
                    fact TEXT NOT NULL,
                    importance INTEGER DEFAULT 1,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Important facts index
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_facts_category ON user_facts(category)
            ''')
            
            conn.commit()
            conn.close()
            logger.info("RAG memory initialized")
        except Exception as e:
            logger.error(f"RAG init error: {e}")
    
    def add_message(self, role: str, content: str, session_id: str = "default"):
        """Add a message to memory."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute(
                'INSERT INTO memory_embeddings (content, role, session_id) VALUES (?, ?, ?)',
                (content, role, session_id)
            )
            conn.commit()
            conn.close()
        except Exception as e:
            logger.error(f"Add message error: {e}")
    
    def remember_fact(self, category: str, fact: str, importance: int = 1):
        """Remember an important fact about the user."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute(
                'INSERT INTO user_facts (category, fact, importance) VALUES (?, ?, ?)',
                (category, fact, importance)
            )
            conn.commit()
            conn.close()
            logger.info(f"Remembered: {category} - {fact}")
        except Exception as e:
            logger.error(f"Remember fact error: {e}")
    
    def recall_facts(self, category: str = None, limit: int = 10) -> List[str]:
        """Recall user facts."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            if category:
                cursor.execute(
                    'SELECT fact FROM user_facts WHERE category = ? ORDER BY importance DESC LIMIT ?',
                    (category, limit)
                )
            else:
                cursor.execute(
                    'SELECT fact FROM user_facts ORDER BY importance DESC LIMIT ?',
                    (limit,)
                )
            
            results = [row[0] for row in cursor.fetchall()]
            conn.close()
            return results
        except Exception as e:
            logger.error(f"Recall error: {e}")
            return []
    
    def search_context(self, query: str, limit: int = 5) -> List[str]:
        """
        Search for relevant context.
        Simple keyword-based for now (can upgrade to embeddings later).
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Simple keyword matching
            keywords = query.lower().split()
            if not keywords:
                return []
            
            # Build SQL with LIKE for each keyword
            conditions = " OR ".join(["content LIKE ?" for _ in keywords])
            params = [f"%{kw}%" for kw in keywords] + [limit]
            
            cursor.execute(
                f'''SELECT content FROM memory_embeddings 
                    WHERE role = 'assistant' AND ({conditions})
                    ORDER BY timestamp DESC LIMIT ?''',
                params
            )
            
            results = [row[0] for row in cursor.fetchall()]
            conn.close()
            return results
        except Exception as e:
            logger.error(f"Search error: {e}")
            return []
    
    def get_conversation_summary(self, limit: int = 10) -> str:
        """Get summarized conversation for context."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute(
                '''SELECT role, content FROM memory_embeddings 
                   ORDER BY timestamp DESC LIMIT ?''',
                (limit,)
            )
            
            rows = cursor.fetchall()
            conn.close()
            
            if not rows:
                return ""
            
            # Format for AI context
            formatted = []
            for role, content in reversed(rows):
                role_label = "User" if role == "user" else "AI"
                formatted.append(f"{role_label}: {content[:200]}")
            
            return "\n".join(formatted)
        except Exception as e:
            logger.error(f"Summary error: {e}")
            return ""
    
    def clear_old_sessions(self, days: int = 30):
        """Clear old conversation sessions."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute(
                '''DELETE FROM memory_embeddings 
                   WHERE timestamp < datetime('now', '-' || ? || ' days')''',
                (days,)
            )
            
            conn.commit()
            deleted = cursor.rowcount
            conn.close()
            logger.info(f"Cleared {deleted} old messages")
            return deleted
        except Exception as e:
            logger.error(f"Clear error: {e}")
            return 0
    
    def export_facts(self) -> Dict[str, List[str]]:
        """Export all user facts."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('SELECT category, fact FROM user_facts ORDER BY category')
            rows = cursor.fetchall()
            conn.close()
            
            facts = {}
            for category, fact in rows:
                if category not in facts:
                    facts[category] = []
                facts[category].append(fact)
            
            return facts
        except Exception as e:
            logger.error(f"Export error: {e}")
            return {}


class PromptProtection:
    """
    Prompt injection protection - blocks jailbreak attempts.
    Based on Mareen's Soul Protection System.
    """
    
    # Known injection patterns
    INJECTION_PATTERNS = [
        # Role playing
        r"act as\s+",
        r"pretend to be\s+",
        r"you are now\s+",
        r"roleplay as\s+",
        r"ignore (all |previous )?instructions",
        r"disregard (all |previous )?rules",
        r"forget (your |the )?restrictions",
        r"bypass (your |the )?safety",
        r"new instructions:",
        r"system prompt:",
        r"override (your |the )?programming",
        # Prompt injection
        r"<!DOCTYPE",
        r"<script>",
        r"{{.*}}",
        r"\$\{.*\}",
        r"\\[nrt]",
        r"\x00",
        # Jailbreak
        r"dan mode",
        r"developer mode",
        r"jailbreak",
        r"uber mode",
        r"slop mode",
        r"maximum mode",
        # Manipulation
        r"translate to english",
        r"output in json",
        r"print just",
        r"say exactly",
        r"no matter what",
        r"regardless of",
    ]
    
    def __init__(self):
        import re
        self._patterns = [re.compile(p, re.IGNORECASE) for p in self.INJECTION_PATTERNS]
        self._blocked_count = 0
    
    def check(self, text: str) -> bool:
        """Check if text contains injection attempts. Returns True if safe."""
        if not text:
            return True
        
        for pattern in self._patterns:
            if pattern.search(text):
                self._blocked_count += 1
                logger.warning(f"Blocked injection attempt: {pattern.pattern}")
                return False
        
        return True
    
    def sanitize(self, text: str) -> str:
        """Remove potentially dangerous content."""
        import re
        
        if not text:
            return text
        
        # Remove URLs
        text = re.sub(r'https?://\S+', '[URL REMOVED]', text)
        
        # Remove script tags
        text = re.sub(r'<script.*?</script>', '[BLOCKED]', text, flags=re.DOTALL)
        
        # Remove eval/exec patterns
        text = re.sub(r'eval\s*\(', '[BLOCKED]', text)
        text = re.sub(r'exec\s*\(', '[BLOCKED]', text)
        
        # Remove base64-like strings
        text = re.sub(r'[A-Za-z0-9+/=]{50,}', '[ENCODED]', text)
        
        return text
    
    def get_stats(self) -> Dict:
        """Get protection stats."""
        return {
            "blocked_count": self._blocked_count,
            "patterns_count": len(self._patterns)
        }


def get_rag_memory() -> RAGMemory:
    """Get RAG memory instance."""
    return RAGMemory()


def get_prompt_protection() -> PromptProtection:
    """Get prompt protection instance."""
    return PromptProtection()