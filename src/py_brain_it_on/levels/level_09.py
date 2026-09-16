"""
Level 9 — Kettenreaktion

Ein schweres Gewicht ruht oben auf einer Rampe hinter einem Stopper.
Der Ball liegt auf einer Plattform in der Spielfeldmitte.
Ziel: Nutze das schwere Gewicht, um den Ball mit Schwung in den Eimer zu stoßen!
"""
from __future__ import annotations

from .base_level import BaseLevel
from ..physics.world import PhysicsWorld
from ..settings import COLOR_CORAL, COLOR_TEAL, WINDOW_WIDTH, WINDOW_HEIGHT


class Level09(BaseLevel):
    LEVEL_NUMBER = 9
    TITLE = "Kettenreaktion"
    GOAL_DESCRIPTION = "Nutze das schwere Gewicht, um den Ball in den Eimer zu stoßen!"
    HINT = "Baue eine Brücke über den Stopper, damit das schwere Gewicht nach unten saust und den Ball anstößt."
    BG_COLOR = (245, 242, 236)
    STAR_THRESHOLDS = (2, 4)
    SOLUTION_DESCRIPTION = "Kettenreaktion: Eine Brücke leitet das schwere Gewicht über den Stopper, sodass es den Ball mit voller Wucht in den Eimer stößt."
    SOLUTION_STROKES = [
        [(280, 290), (440, 340), (650, 500), (840, 580)],
        [(1140, 620), (1350, 750), (1550, 880)],
    ]

    def setup(self, world: PhysicsWorld) -> None:
        W, H = WINDOW_WIDTH, WINDOW_HEIGHT
        floor_y = H - 90

        # Boden
        world.add_static_segment((0, floor_y), (W, floor_y), color=(140, 120, 100), radius=6)

        # Obere Rampe mit Stopper für das schwere Gewicht
        world.add_static_segment((150, 250), (450, 420), color=(140, 120, 100), radius=6)
        world.add_static_segment((450, 420), (450, 380), color=(140, 120, 100), radius=6)

        # Schweres Gewicht (Bronze-Kugel, 8 kg)
        b_heavy = world.add_ball((330, 310), color=(130, 90, 60))
        b_heavy.body.mass = 8.0

        # Plattform in der Mitte mit Zielball
        world.add_static_segment((650, 620), (1200, 620), color=(140, 120, 100), radius=6)
        world.add_ball((900, 570), color=COLOR_CORAL)

        # Eimer unten rechts
        world.add_bucket((1600, floor_y), width=160, height=120, color=COLOR_TEAL)

    def check_victory(self, world: PhysicsWorld, dt: float = 0.0) -> bool:
        # Nur der Zielball (Ball 1) muss im Eimer sein
        if len(world.balls) > 1:
            return world.balls[1].in_bucket
        return world.all_balls_in_bucket
