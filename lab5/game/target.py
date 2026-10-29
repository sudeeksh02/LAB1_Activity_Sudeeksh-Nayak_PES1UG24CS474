import math
import random
import pygame

class SpatialTarget:
    """Dynamic spatial target with shrinking timeout ring for precision reflex testing."""

    def __init__(self, screen_w: int, screen_h: int, radius: int = 42, lifespan_ms: int = 1500):
        padding = 120
        self.x = random.randint(padding, screen_w - padding)
        self.y = random.randint(padding, screen_h - padding)
        self.radius = radius
        self.lifespan_ms = lifespan_ms
        self.spawn_time_ms = pygame.time.get_ticks()
        self.is_hit = False

    def is_expired(self, current_time_ms: int) -> bool:
        return (current_time_ms - self.spawn_time_ms) > self.lifespan_ms

    def check_click(self, mouse_pos: tuple) -> tuple:
        mx, my = mouse_pos
        dist = math.hypot(mx - self.x, my - self.y)
        hit = dist <= self.radius
        if hit:
            self.is_hit = True
        return hit, dist

    def draw(self, surface: pygame.Surface, current_time_ms: int):
        elapsed = current_time_ms - self.spawn_time_ms
        progress = max(0.0, min(1.0, elapsed / self.lifespan_ms))

        # Outer countdown ring (shrinks towards target)
        outer_radius = int(self.radius + (1.0 - progress) * 35)
        ring_color = (255, int(200 * (1 - progress)), 50)
        pygame.draw.circle(surface, ring_color, (self.x, self.y), outer_radius, 3)

        # Bullseye rings
        pygame.draw.circle(surface, (230, 50, 50), (self.x, self.y), self.radius)
        pygame.draw.circle(surface, (255, 255, 255), (self.x, self.y), int(self.radius * 0.65))
        pygame.draw.circle(surface, (230, 50, 50), (self.x, self.y), int(self.radius * 0.35))
        pygame.draw.circle(surface, (255, 255, 0), (self.x, self.y), 4)
