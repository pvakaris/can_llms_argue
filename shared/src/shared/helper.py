def format_elapsed_time(elapsed: float) -> str:
    minutes = int(elapsed // 60)
    seconds = int(elapsed % 60)
    milliseconds = int((elapsed - int(elapsed)) * 1000)
    return f"{minutes} min {seconds} sec {milliseconds} ms"
