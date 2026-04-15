import sqlite3
import logging
from typing import List, Tuple

logger = logging.getLogger(__name__)

class MemoryManager:
    def __init__(self, db_path: str = "INTELLI.db"):
        self.db_path = db_path
        self._init_db()
        
    def _init_db(self):
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    '''CREATE TABLE IF NOT EXISTS user_memory (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        category TEXT NOT NULL,
                        fact TEXT NOT NULL,
                        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                    )'''
                )
                conn.commit()
        except sqlite3.Error as e:
            logger.error(f"Error initializing memory DB: {e}")

    def remember(self, category: str, fact: str):
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO user_memory (category, fact) VALUES (?, ?)",
                    (category, fact)
                )
                conn.commit()
        except sqlite3.Error as e:
            logger.error(f"Error saving memory: {e}")

    def recall(self, category: str = None) -> List[str]:
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                if category:
                    cursor.execute("SELECT fact FROM user_memory WHERE category = ?", (category,))
                else:
                    cursor.execute("SELECT fact FROM user_memory")
                return [row[0] for row in cursor.fetchall()]
        except sqlite3.Error as e:
            logger.error(f"Error reading memory: {e}")
            return []

    def forget_category(self, category: str):
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM user_memory WHERE category = ?", (category,))
                conn.commit()
        except sqlite3.Error as e:
            logger.error(f"Error forgetting memory: {e}")
