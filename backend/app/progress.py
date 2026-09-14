import threading

# Global state
_lock = threading.Lock()
_state = {
    "is_running": False,
    "stage": "Idle",
    "progress": 0,
    "error": None
}

def start_run() -> bool:
    """Starts the run if not already running. Returns True if successfully started, False if already running."""
    with _lock:
        if _state["is_running"]:
            return False
        _state["is_running"] = True
        _state["stage"] = "Starting"
        _state["progress"] = 0
        _state["error"] = None
        return True

def update_progress(stage: str, percent: int):
    """Updates the current stage and progress percentage."""
    with _lock:
        if _state["is_running"]:
            _state["stage"] = stage
            _state["progress"] = max(0, min(100, percent))

def set_error(message: str):
    """Sets the pipeline state to an error state."""
    with _lock:
        _state["is_running"] = False
        _state["stage"] = "Error"
        _state["error"] = message

def complete_run():
    """Marks the pipeline as fully complete."""
    with _lock:
        _state["is_running"] = False
        _state["stage"] = "Complete"
        _state["progress"] = 100
        _state["error"] = None

def get_state() -> dict:
    """Returns a copy of the current state."""
    with _lock:
        return _state.copy()
