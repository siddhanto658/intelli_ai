from typing import Callable, List, Optional, Tuple


Handler = Callable[[str], bool]


class IntentRouter:
    """Lightweight keyword router for Phase 1 migration."""

    def __init__(self):
        self._routes: List[Tuple[List[str], Handler]] = []

    def register(self, keywords: List[str], handler: Handler) -> None:
        self._routes.append((keywords, handler))

    def dispatch(self, query: str) -> bool:
        normalized = (query or "").lower()
        for keywords, handler in self._routes:
            if any(keyword in normalized for keyword in keywords):
                return bool(handler(query))
        return False

