from typing import Callable


def ask_voice_permission(
    action_name: str,
    speak: Callable[[str], None],
    takecommand: Callable[[], str],
) -> bool:
    speak(f"Permission check: Do you allow me to {action_name}? Say yes or no.")
    answer = (takecommand() or "").strip().lower()
    return answer in {"yes", "y", "allow", "okay", "ok"}

