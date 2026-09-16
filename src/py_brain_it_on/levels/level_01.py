"""
Level 1 — Tutorial: Die Rutsche

Ball liegt oben links auf einer Plattform.
Eimer steht unten rechts auf einem Podest.
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
    TITLE = "Tutorial: Die Rutsche"
    GOAL_DESCRIPTION = "Bringe den Ball in den Eimer!"
    HINT = "Zeichne eine schräge Rampe von der Plattform hinab zum Eimer."
    BG_COLOR = (248, 243, 235)
    STAR_THRESHOLDS = (1, 3)
    SOLUTION_DESCRIPTION = "Geschwungene Rutschbahn von der Plattform direkt in den Eimer."
    SOLUTION_STROKES = [
        [(250, 260), (310, 360), (800, 520), (1400, 710), (1540, 750)]
    ]

    def setup(self, world: PhysicsWorld) -> None:
        W, H = WINDOW_WIDTH, WINDOW_HEIGHT

        # Bodenlinie
        world.add_static_segment((0, H - 90), (W, H - 90), color=(140, 120, 100), radius=6)

        # Ball oben links auf einer Plattform
        world.add_static_segment((150, 360), (500, 360), color=(140, 120, 100), radius=6)
        world.add_ball((320, 310), color=COLOR_CORAL)

        # Eimer-Podest unten rechts
        world.add_static_segment((1350, 880), (1800, 880), color=(140, 120, 100), radius=6)
        world.add_bucket((1580, 880), width=150, height=120, color=COLOR_TEAL)

    def draw_background(self, surface: pygame.Surface, area: pygame.Rect) -> None:
        font = get_font(28)
        hint = font.render("Zeichne eine Rampe mit der Maus!", True, (170, 160, 150))
        surface.blit(hint, hint.get_rect(center=(WINDOW_WIDTH // 2, area.bottom - 40)))
