from datetime import datetime


def get_temp_file_name() -> str:
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    return f"tmp/file_{timestamp}.mp3"
