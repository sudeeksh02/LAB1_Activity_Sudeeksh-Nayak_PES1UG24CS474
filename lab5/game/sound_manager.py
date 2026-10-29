import os
import math
import struct
import wave
import pygame

class SoundManager:
    """Procedurally synthesizes and manages sound effects for reflex stimuli and feedback."""

    def __init__(self, assets_dir: str):
        self.sounds_dir = os.path.join(assets_dir, "sounds")
        os.makedirs(self.sounds_dir, exist_ok=True)
        self.sounds = {}
        self.enabled = True

        self._ensure_sound_files()
        self._load_sounds()

    def _generate_wav(self, filename: str, frequencies: list, duration_ms: int, volume: float = 0.5):
        filepath = os.path.join(self.sounds_dir, filename)
        if os.path.exists(filepath):
            return

        sample_rate = 44100
        num_samples = int((duration_ms / 1000.0) * sample_rate)

        with wave.open(filepath, "w") as wav_file:
            wav_file.setnchannels(1)  # Mono
            wav_file.setsampwidth(2)  # 16-bit
            wav_file.setframerate(sample_rate)

            samples = []
            segment_len = num_samples // len(frequencies) if frequencies else num_samples

            for i in range(num_samples):
                seg_idx = min(i // segment_len, len(frequencies) - 1)
                freq = frequencies[seg_idx]
                t = i / sample_rate

                # Envelope: attack & decay to prevent clicking
                attack = min(1.0, i / (0.01 * sample_rate))
                decay = min(1.0, (num_samples - i) / (0.05 * sample_rate))
                env = attack * decay

                val = volume * env * math.sin(2.0 * math.pi * freq * t)
                sample_int = int(max(-32767, min(32767, val * 32767)))
                samples.append(struct.pack("<h", sample_int))

            wav_file.writeframes(b"".join(samples))

    def _ensure_sound_files(self):
        # 1. Go cue: high 880 Hz chime
        self._generate_wav("go_cue.wav", [880], 180, volume=0.6)
        # 2. Click hit: crisp 660 Hz blip
        self._generate_wav("target_hit.wav", [660, 880], 120, volume=0.5)
        # 3. False start / error: 180 Hz buzzer
        self._generate_wav("error_buzzer.wav", [180, 140], 250, volume=0.6)
        # 4. Game over: 4-note ascending triumph chord
        self._generate_wav("victory_fanfare.wav", [440, 554, 659, 880], 400, volume=0.7)

    def _load_sounds(self):
        if not pygame.mixer.get_init():
            try:
                pygame.mixer.init()
            except Exception:
                self.enabled = False
                return

        sound_names = ["go_cue", "target_hit", "error_buzzer", "victory_fanfare"]
        for name in sound_names:
            path = os.path.join(self.sounds_dir, f"{name}.wav")
            if os.path.exists(path):
                try:
                    self.sounds[name] = pygame.mixer.Sound(path)
                except Exception:
                    pass

    def play(self, sound_name: str):
        if not self.enabled:
            return
        snd = self.sounds.get(sound_name)
        if snd:
            try:
                snd.play()
            except Exception:
                pass
