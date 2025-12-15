import os

def format_elapsed_time(elapsed: float) -> str:
    minutes = int(elapsed // 60)
    seconds = int(elapsed % 60)
    milliseconds = int((elapsed - int(elapsed)) * 1000)
    return f"{minutes} min {seconds} sec {milliseconds} ms"

def env_bool(name: str, default: bool) -> bool:
    return os.getenv(name, str(default)).lower() in ("1", "true", "yes", "on")
