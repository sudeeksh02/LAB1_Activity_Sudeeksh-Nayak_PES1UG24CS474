import pygame
from .round import Round
from .sound_manager import SoundManager

# Color Palette
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (75, 85, 99)
GREEN = (34, 197, 94)
BLUE = (37, 99, 235)
RED = (220, 38, 38)
DARK_BG = (24, 31, 44)
CARD_BG = (35, 45, 63)
CARD_BORDER = (55, 68, 92)
GOLD = (245, 158, 11)
TEXT_MUTED = (156, 163, 175)
BTN_DEFAULT = (51, 65, 85)
BTN_HOVER = (71, 85, 105)
BTN_BORDER = (100, 116, 139)

DIFFICULTIES = {
    "Easy": {"rounds": 3, "min_wait_ms": 1500, "max_wait_ms": 3500, "label": "[1] Easy (3 Rds)"},
    "Medium": {"rounds": 5, "min_wait_ms": 1000, "max_wait_ms": 3000, "label": "[2] Medium (5 Rds)"},
    "Hard": {"rounds": 7, "min_wait_ms": 500, "max_wait_ms": 1800, "label": "[3] Hard (7 Rds)"},
}

class GameEngine:
    def __init__(self, width, height, difficulty="Medium"):
        self.width = width
        self.height = height
        self.sound_manager = SoundManager()
        
        # Load fonts
        self.title_font = pygame.font.SysFont("Arial", 28, bold=True)
        self.big_font = pygame.font.SysFont("Arial", 46, bold=True)
        self.font = pygame.font.SysFont("Arial", 20)
        self.small_font = pygame.font.SysFont("Arial", 16)
        
        self.result_pause_ms = 900  # Pause after click to show result/false start
        self.set_difficulty(difficulty)

    def set_difficulty(self, diff_name):
        """Initializes or resets a session with the given difficulty."""
        if diff_name not in DIFFICULTIES:
            diff_name = "Medium"
        self.current_difficulty = diff_name
        cfg = DIFFICULTIES[diff_name]
        self.rounds_total = cfg["rounds"]
        self.min_wait_ms = cfg["min_wait_ms"]
        self.max_wait_ms = cfg["max_wait_ms"]

        self.round_history = []   # list of {"round": int, "ms": int or None, "type": str}
        self.reaction_times = []  # only valid reaction times in ms
        self.round = Round(self.min_wait_ms, self.max_wait_ms)
        self.result_shown_at = None
        self.game_over = False
        self._game_over_sound_played = False
        self.hovered_btn = None

    def handle_event(self, event):
        if self.game_over:
            self._handle_game_over_event(event)
            return

        is_click = (event.type == pygame.MOUSEBUTTONDOWN and event.button == 1)
        is_space = (event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE)

        if is_click or is_space:
            if self.round.state == "waiting":
                # Task 1: Detect premature reaction (false start)
                self.round.register_input()
                self.sound_manager.play("false_start")
                self.round_history.append({
                    "round": len(self.round_history) + 1,
                    "ms": None,
                    "type": "false_start"
                })
                self.result_shown_at = pygame.time.get_ticks()

            elif self.round.state == "go":
                # Task 1: Genuine reaction measured from green cue
                reaction_ms = self.round.register_input()
                self.reaction_times.append(reaction_ms)
                self.round_history.append({
                    "round": len(self.round_history) + 1,
                    "ms": reaction_ms,
                    "type": "success"
                })
                self.result_shown_at = pygame.time.get_ticks()

    def _handle_game_over_event(self, event):
        # Keyboard shortcuts for replay & difficulty
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_1, pygame.K_e):
                self.set_difficulty("Easy")
            elif event.key in (pygame.K_2, pygame.K_m):
                self.set_difficulty("Medium")
            elif event.key in (pygame.K_3, pygame.K_h):
                self.set_difficulty("Hard")
            elif event.key in (pygame.K_r, pygame.K_SPACE):
                self.set_difficulty(self.current_difficulty)
            elif event.key in (pygame.K_ESCAPE, pygame.K_q):
                pygame.event.post(pygame.event.Event(pygame.QUIT))

        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse_pos = event.pos
            buttons = self._get_replay_buttons()
            for key, rect in buttons.items():
                if rect.collidepoint(mouse_pos):
                    if key in DIFFICULTIES:
                        self.set_difficulty(key)
                    elif key == "Quit":
                        pygame.event.post(pygame.event.Event(pygame.QUIT))

    def handle_input(self):
        # Track mouse position for button hover animations on the game over screen
        if self.game_over:
            mouse_pos = pygame.mouse.get_pos()
            buttons = self._get_replay_buttons()
            self.hovered_btn = None
            for key, rect in buttons.items():
                if rect.collidepoint(mouse_pos):
                    self.hovered_btn = key
                    break

    def update(self):
        if self.game_over:
            return

        # Update current round
        just_went = self.round.update()
        if just_went:
            # Task 4: Play sound cue right when screen turns green
            self.sound_manager.play("go")

        # Check if pause after a round outcome is complete
        if self.round.state in ("result", "false_start"):
            now = pygame.time.get_ticks()
            if self.result_shown_at and (now - self.result_shown_at >= self.result_pause_ms):
                self._start_next_round()

    def _start_next_round(self):
        if len(self.round_history) >= self.rounds_total:
            self.game_over = True
            if not self._game_over_sound_played:
                # Task 4: Play session ending sound
                self.sound_manager.play("game_over")
                self._game_over_sound_played = True
                print("Session complete! Reaction times (ms):", self.reaction_times)
                print("Average:", self.average_reaction_ms(), "ms")
            return
        self.round = Round(self.min_wait_ms, self.max_wait_ms)

    def average_reaction_ms(self):
        if not self.reaction_times:
            return 0
        return round(sum(self.reaction_times) / len(self.reaction_times))

    def best_reaction_ms(self):
        if not self.reaction_times:
            return 0
        return min(self.reaction_times)

    def false_start_count(self):
        return sum(1 for item in self.round_history if item["type"] == "false_start")

    def _get_rating(self, avg_ms):
        if not self.reaction_times:
            return "No valid attempts", TEXT_MUTED
        if avg_ms < 200:
            return "Lightning Reflexes! (Pro)", (52, 211, 153)
        elif avg_ms < 250:
            return "Great Reflexes!", (96, 165, 250)
        elif avg_ms < 320:
            return "Average Human Reflexes", GOLD
        else:
            return "Needs Practice!", (248, 113, 113)

    def _get_replay_buttons(self):
        btn_y = 335
        btn_h = 42
        btn_w = 125
        gap = 15
        start_x = 25
        return {
            "Easy": pygame.Rect(start_x, btn_y, btn_w, btn_h),
            "Medium": pygame.Rect(start_x + btn_w + gap, btn_y, btn_w, btn_h),
            "Hard": pygame.Rect(start_x + (btn_w + gap) * 2, btn_y, btn_w, btn_h),
            "Quit": pygame.Rect(start_x + (btn_w + gap) * 3, btn_y, btn_w, btn_h),
        }

    def render(self, screen):
        if self.game_over:
            self._render_game_over(screen)
            return

        # In-game rendering
        if self.round.state == "waiting":
            bg = GRAY
            main_msg = "Wait for green..."
            sub_msg = "Do NOT click yet!"
        elif self.round.state == "go":
            bg = GREEN
            main_msg = "CLICK NOW!"
            sub_msg = "Press Space or Left Click!"
        elif self.round.state == "false_start":
            bg = RED
            main_msg = "TOO SOON!"
            sub_msg = "False Start! Wait for green."
        else:  # result
            bg = BLUE
            main_msg = f"{self.round.reaction_ms} ms"
            sub_msg = "Reaction recorded!"

        screen.fill(bg)

        # Main center text
        main_surf = self.big_font.render(main_msg, True, WHITE)
        main_rect = main_surf.get_rect(center=(self.width // 2, self.height // 2 - 15))
        screen.blit(main_surf, main_rect)

        # Subtext
        sub_surf = self.font.render(sub_msg, True, WHITE)
        sub_rect = sub_surf.get_rect(center=(self.width // 2, self.height // 2 + 35))
        screen.blit(sub_surf, sub_rect)

        # Header: Round and difficulty info
        current_num = min(len(self.round_history) + 1, self.rounds_total)
        round_text = self.font.render(f"Round {current_num}/{self.rounds_total} ({self.current_difficulty})", True, WHITE)
        screen.blit(round_text, (15, 12))

        # Header: Running average
        avg = self.average_reaction_ms()
        avg_str = f"Avg: {avg} ms" if self.reaction_times else "Avg: -- ms"
        avg_text = self.font.render(avg_str, True, WHITE)
        screen.blit(avg_text, (self.width - avg_text.get_width() - 15, 12))

    def _render_game_over(self, screen):
        # Task 2: Dedicated Results Screen
        screen.fill(DARK_BG)

        # Title
        title_surf = self.title_font.render("SESSION COMPLETE", True, WHITE)
        screen.blit(title_surf, (self.width // 2 - title_surf.get_width() // 2, 18))

        diff_sub = self.small_font.render(
            f"Difficulty: {self.current_difficulty}  •  {self.rounds_total} Rounds",
            True, TEXT_MUTED
        )
        screen.blit(diff_sub, (self.width // 2 - diff_sub.get_width() // 2, 52))

        # Left Card: Round History
        left_card = pygame.Rect(25, 78, 255, 235)
        pygame.draw.rect(screen, CARD_BG, left_card, border_radius=8)
        pygame.draw.rect(screen, CARD_BORDER, left_card, width=1, border_radius=8)

        card_title = self.font.render("Round Breakdown", True, WHITE)
        screen.blit(card_title, (left_card.x + 15, left_card.y + 12))

        y_offset = left_card.y + 44
        line_height = 24 if self.rounds_total <= 5 else 22
        for item in self.round_history:
            r_num = item["round"]
            if item["type"] == "false_start":
                txt = f"Round {r_num}:  False Start"
                color = (248, 113, 113)  # soft red
            else:
                txt = f"Round {r_num}:  {item['ms']} ms"
                color = WHITE
            surf = self.small_font.render(txt, True, color)
            screen.blit(surf, (left_card.x + 15, y_offset))
            y_offset += line_height

        # Right Card: Performance Metrics
        right_card = pygame.Rect(300, 78, 275, 235)
        pygame.draw.rect(screen, CARD_BG, right_card, border_radius=8)
        pygame.draw.rect(screen, CARD_BORDER, right_card, width=1, border_radius=8)

        stats_title = self.font.render("Performance Summary", True, WHITE)
        screen.blit(stats_title, (right_card.x + 15, right_card.y + 12))

        avg = self.average_reaction_ms()
        best = self.best_reaction_ms()
        fs_count = self.false_start_count()
        rating_text, rating_color = self._get_rating(avg)

        stats_y = right_card.y + 45
        stat_lines = [
            ("Average Time:", f"{avg} ms" if self.reaction_times else "N/A", GREEN if avg else TEXT_MUTED),
            ("Best Reaction:", f"{best} ms" if self.reaction_times else "N/A", GOLD if best else TEXT_MUTED),
            ("False Starts:", f"{fs_count}", RED if fs_count > 0 else TEXT_MUTED),
        ]

        for label, val, val_col in stat_lines:
            lbl_surf = self.small_font.render(label, True, TEXT_MUTED)
            screen.blit(lbl_surf, (right_card.x + 15, stats_y))
            val_surf = self.font.render(val, True, val_col)
            screen.blit(val_surf, (right_card.x + 145, stats_y - 2))
            stats_y += 32

        # Reflex Rating Box
        stats_y += 10
        rate_lbl = self.small_font.render("Reflex Rating:", True, TEXT_MUTED)
        screen.blit(rate_lbl, (right_card.x + 15, stats_y))
        rate_surf = self.small_font.render(rating_text, True, rating_color)
        screen.blit(rate_surf, (right_card.x + 15, stats_y + 22))

        # Task 3: Interactive Replay Buttons
        buttons = self._get_replay_buttons()
        btn_labels = {
            "Easy": "[1] Easy",
            "Medium": "[2] Medium",
            "Hard": "[3] Hard",
            "Quit": "[Q] Quit",
        }

        for key, rect in buttons.items():
            is_hovered = (self.hovered_btn == key)
            bg_col = BTN_HOVER if is_hovered else BTN_DEFAULT
            pygame.draw.rect(screen, bg_col, rect, border_radius=6)
            border_col = (147, 197, 253) if is_hovered else BTN_BORDER
            pygame.draw.rect(screen, border_col, rect, width=1, border_radius=6)

            txt = btn_labels[key]
            lbl_surf = self.small_font.render(txt, True, WHITE)
            lbl_rect = lbl_surf.get_rect(center=rect.center)
            screen.blit(lbl_surf, lbl_rect)
