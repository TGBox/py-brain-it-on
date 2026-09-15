"""
level_select.py — Level-Auswahl mit Sterneanzeige und Lock-System.
"""
from __future__ import annotations

import math
import pygame

from .base_scene import BaseScene
from ..settings import (
    COLOR_BG, COLOR_CORAL, COLOR_TEAL, COLOR_YELLOW,
    COLOR_TEXT, COLOR_TEXT_LIGHT, COLOR_WHITE, COLOR_PURPLE,
    FONT_SIZE_LG, FONT_SIZE_MD, FONT_SIZE_SM, FONT_SIZE_XS,
    TOTAL_LEVELS, WINDOW_WIDTH, WINDOW_HEIGHT,
)
from ..ui.components import (
    RoundedButton, get_font, draw_rounded_rect, draw_text_centered, draw_star,
)
from ..ui.animations import Tween, ease_out_back


# Level-Farben (eine pro Level)
_LEVEL_COLORS = [
    (255, 107, 107),   # Korallrot
    (78, 205, 196),    # Türkis
    (255, 230, 109),   # Gelb
    (162, 105, 220),   # Lila
    (85, 210, 130),    # Grün
    (255, 165, 60),    # Orange
    (100, 181, 246),   # Hellblau
    (240, 98, 146),    # Pink
]


class LevelSelectScene(BaseScene):
    """Level-Auswahl-Szene."""

    def __init__(self, game) -> None:
        super().__init__(game)
        self._t = 0.0
        # Einblend-Animationen für Kacheln
        self._tile_tweens = [
            Tween(0, 1, 0.4 + i * 0.06, ease_out_back)
            for i in range(TOTAL_LEVELS)
        ]
        self._back_btn = RoundedButton(
            "← Zurück",
            pygame.Rect(20, 15, 130, 44),
            color=(140, 130, 125),
            font_size=FONT_SIZE_SM,
            on_click=self._on_back,
        )
        # Layout: 4×2 Grid
        self._tile_rects = self._calc_tile_rects()
        self._hovered: int | None = None

    def on_enter(self) -> None:
        for tw in self._tile_tweens:
            tw.reset()

    def handle_event(self, event: pygame.event.Event) -> None:
        self._back_btn.handle_event(event)
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for i, rect in enumerate(self._tile_rects):
                if rect.collidepoint(event.pos):
                    if self._is_unlocked(i + 1):
                        self._start_level(i + 1)
                    return

    def update(self, dt: float) -> None:
        self._t += dt
        self._back_btn.update(dt)
        for tw in self._tile_tweens:
            tw.update(dt)
        # Hover-Erkennung
        mx, my = pygame.mouse.get_pos()
        self._hovered = None
        for i, rect in enumerate(self._tile_rects):
            if rect.collidepoint((mx, my)) and self._is_unlocked(i + 1):
                self._hovered = i

    def draw(self, surface: pygame.Surface) -> None:
        surface.fill(COLOR_BG)

        # Überschrift
        font_title = get_font(FONT_SIZE_LG, bold=True)
        title_surf = font_title.render("Level Auswahl", True, COLOR_TEXT)
        surface.blit(title_surf, title_surf.get_rect(center=(WINDOW_WIDTH // 2, 48)))

        # Punkte-Linie
        pygame.draw.line(surface, (220, 210, 200), (60, 78), (WINDOW_WIDTH - 60, 78), 2)

        # Level-Kacheln
        for i, rect in enumerate(self._tile_rects):
            self._draw_tile(surface, i, rect)

        # Zurück-Button
        self._back_btn.draw(surface)

        # Gesamt-Sterne unten
        save = self.game.save_data
        total_stars = sum(v.get("stars", 0) for v in save["levels"].values())
        max_stars = TOTAL_LEVELS * 3
        font_sm = get_font(FONT_SIZE_SM)
        star_text = f"⭐ {total_stars} / {max_stars} Sterne"
        st_surf = font_sm.render(star_text, True, (150, 140, 135))
        surface.blit(st_surf, st_surf.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT - 22)))

    def _draw_tile(self, surface: pygame.Surface, idx: int, rect: pygame.Rect) -> None:
        level_num = idx + 1
        save = self.game.save_data
        level_data = save["levels"].get(str(level_num), {"stars": 0, "solved": False})
        stars = level_data.get("stars", 0)
        solved = level_data.get("solved", False)
        unlocked = self._is_unlocked(level_num)

        # Einblend-Skalierung
        scale = self._tile_tweens[idx].value
        if scale < 0.01:
            return
        cx, cy = rect.center
        w = int(rect.width * scale)
        h = int(rect.height * scale)
        scaled_rect = pygame.Rect(cx - w // 2, cy - h // 2, w, h)

        # Farbe
        if not unlocked:
            color = (190, 185, 180)
        elif self._hovered == idx:
            base = _LEVEL_COLORS[idx % len(_LEVEL_COLORS)]
            color = tuple(min(255, c + 20) for c in base)
        else:
            color = _LEVEL_COLORS[idx % len(_LEVEL_COLORS)]

        draw_rounded_rect(surface, color, scaled_rect, radius=18, shadow_offset=5)

        if not unlocked:
            # Schloss-Symbol
            font_lock = get_font(28)
            lock_surf = font_lock.render("🔒", True, (160, 155, 150))
            surface.blit(lock_surf, lock_surf.get_rect(center=(cx, cy - 8)))
            font_sm = get_font(FONT_SIZE_XS)
            lock_label = font_sm.render(f"Level {level_num}", True, (160, 155, 150))
            surface.blit(lock_label, lock_label.get_rect(center=(cx, cy + 22)))
        else:
            # Level-Nummer
            font_num = get_font(FONT_SIZE_MD + 6, bold=True)
            num_surf = font_num.render(str(level_num), True, COLOR_WHITE)
            surface.blit(num_surf, num_surf.get_rect(center=(cx, cy - 14)))

            # Sterne (klein)
            star_r = 9
            for s in range(3):
                sx = cx - 18 + s * 18
                draw_star(surface, (sx, cy + 22), star_r, filled=(s < stars))

    def _calc_tile_rects(self) -> list[pygame.Rect]:
        """Berechnet die Positionen der 8 Kacheln in einem 4×2-Grid."""
        rects = []
        cols, rows = 4, 2
        tile_w, tile_h = 150, 110
        pad_x = (WINDOW_WIDTH - cols * tile_w) // (cols + 1)
        pad_y = 50
        start_y = 105
        for row in range(rows):
            for col in range(cols):
                x = pad_x + col * (tile_w + pad_x)
                y = start_y + row * (tile_h + pad_y)
                rects.append(pygame.Rect(x, y, tile_w, tile_h))
        return rects

    def _is_unlocked(self, level: int) -> bool:
        """Level 1 ist immer frei; folgende werden nach Lösung des Vorgängers freigeschaltet."""
        if level == 1:
            return True
        save = self.game.save_data
        prev = save["levels"].get(str(level - 1), {})
        return prev.get("solved", False)

    def _start_level(self, level: int) -> None:
        from .game_scene import GameScene
        self.game.push_scene(GameScene(self.game, level))

    def _on_back(self) -> None:
        self.game.pop_scene()
