import edge_tts

from utils import get_temp_file_name


def gen(text: str, voice: str) -> str:
    print("Generating file...")
    communicate = edge_tts.Communicate(text, voice)

    filename = get_temp_file_name()
    communicate.save_sync(filename)
    return filename
