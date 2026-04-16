"""
INTELLI AI - Thread Safety Module
Provides thread-safe state management for shared variables.
"""
import threading
from typing import Any, Optional
from contextlib import contextmanager


class ThreadSafeState:
    """Thread-safe state container with lock protection."""
    
    def __init__(self, initial_value: Any = None):
        self._value = initial_value
        self._lock = threading.Lock()
    
    @property
    def value(self) -> Any:
        """Get the current value (thread-safe)."""
        with self._lock:
            return self._value
    
    @value.setter
    def value(self, new_value: Any) -> None:
        """Set a new value (thread-safe)."""
        with self._lock:
            self._value = new_value
    
    @contextmanager
    def modify(self):
        """Context manager for modifying the value atomically."""
        with self._lock:
            yield self._value
    
    def get_and_set(self, new_value: Any) -> Any:
        """Get current value and set new value atomically."""
        with self._lock:
            old_value = self._value
            self._value = new_value
            return old_value


class ThreadSafeFlag:
    """Thread-safe boolean flag."""
    
    def __init__(self, initial: bool = False):
        self._flag = initial
        self._lock = threading.Lock()
    
    @property
    def is_set(self) -> bool:
        with self._lock:
            return self._flag
    
    def set(self) -> None:
        with self._lock:
            self._flag = True
    
    def clear(self) -> None:
        with self._lock:
            self._flag = False
    
    def toggle(self) -> bool:
        """Toggle and return new state."""
        with self._lock:
            self._flag = not self._flag
            return self._flag


# Global thread-safe states
stop_listening = ThreadSafeFlag(False)
hotword_active = ThreadSafeFlag(True)
is_speaking = ThreadSafeFlag(False)
is_listening = ThreadSafeFlag(False)
