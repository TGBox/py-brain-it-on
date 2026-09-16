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
    assert len(anchored_stroke.connection_points) > 0


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


if __name__ == "__main__":
    test_levels()
    test_scenes()
    test_dynamic_stroke_physics()
    test_reset_and_connections()
    print("All tests passed!")
