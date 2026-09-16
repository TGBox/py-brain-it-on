"""
Level 1 — Tutorial: Rampe zeichnen

Ball liegt oben links auf einer Plattform.
Eimer steht unten rechts.
Ziel: Eine Rampe zeichnen, damit der Ball in den Eimer rollt.
"""
from __future__ import annotations

import pygame

from .base_level import BaseLevel
from ..physics.world import PhysicsWorld
from ..settings import COLOR_CORAL, COLOR_TEAL, WINDOW_WIDTH, WINDOW_HEIGHT
from ..ui.components import get_font


class Level01(BaseLevel):
    LEVEL_NUMBER = 1
    TITLE = "Tutorial"
    HINT = "Zeichne eine schraege Rampe vom Ball zum Eimer hin."
    BG_COLOR = (248, 243, 235)

    def setup(self, world: PhysicsWorld) -> None:
        W, H = WINDOW_WIDTH, WINDOW_HEIGHT

        # Ball oben links auf einer Plattform
        world.add_static_segment((60, 180), (200, 180), color=(140, 120, 100), radius=5)
        world.add_ball((130, 145), color=COLOR_CORAL)

        # Eimer unten rechts
        world.add_bucket((620, 460), width=80, height=65, color=COLOR_TEAL)

        # Boden-Plattform rechts
        world.add_static_segment((480, 460), (WINDOW_WIDTH - 60, 460), color=(140, 120, 100), radius=5)

    def draw_background(self, surface: pygame.Surface, area: pygame.Rect) -> None:
        font = get_font(14)
        # Pfeil-Hint
        hint = font.render("Zeichne eine Rampe!", True, (160, 150, 140))
        surface.blit(hint, (WINDOW_WIDTH // 2 - hint.get_width() // 2, area.bottom - 30))
