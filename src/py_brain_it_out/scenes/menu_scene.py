"""
menu_scene.py — Hauptmenü mit animiertem Hintergrund.
"""
from __future__ import annotations
from py_brain_it_out.settings import FONT_SIZE_XS

import math
import random
import pygame

from .base_scene import BaseScene
from ..settings import (
    COLOR_BG, COLOR_CORAL, COLOR_TEAL, COLOR_YELLOW,
    COLOR_TEXT, COLOR_WHITE, COLOR_PURPLE,
    FONT_SIZE_XL, FONT_SIZE_LG, FONT_SIZE_MD, FONT_SIZE_SM,
    WINDOW_WIDTH, WINDOW_HEIGHT,
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

        # Buttons
        btn_w, btn_h = 260, 60
        cx = WINDOW_WIDTH // 2
        self._btn_play = RoundedButton(
            "🎮  Spielen",
            pygame.Rect(cx - btn_w // 2, 320, btn_w, btn_h),
            color=COLOR_CORAL,
            on_click=self._on_play,
            font_size=FONT_SIZE_MD,
        )
        self._btn_quit = RoundedButton(
            "Beenden",
            pygame.Rect(cx - btn_w // 2, 400, btn_w, btn_h),
            color=(140, 130, 125),
            font_size=FONT_SIZE_MD,
            on_click=self._on_quit,
        )

        # Schwebende Dekoration
        self._bubbles = [
            {
                "x": random.randint(50, WINDOW_WIDTH - 50),
                "y": random.randint(50, WINDOW_HEIGHT - 50),
                "r": random.randint(15, 40),
                "color": random.choice([COLOR_CORAL, COLOR_TEAL, COLOR_YELLOW, COLOR_PURPLE]),
                "speed": random.uniform(20, 60),
                "phase": random.uniform(0, math.pi * 2),
            }
            for _ in range(12)
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

        # Dekoratives Gehirn-Symbol (Text-Kunst)
        font_brain = get_font(80)
        brain_surf = font_brain.render("🧠", True, (200, 180, 170))
        scale = self._pulse.scale
        scaled = pygame.transform.scale(
            brain_surf,
            (int(brain_surf.get_width() * scale), int(brain_surf.get_height() * scale))
        )
        surface.blit(scaled, scaled.get_rect(center=(WINDOW_WIDTH // 2, 180)))

        # Titel mit Bounce-Animation
        title_y_offset = self._title_tween.value
        font_title = get_font(FONT_SIZE_XL + 8, bold=True)
        title_surf = font_title.render("Py Brain It Out!", True, COLOR_TEXT)
        # Schatten
        shadow_surf = font_title.render("Py Brain It Out!", True, (0, 0, 0))
        shadow_surf.set_alpha(30)
        surface.blit(shadow_surf, shadow_surf.get_rect(center=(WINDOW_WIDTH // 2 + 3, 78 + 3 + title_y_offset)))
        surface.blit(title_surf, title_surf.get_rect(center=(WINDOW_WIDTH // 2, 78 + title_y_offset)))

        # Untertitel
        subtitle_alpha = int(min(255, self._subtitle_tween.value * 255))
        font_sub = get_font(FONT_SIZE_SM)
        sub_surf = font_sub.render("Tricky Rätsel auf Deutsch 🇩🇪", True, (120, 110, 105))
        sub_surf.set_alpha(subtitle_alpha)
        surface.blit(sub_surf, sub_surf.get_rect(center=(WINDOW_WIDTH // 2, 240)))

        # Fortschritts-Info
        save = self.game.save_data
        solved = sum(1 for v in save["levels"].values() if v.get("solved", False))
        if solved > 0:
            font_prog = get_font(FONT_SIZE_XS)
            prog_text = f"Fortschritt: {solved}/{len(save['levels'])} Level gelöst"
            prog_surf = font_prog.render(prog_text, True, (150, 140, 135))
            surface.blit(prog_surf, prog_surf.get_rect(center=(WINDOW_WIDTH // 2, 285)))

        # Buttons
        self._btn_play.draw(surface)
        self._btn_quit.draw(surface)

        # Version
        font_ver = get_font(12)
        ver_surf = font_ver.render("v0.1.0 — 8 Level", True, (180, 170, 165))
        surface.blit(ver_surf, (WINDOW_WIDTH - 130, WINDOW_HEIGHT - 22))

    def _on_play(self) -> None:
        from .level_select import LevelSelectScene
        self.game.push_scene(LevelSelectScene(self.game))

    def _on_quit(self) -> None:
        pygame.event.post(pygame.event.Event(pygame.QUIT))
