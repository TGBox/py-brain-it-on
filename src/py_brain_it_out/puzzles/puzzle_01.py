"""
puzzle_01.py — Level 1: "Welches ist das größte?"

TRICK: Nicht das größte Bild-Element anklicken, sondern das Wort "größte"
im Fragetext selbst anklicken!
"""
from __future__ import annotations

import pygame

from ..puzzles.base_puzzle import BasePuzzle
from ..settings import (
    COLOR_BG,
    COLOR_CORAL,
    COLOR_TEAL,
    COLOR_TEXT,
    COLOR_WHITE,
    COLOR_YELLOW,
)
from ..ui.components import draw_rounded_rect, draw_text_centered, get_font
from ..ui.animations import ShakeEffect, Tween, ease_out_bounce


class Puzzle01(BasePuzzle):
    LEVEL_NUMBER = 1
    TITLE = "Level 1"
    QUESTION = "Welches ist das größte?"
    HINT = "Lies die Frage nochmal genau... Das Wort 'größte' steckt in der Frage selbst!"

    # Größen der drei Formen (klein, mittel, groß)
    _SHAPES = [
        {"label": "Kreis", "size": 45, "color": COLOR_CORAL, "pos_ratio": (0.25, 0.58)},
        {"label": "Quadrat", "size": 80, "color": COLOR_TEAL, "pos_ratio": (0.5, 0.62)},
        {"label": "Dreieck", "size": 60, "color": COLOR_YELLOW, "pos_ratio": (0.75, 0.58)},
    ]

    def __init__(self, game, on_solved, on_wrong):
        super().__init__(game, on_solved, on_wrong)
        self._shake = ShakeEffect(intensity=6, duration=0.4)
        # Bouncing-Animation für falschen Klick
        self._wrong_flash_timer = 0.0
        # Rect des "größte"-Wortes in der Frage — wird beim Zeichnen gesetzt
        self._groesste_rect: pygame.Rect | None = None
        self._clicked_wrong: list[int] = []  # Indizes der falsch geklickten Formen

    def handle_event(self, event: pygame.event.Event) -> None:
        if self._solved:
            return
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            pos = event.pos
            # Prüfen, ob das Wort "größte" in der Frage geklickt wurde
            if self._groesste_rect and self._groesste_rect.collidepoint(pos):
                self._solve()
                return
            # Prüfen, ob eine der Formen geklickt wurde (falsch!)
            for i, shape in enumerate(self._SHAPES):
                shape_rect = self._get_shape_rect(shape)
                if shape_rect.collidepoint(pos):
                    self._wrong()
                    self._shake.start()
                    if i not in self._clicked_wrong:
                        self._clicked_wrong.append(i)
                    return

    def update(self, dt: float) -> None:
        self._shake.update(dt)

    def draw(self, surface: pygame.Surface, area: pygame.Rect) -> None:
        w, h = area.width, area.height
        ox, oy = area.x, area.y

        # ---- Hintergrund ----
        surface.fill(COLOR_BG, area)

        # ---- Fragetext mit hervorgehobenem "größte" ----
        font_q = get_font(30)
        # Frage in zwei Teile splitten: "Welches ist das " und "größte" und "?"
        part1 = "Welches ist das "
        part2 = "größte"
        part3 = "?"

        surf1 = font_q.render(part1, True, COLOR_TEXT)
        surf2 = font_q.render(part2, True, COLOR_CORAL)  # Hervorhebung!
        surf3 = font_q.render(part3, True, COLOR_TEXT)

        # Gesamtbreite berechnen
        total_w = surf1.get_width() + surf2.get_width() + surf3.get_width()
        start_x = ox + (w - total_w) // 2
        q_y = oy + int(h * 0.18)

        surface.blit(surf1, (start_x, q_y))
        x2 = start_x + surf1.get_width()
        surface.blit(surf2, (x2, q_y))

        # Unterstreichung für "größte" — klickbares Hinweiselement
        self._groesste_rect = pygame.Rect(
            x2 - 4, q_y - 4,
            surf2.get_width() + 8,
            surf2.get_height() + 8,
        )
        # Subtile Rahmen-Andeutung
        pygame.draw.rect(surface, (*COLOR_CORAL, 80), self._groesste_rect, 2, border_radius=4)

        x3 = x2 + surf2.get_width()
        surface.blit(surf3, (x3, q_y))

        # ---- Formen ----
        shake_offset = int(self._shake.offset_x)
        for i, shape in enumerate(self._SHAPES):
            rect = self._get_shape_rect(shape)
            rect.x += shake_offset if i in self._clicked_wrong else 0

            color = shape["color"]
            label = shape["label"]

            if label == "Kreis":
                pygame.draw.circle(surface, (0, 0, 0, 50),
                                   (rect.centerx + 3, rect.centery + 3), shape["size"])
                pygame.draw.circle(surface, color, rect.center, shape["size"])
            elif label == "Quadrat":
                shadow = rect.move(3, 3)
                pygame.draw.rect(surface, (0, 0, 0, 60), shadow, border_radius=8)
                pygame.draw.rect(surface, color, rect, border_radius=8)
            elif label == "Dreieck":
                pts = [
                    (rect.centerx, rect.top),
                    (rect.left, rect.bottom),
                    (rect.right, rect.bottom),
                ]
                shadow_pts = [(x + 3, y + 3) for x, y in pts]
                pygame.draw.polygon(surface, (0, 0, 0, 60), shadow_pts)
                pygame.draw.polygon(surface, color, pts)

            # Größen-Label
            font_lbl = get_font(18)
            lbl_surf = font_lbl.render(label, True, COLOR_TEXT)
            surface.blit(lbl_surf, lbl_surf.get_rect(center=(rect.centerx, rect.bottom + 18)))

    def _get_shape_rect(self, shape: dict) -> pygame.Rect:
        """Berechnet das umschließende Rect einer Form."""
        from ..settings import WINDOW_WIDTH, WINDOW_HEIGHT
        cx = int(shape["pos_ratio"][0] * WINDOW_WIDTH)
        cy = int(shape["pos_ratio"][1] * WINDOW_HEIGHT)
        s = shape["size"]
        return pygame.Rect(cx - s, cy - s, s * 2, s * 2)
