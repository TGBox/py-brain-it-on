"""
puzzle_04.py — Level 4: "Was ist 1 + 2 + 3 = ?"

TRICK: Nicht "6" eingeben oder tippen, sondern das "="-Zeichen
in der Gleichung selbst anklicken!
"""
from __future__ import annotations

import pygame

from ..puzzles.base_puzzle import BasePuzzle
from ..settings import (
    COLOR_BG, COLOR_CORAL, COLOR_TEXT, COLOR_WHITE,
    COLOR_TEAL, COLOR_YELLOW, FONT_SIZE_XL, FONT_SIZE_MD,
)
from ..ui.components import get_font, draw_rounded_rect, draw_text_centered
from ..ui.animations import ShakeEffect


class Puzzle04(BasePuzzle):
    LEVEL_NUMBER = 4
    TITLE = "Level 4"
    QUESTION = "Was ist 1 + 2 + 3 = ?"
    HINT = "Die Antwort liegt direkt vor dir — buchstäblich! Schau dir die Gleichung an."

    # Antwort-Buttons (Fallen!)
    _ANSWER_BUTTONS = [
        {"label": "3", "pos_ratio": (0.25, 0.72)},
        {"label": "6", "pos_ratio": (0.5, 0.72)},   # <-- Erwartete Antwort, aber FALSCH!
        {"label": "9", "pos_ratio": (0.75, 0.72)},
    ]

    def __init__(self, game, on_solved, on_wrong):
        super().__init__(game, on_solved, on_wrong)
        self._shake = ShakeEffect()
        self._equals_rect: pygame.Rect | None = None
        self._clicked_buttons: list[str] = []
        self._wobble_timer = 0.0

    def handle_event(self, event: pygame.event.Event) -> None:
        if self._solved:
            return
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            # "="-Zeichen in der Gleichung anklicken → Lösung!
            if self._equals_rect and self._equals_rect.collidepoint(event.pos):
                self._solve()
                return
            # Antwort-Buttons → Fallen!
            for btn in self._ANSWER_BUTTONS:
                rect = self._get_button_rect(btn)
                if rect.collidepoint(event.pos):
                    self._wrong()
                    self._shake.start()
                    if btn["label"] not in self._clicked_buttons:
                        self._clicked_buttons.append(btn["label"])
                    return

    def update(self, dt: float) -> None:
        self._shake.update(dt)
        self._wobble_timer += dt

    def draw(self, surface: pygame.Surface, area: pygame.Rect) -> None:
        w, h = area.width, area.height
        ox, oy = area.x, area.y
        surface.fill(COLOR_BG, area)

        # Tafel-Hintergrund
        board_rect = pygame.Rect(ox + 60, oy + 110, w - 120, 140)
        pygame.draw.rect(surface, (50, 90, 70), board_rect, border_radius=16)
        pygame.draw.rect(surface, (35, 65, 50), board_rect, 4, border_radius=16)

        # Kreide-Linie
        for i in range(0, board_rect.width, 8):
            if (i // 8) % 3 == 0:
                pygame.draw.line(surface, (200, 200, 180),
                                 (board_rect.x + i, board_rect.bottom - 6),
                                 (board_rect.x + i + 5, board_rect.bottom - 6), 1)

        # Gleichung auf der Tafel
        font_eq = get_font(54)
        parts = [
            ("1", (230, 230, 200)),
            (" + ", (200, 200, 180)),
            ("2", (230, 230, 200)),
            (" + ", (200, 200, 180)),
            ("3", (230, 230, 200)),
            (" ", (200, 200, 180)),
            ("=", (255, 230, 100)),   # Hervorgehoben!
            (" ?", (200, 200, 180)),
        ]

        total_w = sum(font_eq.size(p[0])[0] for p in parts)
        x = board_rect.centerx - total_w // 2
        y = board_rect.centery - font_eq.get_height() // 2

        for text, color in parts:
            surf = font_eq.render(text, True, color)
            rect = surf.get_rect(topleft=(x, y))
            surface.blit(surf, rect)
            if text == "=":
                # Klick-Bereich um das "="
                self._equals_rect = rect.inflate(12, 8)
                # Pulsierender Rahmen
                import math
                pulse = abs(math.sin(self._wobble_timer * 2))
                frame_color = (255, 230, 100, int(80 + 100 * pulse))
                frame_surf = pygame.Surface(
                    (self._equals_rect.width, self._equals_rect.height), pygame.SRCALPHA
                )
                pygame.draw.rect(frame_surf, (255, 230, 100, int(80 + 100 * pulse)),
                                 frame_surf.get_rect(), 2, border_radius=4)
                surface.blit(frame_surf, self._equals_rect.topleft)
            x += surf.get_width()

        # Antwort-Buttons (Fallen)
        shake_x = int(self._shake.offset_x)
        for btn in self._ANSWER_BUTTONS:
            rect = self._get_button_rect(btn)
            is_wrong = btn["label"] in self._clicked_buttons
            color = (230, 80, 80) if is_wrong else (78, 205, 196)
            draw_rounded_rect(surface, color, rect.move(shake_x if is_wrong else 0, 0),
                              radius=16, shadow_offset=3)
            font_btn = get_font(FONT_SIZE_MD + 4)
            draw_text_centered(surface, btn["label"], font_btn, COLOR_WHITE,
                               rect.move(shake_x if is_wrong else 0, 0).center)

        # Hinweis unter Buttons
        font_sm = get_font(16)
        sub = font_sm.render("Welche Taste drückst du eigentlich...?", True, (140, 130, 120))
        surface.blit(sub, sub.get_rect(center=(ox + w // 2, oy + h - 25)))

    def _get_button_rect(self, btn: dict) -> pygame.Rect:
        from ..settings import WINDOW_WIDTH, WINDOW_HEIGHT
        cx = int(btn["pos_ratio"][0] * WINDOW_WIDTH)
        cy = int(btn["pos_ratio"][1] * WINDOW_HEIGHT)
        return pygame.Rect(cx - 50, cy - 28, 100, 56)
