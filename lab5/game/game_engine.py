import random
import pygame
from typing import List
from .round import RoundResult
from .target import SpatialTarget
from .analytics import ReflexAnalytics
from .sound_manager import SoundManager

class GameEngine:
    """State-machine driven reflex testing engine supporting multi-modal reaction paradigms."""

    # States
    STATE_MENU = "MENU"
    STATE_WAITING = "WAITING"
    STATE_STIMULUS = "STIMULUS"
    STATE_FEEDBACK = "FEEDBACK"
    STATE_GAME_OVER = "GAME_OVER"

    # Modes
    MODE_VISUAL = "Visual Reflex"
    MODE_SPATIAL_AIM = "Spatial Aim & Precision"
    MODE_STROOP_GONOGO = "Incongruent Go/No-Go"

    # Color Palette (Flat Modern Dark Theme)
    COLOR_BG = (24, 28, 36)
    COLOR_PANEL = (35, 42, 54)
    COLOR_WAITING = (70, 78, 92)
    COLOR_GO = (46, 204, 113)
    COLOR_NOGO = (231, 76, 60)
    COLOR_WARN = (241, 196, 15)
    COLOR_TEXT = (245, 247, 250)
    COLOR_MUTED = (160, 174, 192)
    COLOR_ACCENT = (52, 152, 219)

    def __init__(self, screen: pygame.Surface, assets_dir: str):
        self.screen = screen
        self.width, self.height = screen.get_size()
        self.sound_mgr = SoundManager(assets_dir)

        # Fonts
        self.font_title = pygame.font.SysFont("Segoe UI", 36, bold=True)
        self.font_large = pygame.font.SysFont("Segoe UI", 28, bold=True)
        self.font_medium = pygame.font.SysFont("Segoe UI", 20, bold=True)
        self.font_body = pygame.font.SysFont("Segoe UI", 16)
        self.font_small = pygame.font.SysFont("Segoe UI", 13)

        # Configuration
        self.active_mode = self.MODE_VISUAL
        self.difficulty = "Medium"
        self.max_trials = 5
        self.min_delay_ms = 1200
        self.max_delay_ms = 2800

        # State Variables
        self.state = self.STATE_MENU
        self.current_trial = 0
        self.rounds: List[RoundResult] = []
        self.stats = {}

        # Timing
        self.wait_start_ms = 0
        self.target_stimulus_ms = 0
        self.actual_stimulus_ms = 0
        self.feedback_msg = ""
        self.feedback_color = self.COLOR_TEXT

        # Mode Specifics
        self.active_target: SpatialTarget = None
        self.is_current_trial_go = True  # For Go/No-Go

    def set_difficulty(self, diff: str):
        self.difficulty = diff
        if diff == "Easy":
            self.max_trials = 3
            self.min_delay_ms = 1800
            self.max_delay_ms = 3500
        elif diff == "Medium":
            self.max_trials = 5
            self.min_delay_ms = 1200
            self.max_delay_ms = 2800
        elif diff == "Hard":
            self.max_trials = 7
            self.min_delay_ms = 600
            self.max_delay_ms = 1800

    def start_session(self, mode: str):
        self.active_mode = mode
        self.current_trial = 0
        self.rounds = []
        self.stats = {}
        self._next_trial()

    def _next_trial(self):
        if self.current_trial >= self.max_trials:
            self.state = self.STATE_GAME_OVER
            self.stats = ReflexAnalytics.compute_session_stats(self.rounds)
            self.sound_mgr.play("victory_fanfare")
            return

        self.current_trial += 1
        self.state = self.STATE_WAITING
        self.wait_start_ms = pygame.time.get_ticks()
        delay = random.randint(self.min_delay_ms, self.max_delay_ms)
        self.target_stimulus_ms = self.wait_start_ms + delay

        # Setup trial parameters
        if self.active_mode == self.MODE_STROOP_GONOGO:
            # 70% chance of GO, 30% chance of NO-GO
            self.is_current_trial_go = random.random() < 0.70
        else:
            self.is_current_trial_go = True

        self.active_target = None

    def handle_event(self, event: pygame.event.Event):
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_q, pygame.K_ESCAPE):
                if self.state == self.STATE_MENU:
                    pygame.quit()
                    exit(0)
                else:
                    self.state = self.STATE_MENU
                    return

            if self.state == self.STATE_MENU:
                if event.key in (pygame.K_1, pygame.K_v):
                    self.start_session(self.MODE_VISUAL)
                elif event.key in (pygame.K_2, pygame.K_a):
                    self.start_session(self.MODE_SPATIAL_AIM)
                elif event.key in (pygame.K_3, pygame.K_g):
                    self.start_session(self.MODE_STROOP_GONOGO)
                elif event.key == pygame.K_e:
                    self.set_difficulty("Easy")
                elif event.key == pygame.K_m:
                    self.set_difficulty("Medium")
                elif event.key == pygame.K_h:
                    self.set_difficulty("Hard")

            elif self.state == self.STATE_GAME_OVER:
                if event.key in (pygame.K_r, pygame.K_SPACE):
                    self.start_session(self.active_mode)
                elif event.key in (pygame.K_m, pygame.K_BACKSPACE):
                    self.state = self.STATE_MENU

            elif self.state in (self.STATE_WAITING, self.STATE_STIMULUS):
                if event.key == pygame.K_SPACE:
                    self._process_interaction(pygame.mouse.get_pos())

            elif self.state == self.STATE_FEEDBACK:
                if event.key == pygame.K_SPACE:
                    self._next_trial()

        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mpos = event.pos
            if self.state == self.STATE_MENU:
                self._handle_menu_clicks(mpos)
            elif self.state == self.STATE_GAME_OVER:
                self._handle_game_over_clicks(mpos)
            elif self.state in (self.STATE_WAITING, self.STATE_STIMULUS):
                self._process_interaction(mpos)
            elif self.state == self.STATE_FEEDBACK:
                self._next_trial()

    def _process_interaction(self, mpos: tuple):
        now = pygame.time.get_ticks()

        # 1. Clicked during WAITING -> False Start!
        if self.state == self.STATE_WAITING:
            self.sound_mgr.play("error_buzzer")
            self.state = self.STATE_FEEDBACK
            self.feedback_msg = "TOO SOON! (False Start)"
            self.feedback_color = self.COLOR_NOGO

            round_data = RoundResult(
                round_number=self.current_trial,
                mode_name=self.active_mode,
                stimulus_time_ms=self.target_stimulus_ms,
                response_time_ms=now,
                is_false_start=True,
                is_correct_go=self.is_current_trial_go
            )
            self.rounds.append(round_data)
            return

        # 2. Clicked during STIMULUS
        if self.state == self.STATE_STIMULUS:
            if self.active_mode == self.MODE_VISUAL:
                latency = now - self.actual_stimulus_ms
                self.sound_mgr.play("target_hit")
                self.state = self.STATE_FEEDBACK
                self.feedback_msg = f"{latency} ms"
                self.feedback_color = self.COLOR_GO

                self.rounds.append(RoundResult(
                    round_number=self.current_trial,
                    mode_name=self.active_mode,
                    stimulus_time_ms=self.actual_stimulus_ms,
                    response_time_ms=now
                ))

            elif self.active_mode == self.MODE_SPATIAL_AIM:
                if self.active_target:
                    hit, dist = self.active_target.check_click(mpos)
                    latency = now - self.actual_stimulus_ms
                    if hit:
                        self.sound_mgr.play("target_hit")
                        self.state = self.STATE_FEEDBACK
                        self.feedback_msg = f"HIT! {latency} ms (Distance: {int(dist)}px)"
                        self.feedback_color = self.COLOR_GO
                    else:
                        self.sound_mgr.play("error_buzzer")
                        self.state = self.STATE_FEEDBACK
                        self.feedback_msg = f"MISSED TARGET! (Offset: {int(dist)}px)"
                        self.feedback_color = self.COLOR_WARN

                    self.rounds.append(RoundResult(
                        round_number=self.current_trial,
                        mode_name=self.active_mode,
                        stimulus_time_ms=self.actual_stimulus_ms,
                        response_time_ms=now,
                        target_pos=(self.active_target.x, self.active_target.y),
                        click_pos=mpos,
                        distance_error_px=dist
                    ))

            elif self.active_mode == self.MODE_STROOP_GONOGO:
                latency = now - self.actual_stimulus_ms
                if self.is_current_trial_go:
                    # Correct GO click
                    self.sound_mgr.play("target_hit")
                    self.state = self.STATE_FEEDBACK
                    self.feedback_msg = f"VALID GO! {latency} ms"
                    self.feedback_color = self.COLOR_GO
                    self.rounds.append(RoundResult(
                        round_number=self.current_trial,
                        mode_name=self.active_mode,
                        stimulus_time_ms=self.actual_stimulus_ms,
                        response_time_ms=now,
                        is_correct_go=True
                    ))
                else:
                    # Inappropriate click on NO-GO! (Commission error)
                    self.sound_mgr.play("error_buzzer")
                    self.state = self.STATE_FEEDBACK
                    self.feedback_msg = "FAILED INHIBITION! (Clicked on RED)"
                    self.feedback_color = self.COLOR_NOGO
                    self.rounds.append(RoundResult(
                        round_number=self.current_trial,
                        mode_name=self.active_mode,
                        stimulus_time_ms=self.actual_stimulus_ms,
                        response_time_ms=now,
                        is_false_start=True,
                        is_correct_go=False
                    ))

    def update(self):
        now = pygame.time.get_ticks()

        # Check for stimulus transition
        if self.state == self.STATE_WAITING:
            if now >= self.target_stimulus_ms:
                self.state = self.STATE_STIMULUS
                self.actual_stimulus_ms = now

                if self.active_mode == self.MODE_VISUAL:
                    self.sound_mgr.play("go_cue")
                elif self.active_mode == self.MODE_SPATIAL_AIM:
                    self.active_target = SpatialTarget(self.width, self.height)
                    self.sound_mgr.play("go_cue")
                elif self.active_mode == self.MODE_STROOP_GONOGO:
                    if self.is_current_trial_go:
                        self.sound_mgr.play("go_cue")
                    else:
                        self.sound_mgr.play("error_buzzer")

        # Check for target expiration in Spatial Aim
        elif self.state == self.STATE_STIMULUS:
            if self.active_mode == self.MODE_SPATIAL_AIM and self.active_target:
                if self.active_target.is_expired(now):
                    self.sound_mgr.play("error_buzzer")
                    self.state = self.STATE_FEEDBACK
                    self.feedback_msg = "TIMEOUT! Target Expired."
                    self.feedback_color = self.COLOR_WARN
                    self.rounds.append(RoundResult(
                        round_number=self.current_trial,
                        mode_name=self.active_mode,
                        stimulus_time_ms=self.actual_stimulus_ms,
                        response_time_ms=now,
                        is_timeout=True
                    ))

            elif self.active_mode == self.MODE_STROOP_GONOGO and not self.is_current_trial_go:
                # In NO-GO mode, holding back for 1200ms is a SUCCESS!
                if (now - self.actual_stimulus_ms) > 1200:
                    self.sound_mgr.play("target_hit")
                    self.state = self.STATE_FEEDBACK
                    self.feedback_msg = "SUCCESSFUL INHIBITION! (Held back on RED)"
                    self.feedback_color = self.COLOR_GO
                    self.rounds.append(RoundResult(
                        round_number=self.current_trial,
                        mode_name=self.active_mode,
                        stimulus_time_ms=self.actual_stimulus_ms,
                        response_time_ms=now,
                        is_correct_go=False
                    ))

    def render(self):
        if self.state == self.STATE_MENU:
            self._render_menu()
        elif self.state == self.STATE_WAITING:
            self._render_waiting()
        elif self.state == self.STATE_STIMULUS:
            self._render_stimulus()
        elif self.state == self.STATE_FEEDBACK:
            self._render_feedback()
        elif self.state == self.STATE_GAME_OVER:
            self._render_game_over()

    def _render_menu(self):
        self.screen.fill(self.COLOR_BG)

        # Header Title
        title_surf = self.font_title.render("Cognitive Reflex & Reaction Test Suite", True, self.COLOR_TEXT)
        self.screen.blit(title_surf, (self.width//2 - title_surf.get_width()//2, 50))

        sub_surf = self.font_body.render("Software Engineering Lab 5 — PES University (Dept. of CSE)", True, self.COLOR_MUTED)
        self.screen.blit(sub_surf, (self.width//2 - sub_surf.get_width()//2, 100))

        # Mode Selection Cards
        modes = [
            ("[1] Visual Reflex Mode", "Classic full-screen stimulus color reaction testing with false start detection.", pygame.Rect(self.width//2 - 320, 160, 640, 80), self.active_mode == self.MODE_VISUAL),
            ("[2] Spatial Aim & Precision", "Dynamic circular targets appearing at random coordinates. Measures aim speed and accuracy.", pygame.Rect(self.width//2 - 320, 260, 640, 80), self.active_mode == self.MODE_SPATIAL_AIM),
            ("[3] Incongruent Go/No-Go", "Cognitive inhibition test. Click ONLY when screen is Green; hold back when Red!", pygame.Rect(self.width//2 - 320, 360, 640, 80), self.active_mode == self.MODE_STROOP_GONOGO),
        ]

        mpos = pygame.mouse.get_pos()
        for title, desc, rect, is_sel in modes:
            hover = rect.collidepoint(mpos)
            bg = (45, 55, 72) if hover else (self.COLOR_PANEL if not is_sel else (38, 70, 95))
            border = self.COLOR_ACCENT if is_sel or hover else (60, 72, 90)
            pygame.draw.rect(self.screen, bg, rect, border_radius=8)
            pygame.draw.rect(self.screen, border, rect, width=2, border_radius=8)

            t_s = self.font_medium.render(title, True, self.COLOR_TEXT)
            d_s = self.font_small.render(desc, True, self.COLOR_MUTED)
            self.screen.blit(t_s, (rect.x + 20, rect.y + 16))
            self.screen.blit(d_s, (rect.x + 20, rect.y + 46))

        # Difficulty Bar
        diff_label = self.font_body.render(f"Difficulty Level: {self.difficulty} ({self.max_trials} Trials)", True, self.COLOR_TEXT)
        self.screen.blit(diff_label, (self.width//2 - diff_label.get_width()//2, 470))

        diffs = [("Easy (3)", "Easy"), ("Medium (5)", "Medium"), ("Hard (7)", "Hard")]
        for i, (txt, val) in enumerate(diffs):
            rect = pygame.Rect(self.width//2 - 180 + i * 125, 505, 110, 36)
            is_active = self.difficulty == val
            bg = self.COLOR_ACCENT if is_active else (40, 48, 62)
            pygame.draw.rect(self.screen, bg, rect, border_radius=6)
            s = self.font_body.render(txt, True, self.COLOR_TEXT)
            self.screen.blit(s, (rect.x + rect.w//2 - s.get_width()//2, rect.y + 7))

        # Start prompt
        start_txt = self.font_body.render("Click any Mode card above or press [1 / 2 / 3] to begin test", True, self.COLOR_GO)
        self.screen.blit(start_txt, (self.width//2 - start_txt.get_width()//2, 570))

    def _render_waiting(self):
        self.screen.fill(self.COLOR_WAITING)
        s1 = self.font_title.render("WAIT FOR SIGNAL...", True, self.COLOR_TEXT)
        s2 = self.font_body.render(f"Trial {self.current_trial} of {self.max_trials}  |  Do NOT click early!", True, (220, 225, 230))
        self.screen.blit(s1, (self.width//2 - s1.get_width()//2, self.height//2 - 40))
        self.screen.blit(s2, (self.width//2 - s2.get_width()//2, self.height//2 + 25))

    def _render_stimulus(self):
        if self.active_mode == self.MODE_VISUAL:
            self.screen.fill(self.COLOR_GO)
            s = self.font_title.render("CLICK NOW!", True, (20, 20, 20))
            self.screen.blit(s, (self.width//2 - s.get_width()//2, self.height//2 - 25))

        elif self.active_mode == self.MODE_SPATIAL_AIM:
            self.screen.fill(self.COLOR_BG)
            if self.active_target:
                self.active_target.draw(self.screen, pygame.time.get_ticks())
            hud = self.font_small.render(f"Trial {self.current_trial}/{self.max_trials} — CLICK THE BULLSEYE!", True, self.COLOR_MUTED)
            self.screen.blit(hud, (20, 20))

        elif self.active_mode == self.MODE_STROOP_GONOGO:
            if self.is_current_trial_go:
                self.screen.fill(self.COLOR_GO)
                s = self.font_title.render("GO! CLICK!", True, (20, 20, 20))
                self.screen.blit(s, (self.width//2 - s.get_width()//2, self.height//2 - 25))
            else:
                self.screen.fill(self.COLOR_NOGO)
                s = self.font_title.render("NO-GO! DO NOT CLICK!", True, (255, 255, 255))
                self.screen.blit(s, (self.width//2 - s.get_width()//2, self.height//2 - 25))

    def _render_feedback(self):
        self.screen.fill(self.COLOR_BG)
        box_rect = pygame.Rect(self.width//2 - 280, self.height//2 - 120, 560, 240)
        pygame.draw.rect(self.screen, self.COLOR_PANEL, box_rect, border_radius=12)
        pygame.draw.rect(self.screen, self.feedback_color, box_rect, width=3, border_radius=12)

        s1 = self.font_title.render(self.feedback_msg, True, self.feedback_color)
        s2 = self.font_body.render(f"Trial {self.current_trial} of {self.max_trials} Completed", True, self.COLOR_TEXT)
        s3 = self.font_small.render("Click or press [Space] to proceed to next trial...", True, self.COLOR_MUTED)

        self.screen.blit(s1, (self.width//2 - s1.get_width()//2, self.height//2 - 60))
        self.screen.blit(s2, (self.width//2 - s2.get_width()//2, self.height//2 + 10))
        self.screen.blit(s3, (self.width//2 - s3.get_width()//2, self.height//2 + 55))

    def _render_game_over(self):
        self.screen.fill(self.COLOR_BG)

        # Header
        h_s = self.font_title.render("Reflex Assessment Summary", True, self.COLOR_TEXT)
        self.screen.blit(h_s, (self.width//2 - h_s.get_width()//2, 35))

        # Stats Cards Grid
        metrics = [
            ("Average Latency", f"{self.stats.get('average_ms', 0)} ms", self.COLOR_GO),
            ("Fastest Reaction", f"{self.stats.get('best_ms', 0)} ms", self.COLOR_ACCENT),
            ("Consistency Index", f"{self.stats.get('consistency_score', 0)}%", self.COLOR_TEXT),
            ("Std Deviation", f"{self.stats.get('std_dev_ms', 0)} ms", self.COLOR_MUTED),
            ("False Starts", f"{self.stats.get('false_starts', 0)}", self.COLOR_NOGO if self.stats.get('false_starts', 0) > 0 else self.COLOR_GO),
            ("Rating Assessment", f"{self.stats.get('rating', '')}", self.COLOR_WARN)
        ]

        card_w, card_h = 240, 75
        for i, (lbl, val, col) in enumerate(metrics):
            col_idx = i % 3
            row_idx = i // 3
            x = self.width//2 - 380 + col_idx * 260
            y = 100 + row_idx * 90
            rect = pygame.Rect(x, y, card_w, card_h)
            pygame.draw.rect(self.screen, self.COLOR_PANEL, rect, border_radius=8)
            pygame.draw.rect(self.screen, (55, 65, 80), rect, width=1, border_radius=8)

            l_s = self.font_small.render(lbl, True, self.COLOR_MUTED)
            v_s = self.font_medium.render(val, True, col)
            self.screen.blit(l_s, (rect.x + 12, rect.y + 12))
            self.screen.blit(v_s, (rect.x + 12, rect.y + 36))

        # Trials Table
        tbl_rect = pygame.Rect(self.width//2 - 380, 290, 760, 210)
        pygame.draw.rect(self.screen, self.COLOR_PANEL, tbl_rect, border_radius=8)
        pygame.draw.rect(self.screen, (55, 65, 80), tbl_rect, width=1, border_radius=8)

        th = self.font_body.render("Trial Breakdown Log", True, self.COLOR_TEXT)
        self.screen.blit(th, (tbl_rect.x + 20, tbl_rect.y + 15))

        y_offset = tbl_rect.y + 50
        for r in self.rounds:
            if r.is_false_start:
                res_txt = "FALSE START (Premature Input)"
                c = self.COLOR_NOGO
            elif r.is_timeout:
                res_txt = "TIMEOUT (Target Expired)"
                c = self.COLOR_WARN
            elif not r.is_correct_go:
                res_txt = "NO-GO ERROR (Clicked Red Distractor)"
                c = self.COLOR_NOGO
            else:
                dist_info = f" | Dist: {int(r.distance_error_px)}px" if r.distance_error_px > 0 else ""
                res_txt = f"{r.latency_ms} ms{dist_info}"
                c = self.COLOR_GO

            row_s = self.font_small.render(f"Trial {r.round_number} [{r.mode_name}]:", True, self.COLOR_MUTED)
            val_s = self.font_small.render(res_txt, True, c)
            self.screen.blit(row_s, (tbl_rect.x + 25, y_offset))
            self.screen.blit(val_s, (tbl_rect.x + 260, y_offset))
            y_offset += 22

        # Buttons
        r_rect = pygame.Rect(self.width//2 - 200, 525, 180, 42)
        m_rect = pygame.Rect(self.width//2 + 20, 525, 180, 42)
        pygame.draw.rect(self.screen, self.COLOR_GO, r_rect, border_radius=6)
        pygame.draw.rect(self.screen, (50, 60, 75), m_rect, border_radius=6)

        r_s = self.font_body.render("[R] Replay Mode", True, (20, 20, 20))
        m_s = self.font_body.render("[M] Main Menu", True, self.COLOR_TEXT)
        self.screen.blit(r_s, (r_rect.x + r_rect.w//2 - r_s.get_width()//2, r_rect.y + 10))
        self.screen.blit(m_s, (m_rect.x + m_rect.w//2 - m_s.get_width()//2, m_rect.y + 10))

    def _handle_menu_clicks(self, mpos: tuple):
        modes = [
            (pygame.Rect(self.width//2 - 320, 160, 640, 80), self.MODE_VISUAL),
            (pygame.Rect(self.width//2 - 320, 260, 640, 80), self.MODE_SPATIAL_AIM),
            (pygame.Rect(self.width//2 - 320, 360, 640, 80), self.MODE_STROOP_GONOGO),
        ]
        for rect, m_name in modes:
            if rect.collidepoint(mpos):
                self.start_session(m_name)
                return

        diffs = [
            (pygame.Rect(self.width//2 - 180, 505, 110, 36), "Easy"),
            (pygame.Rect(self.width//2 - 55, 505, 110, 36), "Medium"),
            (pygame.Rect(self.width//2 + 70, 505, 110, 36), "Hard")
        ]
        for rect, val in diffs:
            if rect.collidepoint(mpos):
                self.set_difficulty(val)
                return

    def _handle_game_over_clicks(self, mpos: tuple):
        r_rect = pygame.Rect(self.width//2 - 200, 525, 180, 42)
        m_rect = pygame.Rect(self.width//2 + 20, 525, 180, 42)
        if r_rect.collidepoint(mpos):
            self.start_session(self.active_mode)
        elif m_rect.collidepoint(mpos):
            self.state = self.STATE_MENU
