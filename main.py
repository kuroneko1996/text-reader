import os
import tkinter as tk
import threading
import audio_gen

from tkinter import scrolledtext
from just_playback import Playback
from cleaner import remove_mp3_files_from_tmp

app_state = {
  "fetching_tts" : False
}

class TextPlayerApp:
  def __init__(self, root):
    self.root = root
    self.root.title("Text Reader")
    self.root.geometry("640x540")

    self.voice_list = ["en-GB-SoniaNeural", "en-US-ChristopherNeural", "en-AU-NatashaNeural", "ru-RU-DmitryNeural", "ru-RU-SvetlanaNeural"]
    self.selected_voice = tk.StringVar(value="en-GB-SoniaNeural")
    # Volume state (0.0 to 1.0)
    self.volume = tk.DoubleVar(value=0.5)

    self.prev_text = ""
    self.prev_voice = ""
    self.filename = ""
    self.paused = False

    # Create widgets
    self.create_widgets()
    self.player = Playback()

  def create_widgets(self):
    # Text input area
    self.text_area = scrolledtext.ScrolledText(
      self.root, wrap=tk.WORD, font=("Arial", 12)
    )
    self.text_area.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
    self.text_area.insert(tk.END, "Type or paste text here…")

    # Control frame
    control_frame = tk.Frame(self.root)
    control_frame.pack(fill=tk.X, padx=10, pady=5)

    # Play button
    self.btn_play = tk.Button(
      control_frame, text="▶ Play", command=self.play,
      width=8, bg="#4CAF50", fg="white"
    )
    self.btn_play.pack(side=tk.LEFT, padx=2)

    # Pause button
    self.btn_pause = tk.Button(
      control_frame, text="⏸ Pause", command=self.pause,
      width=8, bg="#FF9800", fg="white"
    )
    self.btn_pause.pack(side=tk.LEFT, padx=2)

    # Stop button
    self.btn_stop = tk.Button(
      control_frame, text="⏹ Stop", command=self.stop,
      width=8, bg="#f44336", fg="white"
    )
    self.btn_stop.pack(side=tk.LEFT, padx=2)

    # Volume slider
    vol_label = tk.Label(control_frame, text=" Vol:")
    vol_label.pack(side=tk.LEFT, padx=(20, 0))

    self.vol_scale = tk.Scale(
      control_frame, from_=0.0, to=1.0, resolution=0.05,
      orient=tk.HORIZONTAL, variable=self.volume,
      length=150, command=self.on_volume_change
    )
    self.vol_scale.pack(side=tk.LEFT, padx=5)

    # Voices dropdown
    voice_label = tk.Label(control_frame, text=" Voice:")
    voice_label.pack(side=tk.LEFT, padx=(10, 0))

    self.voice_menu = tk.OptionMenu(
      control_frame, self.selected_voice, *self.voice_list,
      command=self.on_voice_change
    )
    self.voice_menu.config(width=10)
    self.voice_menu.pack(side=tk.LEFT, padx=5)


    # Status bar
    self.status = tk.Label(
      self.root, text="Ready", bd=1, relief=tk.SUNKEN, anchor=tk.W
    )
    self.status.pack(fill=tk.X, padx=10, pady=(0, 5))

    # ------------------ Placeholder actions ------------------
  def play(self):
    if self.player.paused:
      self.player.resume()
      return

    if app_state["fetching_tts"]:
      print("Already fetching data")
      return

    text = self.text_area.get("1.0", tk.END).strip()
    if text:
      print(f"PLAY: {text[:50]}…")
      if self.prev_text != text or self.filename == "" or self.prev_voice != self.selected_voice.get():
        self.start_generation(text)
      else:
        self._on_generation_complete(text, self.filename, None)
    else:
      self.status.config(text="No text to read")

  def start_generation(self, text):
    self.btn_play.config(state="disabled")
    self.status.config(text="Generating audio")
    app_state["fetching_tts"] = True
    thread = threading.Thread(
      target=self._generate_audio_thread,
      args=(text, self.selected_voice.get()),
      daemon=True
    )
    thread.start()

  def _generate_audio_thread(self, text, voice):
    """Runs in background with the passed arguments"""
    try:
      result = audio_gen.gen(text, voice)
      self.root.after(0, self._on_generation_complete, text, result, None)
    except Exception as e:
      self.root.after(0, self._on_generation_complete, None, e)


  def _on_generation_complete(self, text, result, error):
    self.btn_play.config(state='normal')
    if error:
        self.status.config(text=f"Error: {error}")
    else:
        self.filename = result
        self.status.config(text=f"Playing (volume={self.volume.get():.2f})")
        self.prev_text = text
        self.prev_voice = self.selected_voice.get()
        self.player.load_file(self.filename)
        self.player.play()
        self.player.set_volume(self.volume.get())

    app_state["fetching_tts"] = False

  def pause(self):
    """Pause the current reading. Replace with TTS pause logic."""
    self.status.config(text="Paused")
    print("PAUSE")
    self.player.pause()

  def stop(self):
    """Stop reading completely. Replace with TTS stop logic."""
    self.status.config(text="Stopped")
    print("STOP")
    self.player.stop()

  def on_volume_change(self, val):
    """Called when the volume slider moves. val is a string."""
    vol = float(val)
    self.status.config(text=f"Volume: {vol:.2f}")
    # TODO: Adjust TTS volume if possible
    print(f"Volume changed to {vol:.2f}")

  def on_voice_change(self, choice):
    """Called when a new voice is selected from the dropdown."""
    self.status.config(text=f"Voice selected: {choice}")
    # TODO: Switch TTS voice
    print(f"Voice changed to {choice}")

# ------------------ Main ------------------
if __name__ == "__main__":
  remove_mp3_files_from_tmp()
  os.makedirs('tmp', exist_ok=True)

  root = tk.Tk()
  app = TextPlayerApp(root)
  root.mainloop()
