#!/usr/bin/env python3
"""
Software Engineering Lab 5: Multi-Modal Cognitive Reflex and Reaction Test Suite
Student: Sudeeksh Nayak (SRN: PES1UG24CS474)
Institution: PES University - Dept. of CSE
"""

import os
import sys
import pygame
from game.game_engine import GameEngine

def main():
    pygame.init()
    pygame.font.init()

    # Window settings
    width, height = 880, 640
    screen = pygame.display.set_mode((width, height))
    pygame.display.set_caption("Cognitive Reflex & Reaction Test Suite — PES1UG24CS474")

    # Locate assets
    current_dir = os.path.dirname(os.path.abspath(__file__))
    assets_dir = os.path.join(current_dir, "assets")

    engine = GameEngine(screen, assets_dir)
    clock = pygame.time.Clock()

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            else:
                engine.handle_event(event)

        engine.update()
        engine.render()
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit(0)

if __name__ == "__main__":
    main()
