"""
Level 12 — Das Labyrinth

Drei Etagen mit versetzten Durchgängen.
Der Ball muss geschickt von Etage zu Etage nach unten manövriert werden.
"""
from __future__ import annotations

from .base_level import BaseLevel
from ..physics.world import PhysicsWorld
from ..settings import COLOR_CORAL, COLOR_TEAL, COLOR_ORANGE, WINDOW_WIDTH, WINDOW_HEIGHT


class Level12(BaseLevel):
    LEVEL_NUMBER = 12
    TITLE = "Das Labyrinth"
    GOAL_DESCRIPTION = "Führe den Ball durch alle Etagen bis zum Eimer!"
    HINT = "Nutze kurze schräge Rampen an den Lücken, um den Ball gezielt auf die nächste Ebene zu leiten."
    BG_COLOR = (248, 244, 238)
    STAR_THRESHOLDS = (1, 3)

    def setup(self, world: PhysicsWorld) -> None:
        W, H = WINDOW_WIDTH, WINDOW_HEIGHT
        floor_y = H - 90

        # Etage 1 (Öffnung rechts)
        world.add_static_segment((100, 280), (1450, 280), color=(140, 120, 100), radius=6)
        world.add_ball((250, 230), color=COLOR_CORAL)

        # Etage 2 (Öffnung links)
        world.add_static_segment((450, 520), (1820, 520), color=COLOR_ORANGE, radius=6)

        # Etage 3 (Öffnung rechts)
        world.add_static_segment((100, 760), (1450, 760), color=(140, 120, 100), radius=6)

        # Boden und Eimer unten links
        world.add_static_segment((0, floor_y), (W, floor_y), color=(140, 120, 100), radius=6)
        world.add_bucket((350, floor_y), width=160, height=120, color=COLOR_TEAL)
