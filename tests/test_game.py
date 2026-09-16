"""
Regression test suite for py-brain-it-on
"""
import os
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

os.environ["SDL_VIDEODRIVER"] = "dummy"

import pygame
pygame.init()

from py_brain_it_on.settings import TOTAL_LEVELS, WINDOW_WIDTH, WINDOW_HEIGHT
from py_brain_it_on.physics.world import PhysicsWorld
from py_brain_it_on.game import Game
from py_brain_it_on.scenes.menu_scene import MenuScene
from py_brain_it_on.scenes.level_select import LevelSelectScene
from py_brain_it_on.scenes.play_scene import PlayScene


def test_levels():
    assert TOTAL_LEVELS == 25, f"Expected 25 levels, got {TOTAL_LEVELS}"
    surface = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))

    for i in range(1, TOTAL_LEVELS + 1):
        mod_name = f"py_brain_it_on.levels.level_{i:02d}"
        cls_name = f"Level{i:02d}"
        __import__(mod_name)
        mod = sys.modules[mod_name]
        cls = getattr(mod, cls_name)
        level = cls()

        assert level.LEVEL_NUMBER == i
        assert len(level.TITLE) > 0
        assert len(level.GOAL_DESCRIPTION) > 0
        assert len(level.HINT) > 0

        world = PhysicsWorld()
        level.setup(world)

        for _ in range(5):
            world.step(1.0 / 60.0)

        res = level.check_victory(world, 1.0 / 60.0)
        assert isinstance(res, (bool, int))
        world.draw(surface)


def test_scenes():
    game = Game()
    surface = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))

    menu = MenuScene(game)
    menu.update(0.016)
    menu.draw(surface)

    lvl_select = LevelSelectScene(game)
    lvl_select.update(0.016)
    lvl_select.draw(surface)

    play = PlayScene(game, 1)
    play.update(0.016)
    play.draw(surface)


def test_dynamic_stroke_physics():
    world = PhysicsWorld()
    world.add_static_segment((0, 1000), (1920, 1000))

    stroke = world.add_drawn_stroke([(400, 300), (600, 300)])
    assert not stroke.is_static
    assert stroke.body is not None

    initial_y = stroke.body.position.y
    for _ in range(60):
        world.step(1.0 / 60.0)

    final_y = stroke.body.position.y
    assert final_y > initial_y + 100

    anchored_stroke = world.add_drawn_stroke([(0, 1000), (200, 950)])
    assert anchored_stroke.is_static
    # Test closed shape (polygon) mass scaling
    open_line = world.add_drawn_stroke([(100, 100), (300, 100)])
    closed_box = world.add_drawn_stroke([(100, 100), (300, 100), (300, 300), (100, 300), (100, 100)])
    assert closed_box.is_closed, "Box should be recognized as closed"
    assert len(closed_box.poly_shapes) > 0, "Closed box should have poly_shapes"
    assert closed_box.body.mass > open_line.body.mass * 5, "Closed box must have much higher mass than open line"


def test_drawing_manager_close():
    from py_brain_it_on.physics.drawing import DrawingManager
    dm = DrawingManager()
    dm.start((100, 100))
    dm.add_point((200, 100))
    dm.add_point((200, 200))
    dm.add_point((100, 200))
    pts = dm.close_and_finish()
    assert pts is not None
    assert pts[0] == pts[-1], "Explicit close must set end point to start point"


def test_reset_and_connections():
    from py_brain_it_on import save_manager
    # Test reset
    fresh = save_manager.reset()
    assert fresh["levels"]["1"]["stars"] == 0
    assert not fresh["levels"]["2"]["solved"]

    # Test connection points on arbitrary static platforms
    world = PhysicsWorld()
    # Add floating platform
    world.add_static_segment((500, 500), (800, 500))

    # Stroke touching platform at (600, 505)
    stroke = world.add_drawn_stroke([(600, 505), (600, 700)])
    assert stroke.is_static, "Stroke touching platform should be static"
    assert len(stroke.connection_points) > 0, "Stroke touching platform should have connection points"

    # Air stroke
    air_stroke = world.add_drawn_stroke([(100, 100), (200, 100)])
    assert not air_stroke.is_static, "Free-floating stroke should be dynamic"
    assert len(air_stroke.connection_points) == 0


def test_reference_solutions():
    """Prüft, dass alle 25 Level eine Musterlösung besitzen, die Sterne-Grenzwerte stimmen und die Lösung physikalisch gewinnt."""
    for i in range(1, TOTAL_LEVELS + 1):
        mod_name = f"py_brain_it_on.levels.level_{i:02d}"
        cls_name = f"Level{i:02d}"
        mod = sys.modules[mod_name]
        cls = getattr(mod, cls_name)
        level = cls()

        assert hasattr(level, "SOLUTION_DESCRIPTION") and len(level.SOLUTION_DESCRIPTION) > 0, (
            f"Level {i} fehlt SOLUTION_DESCRIPTION"
        )
        strokes = level.get_solution_strokes()
        assert len(strokes) > 0, f"Level {i} hat keine SOLUTION_STROKES"

        N = len(strokes)
        assert level.STAR_THRESHOLDS == (N, N + 2), (
            f"Level {i:02d} ({level.TITLE}) STAR_THRESHOLDS {level.STAR_THRESHOLDS} != ({N}, {N + 2})"
        )

        world = PhysicsWorld()
        level.setup(world)
        for st in strokes:
            world.add_drawn_stroke(st)

        won = False
        for step in range(500):
            world.step(1.0 / 60.0)
            if level.check_victory(world, 1.0 / 60.0):
                won = True
                break
        assert won, f"Level {i:02d} ({level.TITLE}) Musterlösung gewinnt die Physiksimulation nicht!"


def test_musterloesung_flow():
    """Testet das Freischalten und Anwenden der Musterlösung nach Fehlversuchen."""
    from py_brain_it_on import save_manager
    game = Game()
    # Level 1 PlayScene mit 0 Fehlversuchen
    save_manager.reset()
    play = PlayScene(game, 1)
    assert play._failed_attempts == 0
    assert not play._show_solution_confirm

    # Nach 2 Fehlversuchen wird die Musterlösung freigeschaltet
    play._record_failure()
    assert play._failed_attempts == 1
    play._record_failure()
    assert play._failed_attempts == 2

    # Klick auf Musterlösung öffnet Bestätigungsdialog
    play._on_request_solution()
    assert play._show_solution_confirm

    # Abbrechen
    play._cancel_solution()
    assert not play._show_solution_confirm

    # Erneut öffnen und bestätigen
    play._on_request_solution()
    play._apply_solution()
    assert not play._show_solution_confirm
    assert play._solution_active
    assert play._stroke_count > 0

    # Starten der Musterlösung
    play._on_start()
    assert play._state == "simulating"


if __name__ == "__main__":
    test_levels()
    test_scenes()
    test_dynamic_stroke_physics()
    test_drawing_manager_close()
    test_reset_and_connections()
    test_reference_solutions()
    test_musterloesung_flow()
    print("All tests passed!")

