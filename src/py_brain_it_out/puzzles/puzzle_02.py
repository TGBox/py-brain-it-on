"""
puzzle_02.py — Level 2: "Finde die Katze"

TRICK: Die Katze ist hinter einem Busch versteckt. Busch wegziehen!
"""
from __future__ import annotations

import math
import pygame

from ..puzzles.base_puzzle import BasePuzzle
from ..settings import COLOR_BG, COLOR_GREEN, COLOR_TEXT, COLOR_WHITE
from ..ui.components import draw_rounded_rect, draw_text_centered, get_font
from ..ui.animations import ShakeEffect, Tween, ease_out_bounce


class Puzzle02(BasePuzzle):
    LEVEL_NUMBER = 2
    TITLE = "Level 2"
    QUESTION = "Finde die Katze!"
    HINT = "Manchmal verstecken sich Katzen hinter Dingen. Vielleicht musst du etwas beiseite schieben?"

    def __init__(self, game, on_solved, on_wrong):
        super().__init__(game, on_solved, on_wrong)
        # Startpositionen
        self._bush_pos = [400, 360]   # Busch (ziehbar)
        self._cat_pos = [400, 355]    # Katze (darunter versteckt)
        self._dragging_bush = False
        self._drag_offset = [0, 0]
        self._cat_revealed = False
        self._cat_blink_timer = 0.0
        self._shake = ShakeEffect()
        self._success_tween: Tween | None = None
        self._reveal_timer = 0.0

    def handle_event(self, event: pygame.event.Event) -> None:
        if self._solved:
            return
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            bx, by = self._bush_pos
            bush_rect = pygame.Rect(bx - 70, by - 50, 140, 100)
            if bush_rect.collidepoint(event.pos):
                self._dragging_bush = True
                self._drag_offset = [event.pos[0] - bx, event.pos[1] - by]

        if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if self._dragging_bush:
                self._dragging_bush = False
                # Prüfen ob Katze sichtbar
                bx, by = self._bush_pos
                cx, cy = self._cat_pos
                dist = math.hypot(bx - cx, by - cy)
                if dist > 100:
                    self._cat_revealed = True
                    self._reveal_timer = 0.0

        if event.type == pygame.MOUSEMOTION:
            if self._dragging_bush:
                self._bush_pos[0] = event.pos[0] - self._drag_offset[0]
                self._bush_pos[1] = event.pos[1] - self._drag_offset[1]

        # Katze anklicken (wenn sichtbar)
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self._cat_revealed:
                cx, cy = self._cat_pos
                cat_rect = pygame.Rect(cx - 35, cy - 35, 70, 70)
                if cat_rect.collidepoint(event.pos):
                    self._solve()

    def update(self, dt: float) -> None:
        self._cat_blink_timer += dt
        self._shake.update(dt)
        if self._cat_revealed:
            self._reveal_timer += dt

    def draw(self, surface: pygame.Surface, area: pygame.Rect) -> None:
        w, h = area.width, area.height
        ox, oy = area.x, area.y
        surface.fill(COLOR_BG, area)

        # Gras-Hintergrund
        grass_rect = pygame.Rect(ox, oy + int(h * 0.6), w, int(h * 0.4))
        pygame.draw.rect(surface, (120, 200, 80), grass_rect)

        # Himmel-Gradient-Andeutung
        sky_rect = pygame.Rect(ox, oy, w, int(h * 0.6))
        sky_surf = pygame.Surface((w, int(h * 0.6)))
        sky_surf.fill((180, 220, 255))
        surface.blit(sky_surf, (ox, oy))

        # Sonne
        pygame.draw.circle(surface, (255, 230, 100), (ox + 80, oy + 80), 40)

        # Katze zeichnen (immer, aber ggf. verdeckt)
        self._draw_cat(surface, self._cat_pos)

        # Hinweis-Pfeil wenn Katze sichtbar
        if self._cat_revealed and self._reveal_timer < 2.0:
            alpha = int(255 * (1 - self._reveal_timer / 2.0))
            font = get_font(18)
            hint = font.render("😸 Klick mich!", True, (50, 150, 50))
            hint.set_alpha(alpha)
            surface.blit(hint, hint.get_rect(center=(self._cat_pos[0], self._cat_pos[1] - 55)))

        # Busch zeichnen (oben drüber)
        self._draw_bush(surface, self._bush_pos)

        # Drag-Hinweis
        if not self._cat_revealed:
            font = get_font(16)
            hint = font.render("← Ziehe den Busch weg →", True, (100, 100, 100))
            surface.blit(hint, hint.get_rect(center=(ox + w // 2, oy + h - 30)))

    def _draw_cat(self, surface: pygame.Surface, pos: list) -> None:
        """Zeichnet eine einfache Cartoon-Katze."""
        cx, cy = int(pos[0]), int(pos[1])
        # Körper
        pygame.draw.ellipse(surface, (180, 140, 100), (cx - 25, cy, 50, 35))
        # Kopf
        pygame.draw.circle(surface, (200, 160, 120), (cx, cy), 30)
        # Ohren
        pygame.draw.polygon(surface, (200, 160, 120), [(cx - 20, cy - 25), (cx - 30, cy - 50), (cx - 8, cy - 28)])
        pygame.draw.polygon(surface, (200, 160, 120), [(cx + 20, cy - 25), (cx + 30, cy - 50), (cx + 8, cy - 28)])
        # Ohren innen (pink)
        pygame.draw.polygon(surface, (255, 180, 180), [(cx - 18, cy - 26), (cx - 26, cy - 44), (cx - 10, cy - 28)])
        pygame.draw.polygon(surface, (255, 180, 180), [(cx + 18, cy - 26), (cx + 26, cy - 44), (cx + 10, cy - 28)])
        # Augen
        blink = self._cat_blink_timer % 3.0 < 0.15
        if blink:
            pygame.draw.line(surface, (50, 30, 20), (cx - 12, cy - 5), (cx - 4, cy - 5), 3)
            pygame.draw.line(surface, (50, 30, 20), (cx + 4, cy - 5), (cx + 12, cy - 5), 3)
        else:
            pygame.draw.circle(surface, (50, 30, 20), (cx - 8, cy - 5), 6)
            pygame.draw.circle(surface, (50, 30, 20), (cx + 8, cy - 5), 6)
            pygame.draw.circle(surface, (255, 255, 255), (cx - 6, cy - 7), 2)
            pygame.draw.circle(surface, (255, 255, 255), (cx + 10, cy - 7), 2)
        # Nase
        pygame.draw.polygon(surface, (230, 120, 140),
                             [(cx, cy + 2), (cx - 4, cy - 2), (cx + 4, cy - 2)])
        # Schnurrbart
        pygame.draw.line(surface, (100, 80, 60), (cx - 4, cy + 3), (cx - 28, cy + 1), 2)
        pygame.draw.line(surface, (100, 80, 60), (cx - 4, cy + 5), (cx - 26, cy + 8), 2)
        pygame.draw.line(surface, (100, 80, 60), (cx + 4, cy + 3), (cx + 28, cy + 1), 2)
        pygame.draw.line(surface, (100, 80, 60), (cx + 4, cy + 5), (cx + 26, cy + 8), 2)
        # Schwanz
        tail_pts = [
            (cx + 25, cy + 20),
            (cx + 50, cy + 30),
            (cx + 60, cy + 10),
            (cx + 55, cy - 10),
        ]
        if len(tail_pts) >= 2:
            pygame.draw.lines(surface, (180, 140, 100), False, tail_pts, 5)

    def _draw_bush(self, surface: pygame.Surface, pos: list) -> None:
        """Zeichnet einen Busch (3 überlappende Kreise)."""
        bx, by = int(pos[0]), int(pos[1])
        # Schatten
        pygame.draw.ellipse(surface, (0, 100, 0), (bx - 72, by - 12, 144, 40))
        # Busch-Kreise
        circles = [
            (bx - 40, by - 20, 55),
            (bx, by - 35, 65),
            (bx + 40, by - 20, 55),
        ]
        for cx, cy, r in circles:
            pygame.draw.circle(surface, (40, 160, 60), (cx, cy), r)
        # Dunklere Akzente
        for cx, cy, r in circles:
            pygame.draw.circle(surface, (30, 130, 45), (cx, cy), r, 3)
        # Hellere Highlights
        pygame.draw.circle(surface, (80, 200, 90), (bx - 15, by - 50), 18)
        pygame.draw.circle(surface, (80, 200, 90), (bx + 20, by - 42), 14)

        # Drag-Handle-Andeutung
        font = get_font(14)
        drag_surf = font.render("✋", True, (255, 255, 255))
        drag_surf.set_alpha(180)
        surface.blit(drag_surf, drag_surf.get_rect(center=(bx, by - 10)))
