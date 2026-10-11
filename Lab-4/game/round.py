import random
import pygame

class Round:
    def __init__(self, min_wait_ms=1000, max_wait_ms=3000):
        self.wait_delay_ms = random.randint(min_wait_ms, max_wait_ms)
        self.state = "waiting"  # "waiting" -> "go" -> "result" / "false_start"
        self.start_time = pygame.time.get_ticks()
        self.go_time = None
        self.reaction_ms = None
        self.is_false_start = False

    def update(self):
        """
        Updates round timer. Returns True on the exact frame the cue changes to 'go'.
        """
        if self.state == "waiting":
            now = pygame.time.get_ticks()
            if now - self.start_time >= self.wait_delay_ms:
                self.state = "go"
                self.go_time = now
                return True  # Signal that 'go' just triggered
        return False

    def register_input(self):
        """
        Handles player input (click or spacebar).
        - If during 'waiting': flags a false start (too soon).
        - If during 'go': measures true reaction time from go_time.
        - If already resolved: ignores redundant input.
        """
        now = pygame.time.get_ticks()
        if self.state == "waiting":
            self.state = "false_start"
            self.is_false_start = True
            self.reaction_ms = None
            return None
        elif self.state == "go":
            self.reaction_ms = max(0, now - self.go_time)
            self.state = "result"
            self.is_false_start = False
            return self.reaction_ms
        return self.reaction_ms
