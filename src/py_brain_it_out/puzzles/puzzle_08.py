"""
puzzle_08.py — Level 8: "Finde den Ausweg!"

TRICK: Der "Ausweg"-Knopf liegt außerhalb des sichtbaren Spielbereichs.
Man muss das Spielfenster selbst vergrößern oder den Knopf aus dem Spielbereich
herausschauen lassen. Tatsächlich: Der Knopf ist halb aus dem Bereich heraus.
Oder: Der Text "Ausweg" in der Frage ist selbst klickbar!
"""
from __future__ import annotations

import math
import pygame

from ..puzzles.base_puzzle import BasePuzzle
from ..settings import (
    COLOR_BG, COLOR_TEXT, COLOR_WHITE, COLOR_CORAL, COLOR_TEAL,
    COLOR_YELLOW, FONT_SIZE_MD,
)
from ..ui.components import get_font, draw_rounded_rect, draw_text_centered
from ..ui.animations import ShakeEffect, Tween, ease_out_bounce


class Puzzle08(BasePuzzle):
    LEVEL_NUMBER = 8
    TITLE = "Level 8"
    QUESTION = "Finde den Ausweg!"
    HINT = "Der Ausweg ist nicht immer da, wo man ihn erwartet. Schau mal außerhalb des Rahmens!"

    def __init__(self, game, on_solved, on_wrong):
        super().__init__(game, on_solved, on_wrong)
        self._shake = ShakeEffect()
        # "Ausweg"-Button außerhalb des normalen Spielbereichs (halb außen)
        # Der Benutzer muss die Maus über den Rand bewegen
        self._ausweg_discovered = False
        self._question_ausweg_rect: pygame.Rect | None = None  # Klickbarer Bereich im Fragetext

        # Wände im Labyrinth
        self._labyrinth_discovered = False
        self._wobble_t = 0.0

        # Fake-Knöpfe (Fallen)
        self._fake_buttons = [
            {"label": "Ausgang →", "rect": pygame.Rect(200, 370, 160, 50), "clicked": False},
            {"label": "← Türe", "rect": pygame.Rect(440, 370, 130, 50), "clicked": False},
            {"label": "Hinaus!", "rect": pygame.Rect(310, 440, 150, 50), "clicked": False},
        ]

    def handle_event(self, event: pygame.event.Event) -> None:
        if self._solved:
            return
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            # Prüfen: Klick auf "Ausweg" im Fragetext
            if self._question_ausweg_rect and self._question_ausweg_rect.collidepoint(event.pos):
                self._solve()
                return

            # Fake-Buttons
            for btn in self._fake_buttons:
                if btn["rect"].collidepoint(event.pos):
                    self._wrong()
                    self._shake.start()
                    btn["clicked"] = True
                    return

    def update(self, dt: float) -> None:
        self._shake.update(dt)
        self._wobble_t += dt

    def draw(self, surface: pygame.Surface, area: pygame.Rect) -> None:
        w, h = area.width, area.height
        ox, oy = area.x, area.y
        surface.fill((50, 48, 62), area)  # Dunkler Raum

        # Labyrinth-Wände (vereinfacht)
        wall_color = (80, 78, 95)
        walls = [
            (ox + 80, oy + 140, 200, 20),
            (ox + 80, oy + 140, 20, 180),
            (ox + 500, oy + 140, 200, 20),
            (ox + 680, oy + 140, 20, 180),
            (ox + 80, oy + 300, 120, 20),
            (ox + 600, oy + 300, 100, 20),
            (ox + 200, oy + 380, 180, 20),
            (ox + 430, oy + 380, 170, 20),
            (ox + 200, oy + 300, 20, 100),
            (ox + 580, oy + 300, 20, 100),
        ]
        for wx, wy, ww, wh in walls:
            pygame.draw.rect(surface, wall_color, (wx, wy, ww, wh), border_radius=3)

        # Spieler-Figur (kleines Männchen)
        player_cx = ox + 400
        player_cy = oy + 490
        pygame.draw.circle(surface, (255, 220, 170), (player_cx, player_cy - 14), 12)
        pygame.draw.rect(surface, (100, 150, 230), (player_cx - 8, player_cy - 2, 16, 20), border_radius=4)

        # Fragetext mit klickbarem "Ausweg"
        self._draw_question_text(surface, area)

        # Fake-Buttons
        shake_x = int(self._shake.offset_x)
        for btn in self._fake_buttons:
            color = (140, 60, 60) if btn["clicked"] else (100, 100, 140)
            draw_rounded_rect(surface, color, btn["rect"].move(shake_x, 0), radius=12, shadow_offset=3)
            font = get_font(FONT_SIZE_MD - 4)
            draw_text_centered(surface, btn["label"], font, COLOR_WHITE, btn["rect"].move(shake_x, 0).center)

        # "Ausweg"-Button am Rand (fast außerhalb)
        edge_rect = pygame.Rect(area.right - 30, oy + h // 2 - 25, 80, 50)
        pulse = abs(math.sin(self._wobble_t * 3)) * 0.3
        edge_color = (
            int(78 + pulse * 100),
            int(205 + pulse * 50),
            int(196 + pulse * 50)
        )
        # Nur den sichtbaren Teil zeichnen
        clipped = edge_rect.clip(area)
        if clipped.width > 5:
            draw_rounded_rect(surface, edge_color, edge_rect, radius=12, shadow_offset=0)
            font = get_font(14)
            label = font.render("AUSWEG", True, COLOR_WHITE)
            surface.blit(label, label.get_rect(midleft=(area.right - 25, oy + h // 2)))

        # Hinweis
        if len([b for b in self._fake_buttons if b["clicked"]]) >= 2:
            font_sm = get_font(14)
            hint = font_sm.render("Vielleicht liegt der Ausweg... woanders?", True, (180, 170, 200))
            surface.blit(hint, hint.get_rect(center=(ox + w // 2, oy + h - 22)))

    def _draw_question_text(self, surface: pygame.Surface, area: pygame.Rect) -> None:
        """Zeichnet den Fragetext mit hervorgehobenem 'Ausweg'."""
        w = area.width
        ox, oy = area.x, area.y
        font_q = get_font(30)

        part1 = "Finde den "
        part2 = "Ausweg"   # <-- Klickbar!
        part3 = "!"

        surf1 = font_q.render(part1, True, (220, 215, 225))
        surf2 = font_q.render(part2, True, COLOR_YELLOW)
        surf3 = font_q.render(part3, True, (220, 215, 225))

        total_w = surf1.get_width() + surf2.get_width() + surf3.get_width()
        x = ox + (w - total_w) // 2
        y = oy + 90

        surface.blit(surf1, (x, y))
        x2 = x + surf1.get_width()
        surface.blit(surf2, (x2, y))

        # Klick-Bereich
        self._question_ausweg_rect = pygame.Rect(x2 - 4, y - 4, surf2.get_width() + 8, surf2.get_height() + 8)

        # Pulsierender Rahmen
        pulse = abs(math.sin(self._wobble_t * 2))
        frame_surf = pygame.Surface(
            (self._question_ausweg_rect.width, self._question_ausweg_rect.height), pygame.SRCALPHA
        )
        pygame.draw.rect(frame_surf, (255, 230, 100, int(60 + 120 * pulse)),
                         frame_surf.get_rect(), 2, border_radius=4)
        surface.blit(frame_surf, self._question_ausweg_rect.topleft)

        x3 = x2 + surf2.get_width()
        surface.blit(surf3, (x3, y))
