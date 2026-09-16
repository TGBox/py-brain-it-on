"""
Level 23 — Das Labyrinth

Drei Etagen mit versetzten Durchgängen.
Der Ball muss geschickt von Etage zu Etage nach unten manövriert werden.
"""
from __future__ import annotations

from .base_level import BaseLevel
from ..physics.world import PhysicsWorld
from ..settings import COLOR_CORAL, COLOR_TEAL, COLOR_ORANGE, WINDOW_WIDTH, WINDOW_HEIGHT


class Level23(BaseLevel):
    LEVEL_NUMBER = 23
    TITLE = "Das Labyrinth"
    GOAL_DESCRIPTION = "Führe den Ball durch alle Etagen bis zum Eimer!"
    HINT = "Nutze kurze schräge Rampen an den Lücken, um den Ball gezielt auf die nächste Ebene zu leiten."
    BG_COLOR = (248, 244, 238)
    STAR_THRESHOLDS = (3, 5)
    SOLUTION_DESCRIPTION = "Drei präzise Umlenkbögen führen den Ball sicher durch die drei Etagen des Labyrinths direkt in den Ziel-Eimer."
    SOLUTION_STROKES = [
        [(800, 400), (950, 440), (920, 510)],
        [(400, 620), (280, 660), (320, 730)],
        [(1000, 820), (1150, 850), (1250, 860)]
    ]

    def setup(self, world: PhysicsWorld) -> None:
        W, H = WINDOW_WIDTH, WINDOW_HEIGHT
        floor_y = H - 90

        # Etage 1 (sanft nach rechts geneigt)
        world.add_static_segment((150, 300), (850, 420), color=(140, 120, 100), radius=6)
        world.add_ball((250, 260), color=COLOR_CORAL)

        # Etage 2 (sanft nach links geneigt)
        world.add_static_segment((1050, 500), (350, 640), color=COLOR_ORANGE, radius=6)

        # Etage 3 (sanft nach rechts geneigt)
        world.add_static_segment((250, 720), (1050, 840), color=(140, 120, 100), radius=6)

        # Boden und Eimer unten rechts
        world.add_static_segment((0, floor_y), (W, floor_y), color=(140, 120, 100), radius=6)
        world.add_bucket((1250, floor_y), width=180, height=120, color=COLOR_TEAL)

