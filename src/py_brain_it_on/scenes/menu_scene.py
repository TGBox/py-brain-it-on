"""
menu_scene.py — Hauptmenü mit animiertem Hintergrund.
"""
from __future__ import annotations

import math
import random
import pygame

from .base_scene import BaseScene
from ..settings import (
    COLOR_BG, COLOR_CORAL, COLOR_TEAL, COLOR_YELLOW,
    COLOR_TEXT, COLOR_WHITE, COLOR_PURPLE,
    FONT_SIZE_XL, FONT_SIZE_LG, FONT_SIZE_MD, FONT_SIZE_SM, FONT_SIZE_XS,
    WINDOW_WIDTH, WINDOW_HEIGHT, TOTAL_LEVELS,
)
from ..ui.components import RoundedButton, get_font, draw_rounded_rect, draw_text_centered
from ..ui.animations import Tween, ease_out_bounce, PulseEffect


class MenuScene(BaseScene):
    """Hauptmenü-Szene."""

    def __init__(self, game) -> None:
        super().__init__(game)
        # Titel-Animation
        self._title_tween = Tween(-80, 0, 0.8, ease_out_bounce)
        self._subtitle_tween = Tween(0, 1, 1.2, ease_out_bounce)

        # Buttons (für 1080p)
        btn_w, btn_h = 360, 80
        cx = WINDOW_WIDTH // 2
        self._btn_play = RoundedButton(
            "Spielen",
            pygame.Rect(cx - btn_w // 2, 580, btn_w, btn_h),
            color=COLOR_CORAL,
            on_click=self._on_play,
            font_size=FONT_SIZE_MD,
        )
        self._btn_quit = RoundedButton(
            "Beenden",
            pygame.Rect(cx - btn_w // 2, 690, btn_w, btn_h),
            color=(140, 130, 125),
            font_size=FONT_SIZE_MD,
            on_click=self._on_quit,
        )

        # Schwebende Dekoration
        self._bubbles = [
            {
                "x": random.randint(50, WINDOW_WIDTH - 50),
                "y": random.randint(50, WINDOW_HEIGHT - 50),
                "r": random.randint(25, 60),
                "color": random.choice([COLOR_CORAL, COLOR_TEAL, COLOR_YELLOW, COLOR_PURPLE]),
                "speed": random.uniform(30, 80),
                "phase": random.uniform(0, math.pi * 2),
            }
            for _ in range(16)
        ]
        self._t = 0.0
        self._pulse = PulseEffect(0.97, 1.03, 1.5)

    def on_enter(self) -> None:
        self._title_tween.reset()
        self._subtitle_tween.reset()

    def handle_event(self, event: pygame.event.Event) -> None:
        self._btn_play.handle_event(event)
        self._btn_quit.handle_event(event)

    def update(self, dt: float) -> None:
        self._t += dt
        self._title_tween.update(dt)
        self._subtitle_tween.update(dt)
        self._btn_play.update(dt)
        self._btn_quit.update(dt)
        self._pulse.update(dt)
        # Bubbles bewegen
        for b in self._bubbles:
            b["y"] -= b["speed"] * dt * 0.3
            b["x"] += math.sin(self._t * 0.5 + b["phase"]) * 0.3
            if b["y"] < -50:
                b["y"] = WINDOW_HEIGHT + 50
                b["x"] = random.randint(50, WINDOW_WIDTH - 50)

    def draw(self, surface: pygame.Surface) -> None:
        surface.fill(COLOR_BG)

        # Schwebende Blasen im Hintergrund
        for b in self._bubbles:
            bubble_surf = pygame.Surface((b["r"] * 2 + 4, b["r"] * 2 + 4), pygame.SRCALPHA)
            alpha = 40
            pygame.draw.circle(bubble_surf, (*b["color"], alpha), (b["r"] + 2, b["r"] + 2), b["r"])
            pygame.draw.circle(bubble_surf, (*b["color"], alpha + 20), (b["r"] + 2, b["r"] + 2), b["r"], 2)
            surface.blit(bubble_surf, (int(b["x"]) - b["r"] - 2, int(b["y"]) - b["r"] - 2))

        # Dekoratives Gehirn-Symbol (gezeichnet)
        brain_cx, brain_cy = WINDOW_WIDTH // 2, 330
        scale = self._pulse.scale
        r = int(90 * scale)
        # Äußerer Kreis
        pygame.draw.circle(surface, COLOR_CORAL, (brain_cx, brain_cy), r)
        pygame.draw.circle(surface, (240, 180, 160), (brain_cx, brain_cy), r - 10)
        # Falten-Linien
        for angle, length in [(0.3, 35), (1.1, 28), (2.0, 32), (2.8, 25)]:
            import math as _m
            ex = brain_cx + int(_m.cos(angle) * (r - 22))
            ey = brain_cy + int(_m.sin(angle) * (r - 22))
            ex2 = brain_cx + int(_m.cos(angle) * (r - 22 + length * 0.5))
            ey2 = brain_cy + int(_m.sin(angle) * (r - 22 + length * 0.5))
            pygame.draw.line(surface, (220, 150, 130), (ex, ey), (ex2, ey2), 5)
        # Trennlinie Mitte
        pygame.draw.line(surface, (220, 150, 130),
                         (brain_cx, brain_cy - r + 15),
                         (brain_cx, brain_cy + r - 15), 4)

        # Titel mit Bounce-Animation
        title_y_offset = self._title_tween.value
        font_title = get_font(FONT_SIZE_XL + 16, bold=True)
        title_surf = font_title.render("Py Brain It On!", True, COLOR_TEXT)
        # Schatten
        shadow_surf = font_title.render("Py Brain It On!", True, (0, 0, 0))
        shadow_surf.set_alpha(30)
        surface.blit(shadow_surf, shadow_surf.get_rect(center=(WINDOW_WIDTH // 2 + 4, 150 + 4 + title_y_offset)))
        surface.blit(title_surf, title_surf.get_rect(center=(WINDOW_WIDTH // 2, 150 + title_y_offset)))

        # Untertitel mit korrektem Umlaut
        subtitle_alpha = int(min(255, self._subtitle_tween.value * 255))
        font_sub = get_font(FONT_SIZE_MD)
        sub_surf = font_sub.render("Tricky Rätsel für schlaue Köpfe", True, (120, 110, 105))
        sub_surf.set_alpha(subtitle_alpha)
        surface.blit(sub_surf, sub_surf.get_rect(center=(WINDOW_WIDTH // 2, 465)))

        # Fortschritts-Info
        save = self.game.save_data
        solved = sum(1 for v in save["levels"].values() if v.get("solved", False))
        if solved > 0:
            font_prog = get_font(FONT_SIZE_SM)
            prog_text = f"Fortschritt: {solved}/{TOTAL_LEVELS} Level gelöst"
            prog_surf = font_prog.render(prog_text, True, (140, 130, 125))
            surface.blit(prog_surf, prog_surf.get_rect(center=(WINDOW_WIDTH // 2, 520)))

        # Buttons
        self._btn_play.draw(surface)
        self._btn_quit.draw(surface)

        # Hinweis zu Vollbild & Steuerung
        font_hint = get_font(FONT_SIZE_XS)
        ctrl_surf = font_hint.render("F11: Vollbild / Fenster | ESC: Beenden", True, (170, 160, 155))
        surface.blit(ctrl_surf, (40, WINDOW_HEIGHT - 45))

        # Version
        ver_surf = font_hint.render(f"v1.0.0 — {TOTAL_LEVELS} Level (FullHD)", True, (170, 160, 155))
        surface.blit(ver_surf, (WINDOW_WIDTH - ver_surf.get_width() - 40, WINDOW_HEIGHT - 45))

    def _on_play(self) -> None:
        from .level_select import LevelSelectScene
        self.game.push_scene(LevelSelectScene(self.game))

    def _on_quit(self) -> None:
        pygame.event.post(pygame.event.Event(pygame.QUIT))
