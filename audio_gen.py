import edge_tts
from datetime import datetime

VOICE = "en-GB-SoniaNeural"

def gen(text: str, voice: str) -> None:
  print("Generating file...")
  communicate = edge_tts.Communicate(text, voice)
  
  timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
  filename = f"tmp/file_{timestamp}.mp3"
  communicate.save_sync(filename)
  return filename
