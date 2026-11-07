import numpy as np
import sounddevice as sd
import aubio
import time


class AudioListener:
    def __init__(self, sample_rate=44100, buffer_size=4096, device_index=1):
        self.sample_rate = sample_rate
        self.buffer_size = buffer_size
        self.device_index = device_index

        # Initialize Aubio YIN pitch detector
        self.pitch_detector = aubio.pitch(
            "default", self.buffer_size * 2, self.buffer_size, self.sample_rate
        )
        self.pitch_detector.set_unit("Hz")
        self.pitch_detector.set_silence(-70)

        self.stream = None
        self.latest_note = None
        self.latest_freq = 0.0
        self.latest_confidence = 0.0

    def _hz_to_note_name(self, frequency):
        if frequency <= 0:
            return None
        midi_num = int(round(69 + 12 * np.log2(frequency / 440.0)))
        notes = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
        note_name = notes[midi_num % 12]
        octave = (midi_num // 12) - 1
        return f"{note_name}{octave}"

    def _audio_callback(self, indata, frames, time_info, status):
        if status:
            pass  # Handle or log status warnings if needed

        samples = np.squeeze(indata).astype(np.float32)
        volume = np.sqrt(np.mean(samples**2))

        if volume < 0.01:
            return  # Skip background noise

        pitch = self.pitch_detector(samples)[0]
        confidence = self.pitch_detector.get_confidence()

        if 30 < pitch < 4000:
            self.latest_freq = float(pitch)
            self.latest_confidence = float(confidence)
            self.latest_note = self._hz_to_note_name(pitch)

    def start(self):
        """Starts the background audio stream thread."""
        self.stream = sd.InputStream(
            channels=1,
            samplerate=self.sample_rate,
            blocksize=self.buffer_size,
            device=self.device_index,
            callback=self._audio_callback,
        )
        self.stream.start()
        print("🎧 AudioListener started in background.")

    def get_current_note(self):
        """Poll this from your Pygame main loop to get the latest detected note."""
        note = self.latest_note
        # Optional: clear it after reading so it doesn't stick on screen indefinitely
        # self.latest_note = None
        return note, self.latest_freq, self.latest_confidence

    def stop(self):
        """Stops the audio stream cleanly."""
        if self.stream:
            self.stream.stop()
            self.stream.close()
            print("🛑 AudioListener stopped.")
