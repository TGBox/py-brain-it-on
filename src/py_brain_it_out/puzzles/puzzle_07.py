"""
puzzle_07.py — Level 7: "Wer schläft?"

TRICK: ALLE Figuren schlafen. Man muss alle gleichzeitig (oder alle nacheinander
schnell) anklicken. Eigentlich: Alle 3 Figuren müssen angeklickt werden.
"""
from __future__ import annotations

import math
import pygame

from ..puzzles.base_puzzle import BasePuzzle
from ..settings import (
    COLOR_BG, COLOR_TEXT, COLOR_WHITE,
    COLOR_CORAL, COLOR_TEAL, COLOR_YELLOW,
)
from ..ui.components import get_font, draw_rounded_rect
from ..ui.animations import ShakeEffect


class Puzzle07(BasePuzzle):
    LEVEL_NUMBER = 7
    TITLE = "Level 7"
    QUESTION = "Wer schläft hier?"
    HINT = "Schau genauer hin... Schlafen vielleicht ALLE? Du musst alle antippen!"

    _FIGURES = [
        {"name": "Anna", "pos": (200, 340), "color": (255, 180, 120), "zz_offset": (30, -60)},
        {"name": "Ben",  "pos": (400, 330), "color": (150, 200, 255), "zz_offset": (35, -65)},
        {"name": "Clara","pos": (610, 340), "color": (200, 150, 220), "zz_offset": (32, -58)},
    ]

    def __init__(self, game, on_solved, on_wrong):
        super().__init__(game, on_solved, on_wrong)
        self._clicked: set[int] = set()  # Indizes der angeklickten Figuren
        self._shake = ShakeEffect()
        self._zz_timer = 0.0
        self._wrong_clicked = False

    def handle_event(self, event: pygame.event.Event) -> None:
        if self._solved:
            return
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for i, fig in enumerate(self._FIGURES):
                rect = self._get_figure_rect(fig)
                if rect.collidepoint(event.pos):
                    self._clicked.add(i)
                    break

            # Alle angeklickt?
            if len(self._clicked) >= len(self._FIGURES):
                self._solve()

    def update(self, dt: float) -> None:
        self._shake.update(dt)
        self._zz_timer += dt

    def draw(self, surface: pygame.Surface, area: pygame.Rect) -> None:
        w, h = area.width, area.height
        ox, oy = area.x, area.y
        surface.fill(COLOR_BG, area)

        # Bett-Hintergrund
        bed_rect = pygame.Rect(ox + 40, oy + 290, w - 80, 160)
        pygame.draw.rect(surface, (220, 200, 170), bed_rect, border_radius=20)
        pygame.draw.rect(surface, (200, 175, 145), bed_rect, 4, border_radius=20)
        # Kissen-Linie
        for fig in self._FIGURES:
            px = fig["pos"][0]
            pillow = pygame.Rect(px - 35, oy + 295, 70, 45)
            pygame.draw.rect(surface, (245, 240, 230), pillow, border_radius=12)
            pygame.draw.rect(surface, (220, 210, 195), pillow, 2, border_radius=12)
        # Decke
        cover_rect = pygame.Rect(ox + 40, oy + 360, w - 80, 80)
        pygame.draw.rect(surface, (180, 160, 220), cover_rect, border_radius=10)
        pygame.draw.rect(surface, (160, 140, 200), cover_rect, 3, border_radius=10)
        # Decken-Muster
        for i in range(0, w - 80, 40):
            pygame.draw.line(surface, (160, 140, 200),
                             (ox + 40 + i, oy + 360),
                             (ox + 40 + i, oy + 440), 1)

        # Figuren zeichnen
        for i, fig in enumerate(self._FIGURES):
            clicked = i in self._clicked
            self._draw_sleeping_figure(surface, fig, clicked, oy)

        # "Wähle alle" Hinweis
        clicked_count = len(self._clicked)
        font = get_font(16)
        if clicked_count == 0:
            msg = "Tippe auf die schlafenden Figuren!"
        elif clicked_count < len(self._FIGURES):
            msg = f"Noch {len(self._FIGURES) - clicked_count} weitere..."
        else:
            msg = "Alle erwischt! 🎉"
        hint_surf = font.render(msg, True, (130, 120, 110))
        surface.blit(hint_surf, hint_surf.get_rect(center=(ox + w // 2, oy + h - 25)))

        # Fortschrittsanzeige
        for i in range(len(self._FIGURES)):
            dot_x = ox + w // 2 - (len(self._FIGURES) - 1) * 20 + i * 40
            color = (80, 200, 130) if i in self._clicked else (200, 190, 180)
            pygame.draw.circle(surface, color, (dot_x, oy + h - 50), 8)

    def _draw_sleeping_figure(self, surface, fig, clicked, oy):
        px, py = fig["pos"]
        color = fig["color"]

        # Grüner Halo wenn angeklickt
        if clicked:
            halo_surf = pygame.Surface((100, 100), pygame.SRCALPHA)
            pygame.draw.circle(halo_surf, (80, 220, 130, 80), (50, 50), 45)
            surface.blit(halo_surf, (px - 50, py - 55))

        # Körper (schläft, also liegend im Bett → nur Kopf sichtbar)
        head_cy = py - 30
        pygame.draw.circle(surface, color, (px, head_cy), 30)
        pygame.draw.circle(surface, (min(color[0] + 30, 255), min(color[1] + 30, 255), min(color[2] + 30, 255)),
                           (px - 8, head_cy - 6), 10)

        # Geschlossene Augen (schläft!)
        pygame.draw.arc(surface, (60, 40, 30),
                        (px - 18, head_cy - 12, 16, 12), 0, math.pi, 3)
        pygame.draw.arc(surface, (60, 40, 30),
                        (px + 2, head_cy - 12, 16, 12), 0, math.pi, 3)

        # Lächeln
        pygame.draw.arc(surface, (200, 100, 100),
                        (px - 10, head_cy - 2, 20, 12), math.pi, 2 * math.pi, 2)

        # "Z Z Z" Animation
        zx, zy = px + fig["zz_offset"][0], oy + fig["zz_offset"][1]
        sizes = [12, 16, 20]
        offsets = [0, 18, 40]
        for j, (sz, off) in enumerate(zip(sizes, offsets)):
            t = (self._zz_timer + j * 0.5) % 2.0
            alpha = int(255 * (1 - t / 2.0)) if t < 1.5 else 0
            y_drift = -int(t * 15)
            font_z = get_font(sz)
            z_surf = font_z.render("z", True, (150, 140, 200))
            z_surf.set_alpha(alpha)
            surface.blit(z_surf, z_surf.get_rect(center=(zx + off, zy + y_drift)))

        # Name
        font_name = get_font(15)
        name_surf = font_name.render(fig["name"], True, (100, 90, 85))
        surface.blit(name_surf, name_surf.get_rect(center=(px, py + 10)))

    def _get_figure_rect(self, fig: dict) -> pygame.Rect:
        px, py = fig["pos"]
        return pygame.Rect(px - 35, py - 65, 70, 75)
