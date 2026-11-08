import os
import threading
import tkinter as tk
from enum import Enum
from tkinter import scrolledtext

import requests
from just_playback import Playback

import audio_gen
from cleaner import remove_audio_files_from_tmp
from config import *
from utils import get_temp_file_name


class AppStates(Enum):
    IDLE = 0
    FETCHING_TTS = 1


class TextPlayerApp:
    def __init__(self, root: tk.Tk, voice_list: tuple[list[str], list[str]], current_source: AppSource) -> None:
        self.root = root
        self.root.title("Text Reader")
        self.root.geometry("640x540")

        self.voice_list = voice_list
        self.current_source = current_source
        self.selected_voice = tk.StringVar(
            value=self.voice_list[current_source.value][0]
        )
        # Volume state (0.0 to 1.0)
        self.volume = tk.DoubleVar(value=0.5)

        self.prev_text = ""
        self.prev_voice = ""
        self.filename = ""
        self.paused = False

        # Create widgets
        self.create_widgets()
        self.player = Playback()

        self.app_state = AppStates.IDLE

    def create_widgets(self) -> None:
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
            control_frame,
            text="▶ Play",
            command=self.play,
            width=8,
            bg="#4CAF50",
            fg="white",
        )
        self.btn_play.pack(side=tk.LEFT, padx=2)

        # Pause button
        self.btn_pause = tk.Button(
            control_frame,
            text="⏸ Pause",
            command=self.pause,
            width=8,
            bg="#FF9800",
            fg="white",
        )
        self.btn_pause.pack(side=tk.LEFT, padx=2)

        # Stop button
        self.btn_stop = tk.Button(
            control_frame,
            text="⏹ Stop",
            command=self.stop,
            width=8,
            bg="#f44336",
            fg="white",
        )
        self.btn_stop.pack(side=tk.LEFT, padx=2)

        # Volume slider
        vol_label = tk.Label(control_frame, text=" Vol:")
        vol_label.pack(side=tk.LEFT, padx=(20, 0))

        self.vol_scale = tk.Scale(
            control_frame,
            from_=0.0,
            to=1.0,
            resolution=0.05,
            orient=tk.HORIZONTAL,
            variable=self.volume,
            length=150,
            command=self.on_volume_change,
        )
        self.vol_scale.pack(side=tk.LEFT, padx=5)

        # Voices dropdown
        voice_label = tk.Label(control_frame, text=" Voice:")
        voice_label.pack(side=tk.LEFT, padx=(10, 0))

        self.voice_menu = tk.OptionMenu(
            control_frame,
            self.selected_voice,
            *self.voice_list[self.current_source.value],
            command=self.on_voice_change,
        )
        self.voice_menu.config(width=10)
        self.voice_menu.pack(side=tk.LEFT, padx=5)

        # Status bar
        self.status = tk.Label(
            self.root, text="Ready", bd=1, relief=tk.SUNKEN, anchor=tk.W
        )
        self.status.pack(fill=tk.X, padx=10, pady=(0, 5))

        # ------------------ Placeholder actions ------------------

    def play(self) -> None:
        if self.player.paused:
            self.player.resume()
            return

        if self.app_state == AppStates.FETCHING_TTS:
            print("Already fetching data")
            return

        text = self.text_area.get("1.0", tk.END).strip()
        if text:
            print(f"PLAY: {text[:50]}…")
            if (
                self.prev_text != text
                or self.filename == ""
                or self.prev_voice != self.selected_voice.get()
            ):
                self.start_generation(text)
            else:
                self._on_generation_complete(text, self.filename, None)
        else:
            self.status.config(text="No text to read")

    def start_generation(self, text: str) -> None:
        self.btn_play.config(state="disabled")
        self.status.config(text="Generating audio")
        self.app_state = AppStates.FETCHING_TTS
        thread = threading.Thread(
            target=self._generate_audio_thread,
            args=(text, self.selected_voice.get()),
            daemon=True,
        )
        thread.start()

    def _generate_audio_thread(self, text: str, voice: str) -> None:
        """Runs in background with the passed arguments"""
        if self.current_source == AppSource.Local:
            form_data = {"text": (None, text)}
            form_data["voice_url"] = (None, voice)
            try:
                response = requests.post(LOCAL_TTS_URL, files=form_data, timeout=45)
                if response.status_code == 200:
                    content_type = response.headers.get("Content-Type", "")
                    if "audio" in content_type or "octet-stream" in content_type:
                        filename = get_temp_file_name()
                        with open(filename, "wb") as file:
                            file.write(response.content)
                        self.root.after(
                            0, self._on_generation_complete, text, filename, None
                        )
                        return
                raise Exception(f"{response.status_code}: {response.text}")
            except Exception as e:
                self.root.after(0, self._on_generation_complete, "", "", e)
        else:
            try:
                result = audio_gen.gen(text, voice)
                self.root.after(0, self._on_generation_complete, text, result, None)
            except Exception as e:
                self.root.after(0, self._on_generation_complete, "", "", e)

    def _on_generation_complete(
        self, text: str, result: str, error: Exception | None
    ) -> None:
        self.btn_play.config(state="normal")
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

        self.app_state = AppStates.FETCHING_TTS

    def pause(self) -> None:
        """Pause the current reading. Replace with TTS pause logic."""
        self.status.config(text="Paused")
        print("PAUSE")
        self.player.pause()

    def stop(self) -> None:
        """Stop reading completely. Replace with TTS stop logic."""
        self.status.config(text="Stopped")
        print("STOP")
        self.player.stop()

    def on_volume_change(self, val: str) -> None:
        """Called when the volume slider moves. val is a string."""
        vol = float(val)
        self.status.config(text=f"Volume: {vol:.2f}")
        # TODO: Adjust TTS volume if possible
        print(f"Volume changed to {vol:.2f}")

    def on_voice_change(self, choice: str | tk.StringVar) -> None:
        """Called when a new voice is selected from the dropdown."""
        self.status.config(text=f"Voice selected: {choice}")
        # TODO: Switch TTS voice
        print(f"Voice changed to {choice}")


# ------------------ Main ------------------
if __name__ == "__main__":
    remove_audio_files_from_tmp()
    os.makedirs("tmp", exist_ok=True)

    root = tk.Tk()
    app = TextPlayerApp(root, VOICES, CURRENT_SOURCE)
    root.mainloop()
