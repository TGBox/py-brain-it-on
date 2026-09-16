"""
level_select.py — Level-Auswahl mit Seiten-Navigation (Pagination) für 25+ Level.
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
    RoundedButton, get_font, draw_rounded_rect, draw_star,
)
from ..ui.animations import Tween, ease_out_back
from .. import save_manager


# Farbpalette für die Kacheln
_LEVEL_COLORS = [
    (255, 107, 107),   # Korallrot
    (78, 205, 196),    # Türkis
    (255, 220, 90),    # Gelb
    (162, 105, 220),   # Lila
    (85, 210, 130),    # Grün
    (255, 160, 50),    # Orange
    (100, 180, 245),   # Hellblau
    (240, 100, 150),   # Pink
    (80, 200, 200),    # Meerblau
    (190, 120, 230),   # Violett
]


def _draw_lock(surface: pygame.Surface, cx: int, cy: int, color: tuple) -> None:
    """Zeichnet ein sauberes Schloss-Symbol für gesperrte Level."""
    # Bügel
    pygame.draw.arc(surface, color, pygame.Rect(cx - 16, cy - 25, 32, 28), 0, math.pi, 5)
    # Körper
    pygame.draw.rect(surface, color, pygame.Rect(cx - 20, cy - 8, 40, 32), border_radius=6)
    # Schlüsselloch
    pygame.draw.circle(surface, COLOR_WHITE, (cx, cy + 4), 5)
    pygame.draw.line(surface, COLOR_WHITE, (cx, cy + 4), (cx, cy + 14), 3)


class LevelSelectScene(BaseScene):
    """Level-Auswahl-Szene mit Blättern durch Seiten (10 Level pro Seite)."""

    LEVELS_PER_PAGE = 10

    def __init__(self, game) -> None:
        super().__init__(game)
        self._t = 0.0
        self.page = 0
        self.total_pages = math.ceil(TOTAL_LEVELS / self.LEVELS_PER_PAGE)
        self._show_reset_confirm = False

        # Einblend-Animationen für Kacheln
        self._tile_tweens = [
            Tween(0, 1, 0.35 + i * 0.04, ease_out_back)
            for i in range(self.LEVELS_PER_PAGE)
        ]

        # Buttons
        self._back_btn = RoundedButton(
            "Zurück",
            pygame.Rect(60, 45, 160, 60),
            color=(140, 130, 125),
            font_size=FONT_SIZE_SM,
            on_click=self._on_back,
        )
        self._reset_btn = RoundedButton(
            "Fortschritt zurücksetzen",
            pygame.Rect(WINDOW_WIDTH - 390, 45, 330, 60),
            color=(200, 95, 85),
            font_size=FONT_SIZE_SM,
            on_click=self._on_request_reset,
        )
        self._prev_btn = RoundedButton(
            "Vorherige Seite",
            pygame.Rect(WINDOW_WIDTH // 2 - 340, 770, 210, 56),
            color=COLOR_TEAL,
            font_size=FONT_SIZE_SM,
            on_click=self._on_prev_page,
        )
        self._next_btn = RoundedButton(
            "Nächste Seite",
            pygame.Rect(WINDOW_WIDTH // 2 + 130, 770, 210, 56),
            color=COLOR_TEAL,
            font_size=FONT_SIZE_SM,
            on_click=self._on_next_page,
        )


        # Dialog-Buttons für Reset-Bestätigung
        cx, cy = WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2
        self._btn_confirm_reset = RoundedButton(
            "Ja, zurücksetzen",
            pygame.Rect(cx - 240, cy + 40, 220, 54),
            color=COLOR_CORAL,
            font_size=FONT_SIZE_SM,
            on_click=self._on_confirm_reset,
        )
        self._btn_cancel_reset = RoundedButton(
            "Abbrechen",
            pygame.Rect(cx + 20, cy + 40, 220, 54),
            color=(140, 130, 125),
            font_size=FONT_SIZE_SM,
            on_click=self._on_cancel_reset,
        )

        self._tile_rects = self._calc_tile_rects()
        self._hovered: int | None = None

    def on_enter(self) -> None:
        self._reset_tweens()
        self._show_reset_confirm = False

    def _reset_tweens(self) -> None:
        for tw in self._tile_tweens:
            tw.reset()

    def _on_prev_page(self) -> None:
        if self.page > 0:
            self.page -= 1
            self._reset_tweens()

    def _on_next_page(self) -> None:
        if self.page < self.total_pages - 1:
            self.page += 1
            self._reset_tweens()

    def _on_request_reset(self) -> None:
        self._show_reset_confirm = True

    def _on_confirm_reset(self) -> None:
        self.game.save_data = save_manager.reset()
        self.page = 0
        self._reset_tweens()
        self._show_reset_confirm = False

    def _on_cancel_reset(self) -> None:
        self._show_reset_confirm = False

    def handle_event(self, event: pygame.event.Event) -> None:
        if self._show_reset_confirm:
            self._btn_confirm_reset.handle_event(event)
            self._btn_cancel_reset.handle_event(event)
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self._show_reset_confirm = False
            return

        self._back_btn.handle_event(event)
        self._reset_btn.handle_event(event)
        if self.page > 0:
            self._prev_btn.handle_event(event)
        if self.page < self.total_pages - 1:
            self._next_btn.handle_event(event)

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for slot_idx, rect in enumerate(self._tile_rects):
                level_num = self.page * self.LEVELS_PER_PAGE + slot_idx + 1
                if level_num > TOTAL_LEVELS:
                    break
                if rect.collidepoint(event.pos):
                    if self._is_unlocked(level_num):
                        self._start_level(level_num)
                    return

    def update(self, dt: float) -> None:
        self._t += dt
        if self._show_reset_confirm:
            self._btn_confirm_reset.update(dt)
            self._btn_cancel_reset.update(dt)
            return

        self._back_btn.update(dt)
        self._reset_btn.update(dt)
        if self.page > 0:
            self._prev_btn.update(dt)
        if self.page < self.total_pages - 1:
            self._next_btn.update(dt)

        for tw in self._tile_tweens:
            tw.update(dt)

        # Hover-Erkennung
        mx, my = pygame.mouse.get_pos()
        self._hovered = None
        for slot_idx, rect in enumerate(self._tile_rects):
            level_num = self.page * self.LEVELS_PER_PAGE + slot_idx + 1
            if level_num <= TOTAL_LEVELS and rect.collidepoint((mx, my)) and self._is_unlocked(level_num):
                self._hovered = slot_idx

    def draw(self, surface: pygame.Surface) -> None:
        surface.fill(COLOR_BG)

        # Überschrift
        font_title = get_font(FONT_SIZE_LG + 6, bold=True)
        title_surf = font_title.render("Level-Auswahl", True, COLOR_TEXT)
        surface.blit(title_surf, title_surf.get_rect(center=(WINDOW_WIDTH // 2, 75)))

        # Trennlinie
        pygame.draw.line(surface, (220, 210, 200), (100, 135), (WINDOW_WIDTH - 100, 135), 3)

        # Level-Kacheln der aktuellen Seite
        for slot_idx, rect in enumerate(self._tile_rects):
            level_num = self.page * self.LEVELS_PER_PAGE + slot_idx + 1
            if level_num <= TOTAL_LEVELS:
                self._draw_tile(surface, slot_idx, level_num, rect)

        # Zurück-Button & Fortschritt-Reset
        self._back_btn.draw(surface)
        self._reset_btn.draw(surface)

        # Seiten-Navigation (wenn mehrere Seiten)
        if self.total_pages > 1:
            if self.page > 0:
                self._prev_btn.draw(surface)
            if self.page < self.total_pages - 1:
                self._next_btn.draw(surface)

            font_page = get_font(FONT_SIZE_SM, bold=True)
            page_str = f"Seite {self.page + 1} von {self.total_pages}"
            page_surf = font_page.render(page_str, True, COLOR_TEXT_LIGHT)
            surface.blit(page_surf, page_surf.get_rect(center=(WINDOW_WIDTH // 2, 798)))

        # Gesamt-Sterne unten
        save = self.game.save_data
        total_stars = sum(v.get("stars", 0) for v in save.get("levels", {}).values())
        max_stars = TOTAL_LEVELS * 3
        star_y = WINDOW_HEIGHT - 65
        star_r = 16

        font_sm = get_font(FONT_SIZE_SM)
        text_before = f"Gesamt: {total_stars} / {max_stars} Sterne gesammelt"
        text_surf = font_sm.render(text_before, True, (130, 120, 115))
        total_w_stars = 3 * star_r * 2 + 2 * 6
        total_content_w = total_w_stars + 16 + text_surf.get_width()
        start_x = WINDOW_WIDTH // 2 - total_content_w // 2

        for s in range(3):
            draw_star(surface, (start_x + s * (star_r * 2 + 6) + star_r, star_y),
                      star_r, filled=(s < min(3, total_stars)))
        surface.blit(text_surf, text_surf.get_rect(
            midleft=(start_x + total_w_stars + 16, star_y)
        ))

        # Bestätigungs-Dialog zum Zurücksetzen
        if self._show_reset_confirm:
            overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 160))
            surface.blit(overlay, (0, 0))

            card_w, card_h = 660, 260
            cx, cy = WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2
            card_rect = pygame.Rect(cx - card_w // 2, cy - card_h // 2, card_w, card_h)
            draw_rounded_rect(surface, COLOR_WHITE, card_rect, radius=24, shadow_offset=10)

            font_dlg_title = get_font(FONT_SIZE_MD, bold=True)
            t_surf = font_dlg_title.render("Fortschritt zurücksetzen?", True, COLOR_CORAL)
            surface.blit(t_surf, t_surf.get_rect(center=(cx, cy - 60)))

            font_dlg_msg = get_font(FONT_SIZE_SM)
            msg_surf = font_dlg_msg.render("Alle Sterne und freigeschalteten Level werden gelöscht.", True, COLOR_TEXT)
            surface.blit(msg_surf, msg_surf.get_rect(center=(cx, cy - 15)))

            self._btn_confirm_reset.draw(surface)
            self._btn_cancel_reset.draw(surface)

    def _draw_tile(self, surface: pygame.Surface, slot_idx: int, level_num: int, rect: pygame.Rect) -> None:
        save = self.game.save_data
        level_data = save.get("levels", {}).get(str(level_num), {"stars": 0, "solved": False})
        stars = level_data.get("stars", 0)
        unlocked = self._is_unlocked(level_num)

        # Einblend-Skalierung
        scale = self._tile_tweens[slot_idx].value
        if scale < 0.01:
            return
        cx, cy = rect.center
        w = int(rect.width * scale)
        h = int(rect.height * scale)
        scaled_rect = pygame.Rect(cx - w // 2, cy - h // 2, w, h)

        # Farbe
        if not unlocked:
            color = (195, 190, 185)
        elif self._hovered == slot_idx:
            base = _LEVEL_COLORS[(level_num - 1) % len(_LEVEL_COLORS)]
            color = tuple(min(255, c + 25) for c in base)
        else:
            color = _LEVEL_COLORS[(level_num - 1) % len(_LEVEL_COLORS)]

        draw_rounded_rect(surface, color, scaled_rect, radius=24, shadow_offset=6)

        if not unlocked:
            _draw_lock(surface, cx, cy - 15, (150, 145, 140))
            font_sm = get_font(FONT_SIZE_SM)
            lock_label = font_sm.render(f"Level {level_num}", True, (145, 140, 135))
            surface.blit(lock_label, lock_label.get_rect(center=(cx, cy + 36)))
        else:
            # Level-Nummer
            font_num = get_font(FONT_SIZE_LG, bold=True)
            num_surf = font_num.render(str(level_num), True, COLOR_WHITE)
            surface.blit(num_surf, num_surf.get_rect(center=(cx, cy - 25)))

            # Sterne (3 Stück)
            star_r = 16
            spacing = star_r * 2 + 10
            start_star_x = cx - spacing
            for s in range(3):
                sx = start_star_x + s * spacing
                draw_star(surface, (sx, cy + 35), star_r, filled=(s < stars))

    def _calc_tile_rects(self) -> list[pygame.Rect]:
        """Berechnet 10 Kacheln in einem 5×2-Grid für 1920x1080."""
        rects = []
        cols, rows = 5, 2
        tile_w, tile_h = 280, 210
        pad_x = (WINDOW_WIDTH - cols * tile_w) // (cols + 1)
        start_y = 200
        pad_y = 50
        for row in range(rows):
            for col in range(cols):
                x = pad_x + col * (tile_w + pad_x)
                y = start_y + row * (tile_h + pad_y)
                rects.append(pygame.Rect(x, y, tile_w, tile_h))
        return rects

    def _is_unlocked(self, level: int) -> bool:
        """Level 1 ist immer frei; folgende nach Lösung des Vorgängers."""
        if level == 1:
            return True
        save = self.game.save_data
        prev = save.get("levels", {}).get(str(level - 1), {})
        return prev.get("solved", False)

    def _start_level(self, level: int) -> None:
        from .play_scene import PlayScene
        self.game.push_scene(PlayScene(self.game, level))

    def _on_back(self) -> None:
        self.game.pop_scene()
