"""
puzzle_05.py — Level 5: "Mach die Parkluecke frei!"

TRICK: Die Parklücke ist durch ein Auto belegt. Aber das Parkplatz-Schild
kann man aus dem Spielbereich herausziehen — damit "existiert" die Parkpflicht nicht mehr!
Alternativ: Das Auto aus dem Bild herausschieben.
"""
from __future__ import annotations

import math
import pygame

from ..puzzles.base_puzzle import BasePuzzle
from ..settings import COLOR_BG, COLOR_CORAL, COLOR_TEXT, COLOR_WHITE, COLOR_TEAL
from ..ui.components import get_font, draw_rounded_rect
from ..ui.animations import ShakeEffect


class Puzzle05(BasePuzzle):
    LEVEL_NUMBER = 5
    TITLE = "Level 5"
    QUESTION = "Mach die Parklücke frei!"
    HINT = "Das störende Auto lässt sich vielleicht aus dem Bild schieben. Versuch es einfach mal!"

    def __init__(self, game, on_solved, on_wrong):
        super().__init__(game, on_solved, on_wrong)
        # Das blockierende Auto
        self._car_pos = [400, 350]
        self._car_dragging = False
        self._car_drag_offset = [0, 0]
        # Parkplatz (Zielbereich, der frei gemacht werden soll)
        self._parking_rect = pygame.Rect(310, 290, 180, 120)
        self._shake = ShakeEffect()
        # Eigenes Auto (immer da, soll dort parken)
        self._my_car_pos = [130, 350]

    def handle_event(self, event: pygame.event.Event) -> None:
        if self._solved:
            return

        car_rect = self._get_car_rect()

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if car_rect.collidepoint(event.pos):
                self._car_dragging = True
                self._car_drag_offset = [
                    event.pos[0] - self._car_pos[0],
                    event.pos[1] - self._car_pos[1],
                ]

        if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if self._car_dragging:
                self._car_dragging = False
                # Prüfen: Auto außerhalb des Bildschirms?
                from ..settings import WINDOW_WIDTH, WINDOW_HEIGHT
                cx, cy = self._car_pos
                if cx < -80 or cx > WINDOW_WIDTH + 80 or cy < -80 or cy > WINDOW_HEIGHT + 80:
                    self._solve()
                    return
                # Prüfen: Auto nicht mehr auf Parkplatz
                car_rect_now = self._get_car_rect()
                if not car_rect_now.colliderect(self._parking_rect):
                    self._solve()

        if event.type == pygame.MOUSEMOTION:
            if self._car_dragging:
                self._car_pos[0] = event.pos[0] - self._car_drag_offset[0]
                self._car_pos[1] = event.pos[1] - self._car_drag_offset[1]

    def update(self, dt: float) -> None:
        self._shake.update(dt)

    def draw(self, surface: pygame.Surface, area: pygame.Rect) -> None:
        w, h = area.width, area.height
        ox, oy = area.x, area.y

        # Straße
        surface.fill((100, 100, 115), area)

        # Gehsteig oben
        pygame.draw.rect(surface, (200, 190, 175), (ox, oy, w, 80))
        pygame.draw.rect(surface, (180, 170, 155), (ox, oy + 80, w, 5))

        # Straßenmarkierungen
        for i in range(0, w, 80):
            pygame.draw.rect(surface, (255, 240, 100), (ox + i, oy + h // 2 - 5, 50, 10), border_radius=3)

        # Parkplatz-Markierung
        pr = self._parking_rect.move(ox, oy - area.y)
        # Grüner Parkplatz-Rahmen
        pygame.draw.rect(surface, (80, 200, 120), (ox + 310, oy + 280, 180, 130), 4, border_radius=6)
        # "P" Symbol
        font_p = get_font(48, bold=True)
        p_surf = font_p.render("P", True, (80, 200, 120))
        p_surf.set_alpha(100)
        surface.blit(p_surf, p_surf.get_rect(center=(ox + 400, oy + 345)))

        # Blockierendes Auto (rot, ziehbar)
        self._draw_car(surface, self._car_pos, (220, 70, 70), label="🚗")

        # Eigenes Auto (blau, wartet links)
        self._draw_car(surface, self._my_car_pos, (70, 120, 220), label="🚙")

        # Pfeil vom eigenen Auto zum Parkplatz
        ax1, ay1 = self._my_car_pos[0] + 70, self._my_car_pos[1]
        ax2, ay2 = 310, self._my_car_pos[1]
        pygame.draw.line(surface, (70, 120, 220), (ax1, ay1), (ax2, ay2), 3)
        # Pfeilspitze
        pygame.draw.polygon(surface, (70, 120, 220), [
            (ax2, ay2),
            (ax2 - 12, ay2 - 8),
            (ax2 - 12, ay2 + 8),
        ])

        # Hinweis
        font_sm = get_font(15)
        hint = font_sm.render("Rotes Auto aus dem Weg ziehen!", True, (220, 220, 220))
        surface.blit(hint, hint.get_rect(center=(ox + w // 2, oy + h - 20)))

    def _draw_car(self, surface, pos, color, label="🚗"):
        cx, cy = int(pos[0]), int(pos[1])
        # Karosserie unten
        pygame.draw.rect(surface, color, (cx - 55, cy - 18, 110, 36), border_radius=8)
        # Karosserie oben (Dach)
        pygame.draw.rect(surface, color, (cx - 35, cy - 38, 70, 26), border_radius=10)
        # Fenster
        pygame.draw.rect(surface, (180, 220, 240), (cx - 30, cy - 35, 28, 20), border_radius=5)
        pygame.draw.rect(surface, (180, 220, 240), (cx + 2, cy - 35, 28, 20), border_radius=5)
        # Räder
        for wx in [cx - 35, cx + 35]:
            pygame.draw.circle(surface, (40, 40, 40), (wx, cy + 18), 14)
            pygame.draw.circle(surface, (80, 80, 80), (wx, cy + 18), 8)
        # Scheinwerfer
        pygame.draw.circle(surface, (255, 240, 150), (cx + 52, cy - 8), 6)
        pygame.draw.circle(surface, (255, 240, 150), (cx + 52, cy + 8), 6)
        # Rücklichter
        pygame.draw.circle(surface, (200, 50, 50), (cx - 52, cy - 8), 5)
        pygame.draw.circle(surface, (200, 50, 50), (cx - 52, cy + 8), 5)

    def _get_car_rect(self) -> pygame.Rect:
        cx, cy = int(self._car_pos[0]), int(self._car_pos[1])
        return pygame.Rect(cx - 55, cy - 38, 110, 56)
