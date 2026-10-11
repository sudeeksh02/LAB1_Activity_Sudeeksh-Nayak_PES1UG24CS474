import os
import wave
import struct
import math
import pygame

class SoundManager:
    """
    Manages sound effects for the reaction time tester.
    Synthesizes and caches clean WAV audio files if not already present.
    """
    def __init__(self, sounds_dir="assets/sounds"):
        self.sounds_dir = sounds_dir
        self.sounds = {}
        self.enabled = True

        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
        except Exception as e:
            print(f"[SoundManager] Warning: Audio mixer failed to initialize: {e}")
            self.enabled = False
            return

        self._ensure_sound_files()
        self._load_sounds()

    def _ensure_sound_files(self):
        os.makedirs(self.sounds_dir, exist_ok=True)
        files = {
            "go.wav": self._generate_go_wav,
            "false_start.wav": self._generate_false_start_wav,
            "game_over.wav": self._generate_game_over_wav,
        }
        for filename, generator in files.items():
            path = os.path.join(self.sounds_dir, filename)
            if not os.path.exists(path) or os.path.getsize(path) < 100:
                try:
                    generator(path)
                except Exception as e:
                    print(f"[SoundManager] Failed generating {filename}: {e}")

    def _generate_go_wav(self, path):
        """Crisp, high-pitched chime (880 Hz) when screen turns green."""
        sample_rate = 44100
        duration = 0.16
        n_samples = int(sample_rate * duration)
        with wave.open(path, 'w') as wav:
            wav.setnchannels(1)
            wav.setsampwidth(2)
            wav.setframerate(sample_rate)
            for i in range(n_samples):
                t = i / sample_rate
                env = math.exp(-14 * t)
                # Pure 880 Hz (A5) chime tone
                sample = env * math.sin(2 * math.pi * 880 * t) * 0.65
                val = int(sample * 32767.0)
                wav.writeframes(struct.pack('<h', max(-32768, min(32767, val))))

    def _generate_false_start_wav(self, path):
        """Low warning buzzer (two-tone 200 Hz / 140 Hz buzz) for early click."""
        sample_rate = 44100
        duration = 0.28
        n_samples = int(sample_rate * duration)
        with wave.open(path, 'w') as wav:
            wav.setnchannels(1)
            wav.setsampwidth(2)
            wav.setframerate(sample_rate)
            for i in range(n_samples):
                t = i / sample_rate
                env = math.exp(-6 * t)
                freq = 200 if t < 0.13 else 140
                # Warm square/sawtooth tone for buzzer feel
                sin_val = math.sin(2 * math.pi * freq * t)
                sample = env * (0.35 if sin_val > 0 else -0.35)
                val = int(sample * 32767.0)
                wav.writeframes(struct.pack('<h', max(-32768, min(32767, val))))

    def _generate_game_over_wav(self, path):
        """Upbeat arpeggio fanfare (C5-E5-G5-C6) for session completion."""
        sample_rate = 44100
        duration = 0.55
        n_samples = int(sample_rate * duration)
        notes = [
            (0.00, 0.12, 523.25),  # C5
            (0.11, 0.23, 659.25),  # E5
            (0.22, 0.34, 783.99),  # G5
            (0.33, 0.55, 1046.50), # C6
        ]
        with wave.open(path, 'w') as wav:
            wav.setnchannels(1)
            wav.setsampwidth(2)
            wav.setframerate(sample_rate)
            for i in range(n_samples):
                t = i / sample_rate
                sample = 0.0
                for start, end, freq in notes:
                    if start <= t < end:
                        nt = t - start
                        env = math.exp(-8 * nt)
                        sample += env * math.sin(2 * math.pi * freq * nt) * 0.45
                val = int(sample * 32767.0)
                wav.writeframes(struct.pack('<h', max(-32768, min(32767, val))))

    def _load_sounds(self):
        sound_names = ["go", "false_start", "game_over"]
        for name in sound_names:
            path = os.path.join(self.sounds_dir, f"{name}.wav")
            if os.path.exists(path):
                try:
                    self.sounds[name] = pygame.mixer.Sound(path)
                except Exception as e:
                    print(f"[SoundManager] Could not load sound {name}: {e}")

    def play(self, sound_name):
        """Play a loaded sound effect by name."""
        if not self.enabled:
            return
        snd = self.sounds.get(sound_name)
        if snd:
            try:
                snd.play()
            except Exception as e:
                print(f"[SoundManager] Error playing {sound_name}: {e}")
