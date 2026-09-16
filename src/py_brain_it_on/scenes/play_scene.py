"""
scenes/play_scene.py — Haupt-Spielszene für Brain it on!

Zustandsmaschine:
  DRAWING    → Spieler zeichnet Formen (Physik pausiert)
  SIMULATING → Physik läuft, Formen eingefroren
  SUCCESS    → Ball(e) im Eimer, Erfolgs-Overlay
  FAILED     → Ball außerhalb des Spielfelds (optional, derzeit kein Timeout)
"""
from __future__ import annotations
import pymunk

import importlib
import math
import pygame

from .base_scene import BaseScene
from ..physics.world import PhysicsWorld
from ..physics.drawing import DrawingManager
from ..settings import (
    WINDOW_WIDTH, WINDOW_HEIGHT, TOTAL_LEVELS, STAR_STROKES,
    COLOR_BG, COLOR_WHITE, COLOR_CORAL, COLOR_TEAL, COLOR_GREEN,
    COLOR_YELLOW, COLOR_TEXT, COLOR_TEXT_LIGHT, COLOR_PANEL,
    FONT_SIZE_LG, FONT_SIZE_MD, FONT_SIZE_SM, FONT_SIZE_XS,
)
from ..ui.components import (
    RoundedButton, get_font, draw_rounded_rect, draw_star,
)
from ..ui.animations import Tween, ease_out_bounce, ease_out_back
from .. import save_manager

# States
STATE_DRAWING    = "drawing"
STATE_SIMULATING = "simulating"
STATE_SUCCESS    = "success"
STATE_FAILED     = "failed"

# Level-Klassen-Registry
_LEVEL_CLASSES: dict[int, type] = {}
for _i in range(1, TOTAL_LEVELS + 1):
    _mod = importlib.import_module(f".level_{_i:02d}", package="py_brain_it_on.levels")
    _cls = getattr(_mod, f"Level{_i:02d}")
    _LEVEL_CLASSES[_i] = _cls


# ---------------------------------------------------------------------------
# Haupt-Spielszene
# ---------------------------------------------------------------------------

class PlayScene(BaseScene):
    """Spielszene: Zeichnen + Physik + UI."""

    # Bereiche
    HEADER_H = 100
    TOOLBAR_H = 90   # untere Leiste mit Buttons

    def __init__(self, game, level: int) -> None:
        super().__init__(game)
        self.level_num = level
        self._level = _LEVEL_CLASSES[level]()
        self._state = STATE_DRAWING

        self._play_area = pygame.Rect(
            0, self.HEADER_H,
            WINDOW_WIDTH, WINDOW_HEIGHT - self.HEADER_H - self.TOOLBAR_H,
        )

        # Physik & Zeichnen
        self._world: PhysicsWorld | None = None
        self._drawing = DrawingManager()
        self._stroke_count = 0
        self._sim_time = 0.0
        self._success_timer = 0.0
        self._fail_timer = 0.0
        self._snapshot_strokes: list[dict] = []
        self._hovered_conn_point: tuple[float, float] | None = None

        # Animationen
        self._success_tween = Tween(0, 1, 0.5, ease_out_bounce)
        self._star_display_stars = 0
        self._star_reveal_timer = 0.0

        # Hinweis & Musterlösung
        self._show_hint = False
        self._hint_timer = 0.0
        self._failed_attempts: int = save_manager.get_failed_attempts(self.game.save_data, self.level_num)
        self._show_solution_confirm: bool = False
        self._solution_active: bool = False

        # Buttons (Toolbar)
        btn_y = WINDOW_HEIGHT - self.TOOLBAR_H + 18
        self._btn_back  = RoundedButton(
            "Zurück", pygame.Rect(30, btn_y, 140, 54),
            color=(140, 130, 125), font_size=FONT_SIZE_SM, on_click=self._on_back,
        )
        self._btn_undo  = RoundedButton(
            "Rückgängig", pygame.Rect(185, btn_y, 170, 54),
            color=(110, 130, 150), font_size=FONT_SIZE_SM, on_click=self._on_undo,
        )
        self._btn_reset = RoundedButton(
            "Ganz neu", pygame.Rect(370, btn_y, 150, 54),
            color=COLOR_CORAL, font_size=FONT_SIZE_SM, on_click=self._on_reset,
        )
        self._btn_start = RoundedButton(
            "Starten", pygame.Rect(WINDOW_WIDTH // 2 - 120, btn_y, 240, 54),
            color=COLOR_GREEN, font_size=FONT_SIZE_SM, on_click=self._on_start,
        )

        # Buttons während der Simulation
        self._btn_edit = RoundedButton(
            "Formen anpassen", pygame.Rect(WINDOW_WIDTH // 2 - 270, btn_y, 250, 54),
            color=COLOR_TEAL, font_size=FONT_SIZE_SM, on_click=self._on_edit_shapes,
        )
        self._btn_sim_reset = RoundedButton(
            "Ganz neu", pygame.Rect(WINDOW_WIDTH // 2 + 10, btn_y, 200, 54),
            color=COLOR_CORAL, font_size=FONT_SIZE_SM, on_click=self._on_reset,
        )

        self._btn_hint  = RoundedButton(
            "Tipp", pygame.Rect(WINDOW_WIDTH - 200, btn_y, 170, 54),
            color=COLOR_YELLOW, font_size=FONT_SIZE_SM, on_click=self._on_hint,
        )

        # Musterlösung Toolbar-Button (freigeschaltet nach mehreren Fehlversuchen)
        self._btn_toolbar_solution = RoundedButton(
            "Musterlösung", pygame.Rect(WINDOW_WIDTH - 425, btn_y, 210, 54),
            color=(215, 145, 35), font_size=FONT_SIZE_SM, on_click=self._on_request_solution,
        )

        # Dialog-Buttons für gescheiterten Versuch
        cx, cy = WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2
        self._btn_fail_keep = RoundedButton(
            "Mit Formen weitermachen", pygame.Rect(cx - 320, cy + 30, 300, 54),
            color=COLOR_TEAL, font_size=FONT_SIZE_SM, on_click=self._on_edit_shapes,
        )
        self._btn_fail_reset = RoundedButton(
            "Ganz neu beginnen", pygame.Rect(cx + 20, cy + 30, 290, 54),
            color=COLOR_CORAL, font_size=FONT_SIZE_SM, on_click=self._on_reset,
        )
        self._btn_fail_solution = RoundedButton(
            "Musterlösung ansehen...", pygame.Rect(cx - 190, cy + 100, 380, 54),
            color=(215, 145, 35), font_size=FONT_SIZE_SM, on_click=self._on_request_solution,
        )

        # Bestätigungs-Dialog Buttons
        self._btn_confirm_solution = RoundedButton(
            "Ja, Lösung zeigen", pygame.Rect(cx - 260, cy + 85, 240, 56),
            color=(215, 145, 35), font_size=FONT_SIZE_SM, on_click=self._apply_solution,
        )
        self._btn_cancel_solution = RoundedButton(
            "Weiter probieren", pygame.Rect(cx + 20, cy + 85, 240, 56),
            color=COLOR_TEAL, font_size=FONT_SIZE_SM, on_click=self._cancel_solution,
        )

        self._btn_next: RoundedButton | None = None

        self._reset_world()


    # ------------------------------------------------------------------
    # Scene-Lifecycle
    # ------------------------------------------------------------------

    def on_enter(self) -> None:
        self._reset_world()

    def on_exit(self) -> None:
        pass

    # ------------------------------------------------------------------
    # Event-Handling
    # ------------------------------------------------------------------

    def handle_event(self, event: pygame.event.Event) -> None:
        # Bestätigungs-Dialog für Musterlösung (höchste Priorität)
        if self._show_solution_confirm:
            self._btn_confirm_solution.handle_event(event)
            self._btn_cancel_solution.handle_event(event)
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_ESCAPE, pygame.K_n):
                    self._cancel_solution()
                elif event.key in (pygame.K_RETURN, pygame.K_SPACE, pygame.K_j, pygame.K_y):
                    self._apply_solution()
            return

        # Erfolgs-Overlay
        if self._state == STATE_SUCCESS:
            if self._btn_next:
                self._btn_next.handle_event(event)
            self._btn_back.handle_event(event)
            return

        # Fehlversuch-Overlay
        if self._state == STATE_FAILED:
            self._btn_fail_keep.handle_event(event)
            self._btn_fail_reset.handle_event(event)
            if self._failed_attempts >= 2:
                self._btn_fail_solution.handle_event(event)
            self._btn_back.handle_event(event)
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_z, pygame.K_RETURN, pygame.K_SPACE, pygame.K_e):
                    self._on_edit_shapes()
                elif event.key == pygame.K_r:
                    self._on_reset()
                elif event.key in (pygame.K_m, pygame.K_l) and self._failed_attempts >= 2:
                    self._on_request_solution()
            return

        # Hinweis schließen
        if self._show_hint and event.type in (pygame.MOUSEBUTTONDOWN, pygame.KEYDOWN):
            self._show_hint = False
            return

        self._btn_back.handle_event(event)
        self._btn_hint.handle_event(event)

        if self._state == STATE_DRAWING:
            self._btn_undo.handle_event(event)
            self._btn_reset.handle_event(event)
            self._btn_start.handle_event(event)
            if self._failed_attempts >= 2:
                self._btn_toolbar_solution.handle_event(event)

            # Tastatur-Kürzel
            if event.type == pygame.KEYDOWN:
                if (event.key == pygame.K_z and (event.mod & pygame.KMOD_CTRL)) or event.key == pygame.K_u:
                    self._on_undo()
                    return
                elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                    self._on_start()
                    return
                elif event.key == pygame.K_r:
                    self._on_reset()
                    return
                elif event.key in (pygame.K_m, pygame.K_l) and self._failed_attempts >= 2:
                    self._on_request_solution()
                    return


            # Zeichnen oder Verbindungspunkt lösen (nur im Spielbereich)
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self._play_area.collidepoint(event.pos):
                    # Verbindungspunkt lösen bei Klick darauf
                    if self._world.remove_connection_point_at(event.pos, threshold=24.0):
                        return
                    self._drawing.start(event.pos)
            elif event.type == pygame.MOUSEMOTION:
                if self._drawing.is_drawing:
                    self._drawing.add_point(event.pos)
            elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                if self._drawing.is_drawing:
                    pts = self._drawing.finish()
                    if pts:
                        self._world.add_drawn_stroke(pts, color=(65, 58, 50))
                        self._stroke_count += 1

        elif self._state == STATE_SIMULATING:
            self._btn_edit.handle_event(event)
            self._btn_sim_reset.handle_event(event)

            # Tastatur-Kürzel
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_z, pygame.K_SPACE, pygame.K_RETURN, pygame.K_e):
                    self._on_edit_shapes()
                    return
                elif event.key == pygame.K_r:
                    self._on_reset()
                    return

    # ------------------------------------------------------------------
    # Update
    # ------------------------------------------------------------------

    def update(self, dt: float) -> None:
        if self._show_solution_confirm:
            self._btn_confirm_solution.update(dt)
            self._btn_cancel_solution.update(dt)
            return

        self._btn_back.update(dt)
        self._btn_hint.update(dt)

        if self._show_hint:
            self._hint_timer -= dt
            if self._hint_timer <= 0:
                self._show_hint = False

        if self._state == STATE_DRAWING:
            self._btn_undo.update(dt)
            self._btn_reset.update(dt)
            self._btn_start.update(dt)
            if self._failed_attempts >= 2:
                self._btn_toolbar_solution.update(dt)

            # Hover über Verbindungspunkten prüfen
            mx, my = pygame.mouse.get_pos()
            if self._play_area.collidepoint((mx, my)) and self._world:
                self._hovered_conn_point = self._world.get_connection_point_at((mx, my), threshold=24.0)
            else:
                self._hovered_conn_point = None

        elif self._state == STATE_SIMULATING:
            self._hovered_conn_point = None
            self._btn_edit.update(dt)
            self._btn_sim_reset.update(dt)
            self._sim_time += dt
            self._world.step(dt)

            # Sieg über Level-Prüfung testen
            if self._level.check_victory(self._world, dt):
                self._success_timer += dt
                if self._success_timer >= 0.5:   # kurz stabil halten
                    self._on_success()
            else:
                self._success_timer = 0.0
                if self._check_failure(dt):
                    self._state = STATE_FAILED
                    self._record_failure()

        elif self._state == STATE_FAILED:
            self._hovered_conn_point = None
            self._btn_fail_keep.update(dt)
            self._btn_fail_reset.update(dt)
            if self._failed_attempts >= 2:
                self._btn_fail_solution.update(dt)

        elif self._state == STATE_SUCCESS:
            self._hovered_conn_point = None
            self._success_tween.update(dt)
            self._star_reveal_timer += dt
            if self._btn_next:
                self._btn_next.update(dt)


    # ------------------------------------------------------------------
    # Draw
    # ------------------------------------------------------------------

    def draw(self, surface: pygame.Surface) -> None:
        # Hintergrund
        surface.fill(self._level.BG_COLOR)

        # Level-spezifischer Hintergrund
        self._level.draw_background(surface, self._play_area)

        # Trennlinie Spielbereich
        pygame.draw.line(surface, (200, 192, 180), (0, self.HEADER_H), (WINDOW_WIDTH, self.HEADER_H), 2)
        pygame.draw.line(
            surface, (200, 192, 180),
            (0, WINDOW_HEIGHT - self.TOOLBAR_H),
            (WINDOW_WIDTH, WINDOW_HEIGHT - self.TOOLBAR_H), 2,
        )

        # Physik-Welt zeichnen
        if self._world:
            self._world.draw(surface, hovered_conn_point=self._hovered_conn_point)

        # Aktueller Strich (Vorschau)
        self._drawing.draw_preview(surface)

        # Musterlösung-Banner (falls aktiv)
        if self._solution_active:
            banner_rect = pygame.Rect(100, self.HEADER_H + 12, WINDOW_WIDTH - 200, 48)
            draw_rounded_rect(surface, (255, 248, 230), banner_rect, radius=12, border_color=(215, 155, 45), border_width=2)
            font_banner = get_font(FONT_SIZE_XS, bold=True)
            desc = getattr(self._level, "SOLUTION_DESCRIPTION", "Musterlösung geladen.")
            b_text = f"Musterlösung: {desc}  •  Klicke 'Starten', um sie auszuführen!"
            b_surf = font_banner.render(b_text, True, (160, 95, 20))
            surface.blit(b_surf, b_surf.get_rect(center=banner_rect.center))

        # Toolbar-Hintergrund
        toolbar_rect = pygame.Rect(0, WINDOW_HEIGHT - self.TOOLBAR_H, WINDOW_WIDTH, self.TOOLBAR_H)
        pygame.draw.rect(surface, COLOR_WHITE, toolbar_rect)

        # Header
        self._draw_header(surface)

        # Toolbar-Buttons je nach Zustand
        self._btn_back.draw(surface)
        self._btn_hint.draw(surface)

        if self._state == STATE_DRAWING:
            self._btn_undo.draw(surface)
            self._btn_reset.draw(surface)
            self._btn_start.draw(surface)
            if self._failed_attempts >= 2:
                self._btn_toolbar_solution.draw(surface)

            # Info-Tipp: Klick auf Niete löst Verbindung
            if any(s.connection_points for s in self._world.drawn_strokes):
                font_info = get_font(FONT_SIZE_XS)
                tip_surf = font_info.render("Tipp: Klicke auf rote Niete, um Verbindungen zu lösen", True, (160, 100, 90))
                right_bound = WINDOW_WIDTH - 445 if self._failed_attempts >= 2 else WINDOW_WIDTH - 220
                surface.blit(tip_surf, tip_surf.get_rect(midright=(right_bound, WINDOW_HEIGHT - self.TOOLBAR_H // 2)))

        elif self._state == STATE_SIMULATING:
            self._btn_edit.draw(surface)
            self._btn_sim_reset.draw(surface)
            # "Physik läuft..." Anzeige
            font_sim = get_font(FONT_SIZE_SM)
            sim_surf = font_sim.render("Physik läuft...", True, COLOR_TEXT_LIGHT)
            surface.blit(sim_surf, sim_surf.get_rect(
                center=(WINDOW_WIDTH // 2 - 420, WINDOW_HEIGHT - self.TOOLBAR_H // 2)
            ))

        # Strichanzahl
        if self._state in (STATE_DRAWING, STATE_SIMULATING):
            font_strokes = get_font(FONT_SIZE_SM)
            sc_surf = font_strokes.render(f"Gezeichnete Striche: {self._stroke_count}", True, COLOR_TEXT_LIGHT)
            surface.blit(sc_surf, sc_surf.get_rect(midleft=(WINDOW_WIDTH // 2 + 150, WINDOW_HEIGHT - self.TOOLBAR_H // 2)))

        # Hinweis-Overlay
        if self._show_hint:
            self._draw_hint_overlay(surface)

        # Fehlversuch-Overlay
        if self._state == STATE_FAILED:
            self._draw_failed_overlay(surface)

        # Erfolgs-Overlay
        if self._state == STATE_SUCCESS:
            self._draw_success_overlay(surface)

        # Bestätigungs-Dialog für Musterlösung (höchste Render-Ebene)
        if self._show_solution_confirm:
            self._draw_solution_confirm_dialog(surface)


    # ------------------------------------------------------------------
    # Interne Zeichenmethoden
    # ------------------------------------------------------------------

    def _draw_header(self, surface: pygame.Surface) -> None:
        header_rect = pygame.Rect(0, 0, WINDOW_WIDTH, self.HEADER_H)
        pygame.draw.rect(surface, COLOR_WHITE, header_rect)

        # Level-Badge
        badge_rect = pygame.Rect(30, 24, 150, 52)
        draw_rounded_rect(surface, COLOR_TEAL, badge_rect, radius=12, shadow_offset=2)
        font_badge = get_font(FONT_SIZE_SM, bold=True)
        badge_surf = font_badge.render(f"Level {self.level_num}", True, COLOR_WHITE)
        surface.blit(badge_surf, badge_surf.get_rect(center=badge_rect.center))

        # Titel & Ziel
        font_title = get_font(FONT_SIZE_MD, bold=True)
        title_surf = font_title.render(self._level.TITLE, True, COLOR_TEXT)
        surface.blit(title_surf, title_surf.get_rect(center=(WINDOW_WIDTH // 2, 38)))

        font_goal = get_font(FONT_SIZE_SM)
        goal_text = getattr(self._level, "GOAL_DESCRIPTION", "Bringe den Ball in den Eimer!")
        goal_surf = font_goal.render(goal_text, True, COLOR_CORAL)
        surface.blit(goal_surf, goal_surf.get_rect(center=(WINDOW_WIDTH // 2, 74)))

        # Zustand-Indikator (Punkt oben rechts)
        state_color = {
            STATE_DRAWING: COLOR_YELLOW,
            STATE_SIMULATING: COLOR_GREEN,
            STATE_SUCCESS: COLOR_TEAL,
        }.get(self._state, COLOR_TEXT_LIGHT)
        state_label = {
            STATE_DRAWING: "Zeichnen",
            STATE_SIMULATING: "Simulation",
            STATE_SUCCESS: "Geschafft!",
        }.get(self._state, "")
        pygame.draw.circle(surface, state_color, (WINDOW_WIDTH - 210, self.HEADER_H // 2), 9)
        font_state = get_font(FONT_SIZE_SM, bold=True)
        state_surf = font_state.render(state_label, True, state_color)
        surface.blit(state_surf, state_surf.get_rect(midleft=(WINDOW_WIDTH - 190, self.HEADER_H // 2)))

    def _draw_hint_overlay(self, surface: pygame.Surface) -> None:
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 140))
        surface.blit(overlay, (0, 0))

        card_w, card_h = 680, 260
        cx, cy = WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2
        card_rect = pygame.Rect(cx - card_w // 2, cy - card_h // 2, card_w, card_h)
        draw_rounded_rect(surface, COLOR_WHITE, card_rect, radius=24, shadow_offset=8)

        font_title = get_font(FONT_SIZE_MD, bold=True)
        t_surf = font_title.render("Level-Tipp", True, COLOR_YELLOW)
        surface.blit(t_surf, t_surf.get_rect(center=(cx, cy - 65)))

        font_hint = get_font(FONT_SIZE_SM)
        # Zeilenumbruch
        words = self._level.HINT.split()
        lines, cur = [], ""
        for w in words:
            test = (cur + " " + w).strip()
            if font_hint.size(test)[0] < card_w - 60:
                cur = test
            else:
                if cur:
                    lines.append(cur)
                cur = w
        if cur:
            lines.append(cur)

        y = cy - 10
        for line in lines:
            ls = font_hint.render(line, True, COLOR_TEXT)
            surface.blit(ls, ls.get_rect(center=(cx, y)))
            y += font_hint.get_height() + 6

        font_xs = get_font(FONT_SIZE_XS)
        close_s = font_xs.render("Klicke irgendwo zum Schließen", True, COLOR_TEXT_LIGHT)
        surface.blit(close_s, close_s.get_rect(center=(cx, card_rect.bottom - 26)))

    def _draw_failed_overlay(self, surface: pygame.Surface) -> None:
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 160))
        surface.blit(overlay, (0, 0))

        has_solution = self._failed_attempts >= 2
        card_w, card_h = 780, (410 if has_solution else 320)
        cx, cy = WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2
        card_rect = pygame.Rect(cx - card_w // 2, cy - card_h // 2, card_w, card_h)
        draw_rounded_rect(surface, COLOR_WHITE, card_rect, radius=26, shadow_offset=10)

        font_title = get_font(FONT_SIZE_LG, bold=True)
        t_surf = font_title.render("Versuch nicht geglückt", True, COLOR_CORAL)
        surface.blit(t_surf, t_surf.get_rect(center=(cx, cy - (125 if has_solution else 80))))

        font_msg = get_font(FONT_SIZE_SM)
        m1_surf = font_msg.render("Der Ball hat das Ziel nicht erreicht.", True, COLOR_TEXT)
        surface.blit(m1_surf, m1_surf.get_rect(center=(cx, cy - (75 if has_solution else 30))))

        font_sub = get_font(FONT_SIZE_SM)
        sub_text = (
            "Möchtest du die Formen anpassen, neu beginnen oder die Musterlösung ansehen?"
            if has_solution else
            "Möchtest du die gezeichneten Formen anpassen oder ganz neu beginnen?"
        )
        m2_surf = font_sub.render(sub_text, True, COLOR_TEXT_LIGHT)
        surface.blit(m2_surf, m2_surf.get_rect(center=(cx, cy - (40 if has_solution else 2))))

        btn_y1 = cy + (15 if has_solution else 45)
        self._btn_fail_keep.rect.center = (cx - 165, btn_y1)
        self._btn_fail_reset.rect.center = (cx + 165, btn_y1)
        self._btn_fail_keep.draw(surface)
        self._btn_fail_reset.draw(surface)

        if has_solution:
            self._btn_fail_solution.rect.center = (cx, cy + 95)
            self._btn_fail_solution.draw(surface)

    def _draw_solution_confirm_dialog(self, surface: pygame.Surface) -> None:
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        surface.blit(overlay, (0, 0))

        card_w, card_h = 760, 360
        cx, cy = WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2
        card_rect = pygame.Rect(cx - card_w // 2, cy - card_h // 2, card_w, card_h)
        draw_rounded_rect(surface, COLOR_WHITE, card_rect, radius=26, shadow_offset=12)

        font_title = get_font(FONT_SIZE_LG, bold=True)
        t_surf = font_title.render("Musterlösung anzeigen?", True, (215, 145, 35))
        surface.blit(t_surf, t_surf.get_rect(center=(cx, cy - 100)))

        font_msg = get_font(FONT_SIZE_SM)
        m1_surf = font_msg.render("Möchtest du dir die Musterlösung für dieses Level ansehen?", True, COLOR_TEXT)
        surface.blit(m1_surf, m1_surf.get_rect(center=(cx, cy - 45)))

        font_sub = get_font(FONT_SIZE_XS)
        m2_surf = font_sub.render("Das selbstständige Lösen macht am meisten Spaß,", True, COLOR_TEXT_LIGHT)
        m3_surf = font_sub.render("aber die Musterlösung zeigt dir einen zuverlässigen physikalischen Lösungsweg.", True, COLOR_TEXT_LIGHT)
        surface.blit(m2_surf, m2_surf.get_rect(center=(cx, cy - 15)))
        surface.blit(m3_surf, m3_surf.get_rect(center=(cx, cy + 10)))

        self._btn_confirm_solution.draw(surface)
        self._btn_cancel_solution.draw(surface)


    def _draw_success_overlay(self, surface: pygame.Surface) -> None:
        scale = self._success_tween.value

        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
        alpha = min(180, int(180 * scale))
        overlay.fill((0, 0, 0, alpha))
        surface.blit(overlay, (0, 0))

        card_w, card_h = 640, 420
        cx, cy = WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2
        cw = int(card_w * min(1.0, scale * 1.5))
        ch = int(card_h * min(1.0, scale * 1.5))
        card_rect = pygame.Rect(cx - cw // 2, cy - ch // 2, cw, ch)
        draw_rounded_rect(surface, COLOR_WHITE, card_rect, radius=28, shadow_offset=12)

        if scale > 0.4:
            font_big = get_font(FONT_SIZE_LG, bold=True)
            ok_surf = font_big.render("Geschafft!", True, COLOR_GREEN)
            surface.blit(ok_surf, ok_surf.get_rect(center=(cx, cy - 120)))

            # Sterne zeichnen
            star_r = 38
            spacing = int(star_r * 2.8)
            star_y = cy - 30
            for i in range(3):
                sx = cx - spacing + i * spacing
                filled = i < self._star_display_stars and self._star_reveal_timer > i * 0.3 + 0.2
                draw_star(surface, (sx, star_y), star_r, filled=filled)

            font_sm = get_font(FONT_SIZE_MD, bold=True)
            labels = ["Gut gemacht!", "Klasse gelöst!", "Perfekt gemeistert!"]
            lbl = labels[self._star_display_stars - 1] if self._star_display_stars > 0 else ""
            lbl_surf = font_sm.render(lbl, True, COLOR_TEXT)
            surface.blit(lbl_surf, lbl_surf.get_rect(center=(cx, cy + 45)))

            # Strich-Info
            thresholds = getattr(self._level, "STAR_THRESHOLDS", (1, 3))
            font_info = get_font(FONT_SIZE_SM)
            stroke_info = font_info.render(
                f"{self._stroke_count} Strich(e) verwendet (3 Sterne: ≤{thresholds[0]}, 2 Sterne: ≤{thresholds[1]})",
                True, COLOR_TEXT_LIGHT
            )
            surface.blit(stroke_info, stroke_info.get_rect(center=(cx, cy + 85)))

            # Weiter-Button
            if self._star_reveal_timer > 0.8 and self._btn_next:
                self._btn_next.draw(surface)
            self._btn_back.draw(surface)

    # ------------------------------------------------------------------
    # Actions
    # ------------------------------------------------------------------

    def _on_start(self) -> None:
        """Starte die Physik-Simulation."""
        if self._state != STATE_DRAWING:
            return
        # Snapshot der gezeichneten Formen sichern, falls der Versuch scheitert
        if self._world:
            self._snapshot_strokes = [
                {
                    "points": list(s.points),
                    "is_static": s.is_static,
                    "connection_points": list(s.connection_points),
                    "color": s.color,
                }
                for s in self._world.drawn_strokes
            ]
        self._state = STATE_SIMULATING
        self._sim_time = 0.0
        self._fail_timer = 0.0

    def _on_undo(self) -> None:
        """Macht den zuletzt gezeichneten Strich rückgängig."""
        if self._state != STATE_DRAWING or not self._world:
            return
        removed = self._world.pop_drawn_stroke()
        if removed:
            self._stroke_count = max(0, self._stroke_count - 1)

    def _on_edit_shapes(self) -> None:
        """Setzt Bälle/Physik zurück und behält die gezeichneten Formen zum Weiterarbeiten bei."""
        if self._state == STATE_SIMULATING and self._sim_time >= 1.5:
            self._record_failure()
        self._restore_snapshot_strokes()

    def _on_reset(self) -> None:
        """Setzt das Level komplett neu auf (alle Striche werden gelöscht)."""
        if self._state == STATE_SIMULATING and self._sim_time >= 1.5:
            self._record_failure()
        self._snapshot_strokes = []
        self._solution_active = False
        self._reset_world()

    def _on_hint(self) -> None:
        self._show_hint = not self._show_hint
        if self._show_hint:
            self._hint_timer = 12.0

    def _record_failure(self) -> None:
        """Zählt einen Fehlversuch und speichert diesen ab."""
        self._failed_attempts = save_manager.record_failure(self.game.save_data, self.level_num)

    def _on_request_solution(self) -> None:
        """Öffnet den Bestätigungs-Dialog für die Musterlösung."""
        self._show_solution_confirm = True

    def _cancel_solution(self) -> None:
        """Schließt den Bestätigungs-Dialog ohne die Lösung zu laden."""
        self._show_solution_confirm = False

    def _apply_solution(self) -> None:
        """Lädt die Musterlösung für das aktuelle Level und bereitet sie zum Ausführen vor."""
        self._show_solution_confirm = False
        self._reset_world()
        self._solution_active = True
        strokes = self._level.get_solution_strokes()
        if self._world and strokes:
            for st in strokes:
                # Musterlösung erhält edle Bernstein/Gold-Färbung
                self._world.add_drawn_stroke(st, color=(205, 140, 30))
            self._stroke_count = len(self._world.drawn_strokes)
            self._snapshot_strokes = [
                {
                    "points": list(s.points),
                    "is_static": s.is_static,
                    "connection_points": list(s.connection_points),
                    "color": s.color,
                }
                for s in self._world.drawn_strokes
            ]
        self._state = STATE_DRAWING


    def _restore_snapshot_strokes(self) -> None:
        """Stellt die gezeichneten Formen vor der Simulation wieder her."""
        self._reset_world()
        if not self._snapshot_strokes or not self._world:
            return

        from ..physics.world import DrawnStroke, SEGMENT_RADIUS, WALL_ELASTICITY, WALL_FRICTION, CTYPE_DRAWN
        for stroke_data in self._snapshot_strokes:
            pts = stroke_data["points"]
            conn_pts = stroke_data["connection_points"]
            is_static = stroke_data["is_static"]
            color = stroke_data.get("color", (80, 70, 65))

            if is_static and conn_pts:
                body = pymunk.Body(body_type=pymunk.Body.STATIC)
                segments = []
                for i in range(len(pts) - 1):
                    seg = pymunk.Segment(body, pts[i], pts[i + 1], SEGMENT_RADIUS)
                    seg.elasticity = WALL_ELASTICITY
                    seg.friction = WALL_FRICTION
                    seg.collision_type = CTYPE_DRAWN
                    segments.append(seg)
                self._world.space.add(body, *segments)
                self._world._level_static_shapes.extend(segments)
                stroke = DrawnStroke(
                    points=pts,
                    segments=segments,
                    body=body,
                    color=color,
                    is_static=True,
                    connection_points=conn_pts,
                )
                self._world.drawn_strokes.append(stroke)
            else:
                self._world.add_drawn_stroke(pts, color=color)

        self._stroke_count = len(self._world.drawn_strokes)

    def _check_failure(self, dt: float) -> bool:
        """Prüft, ob der Ball verloren gegangen ist oder die Bewegung erloschen ist."""
        if not self._world or not self._world.balls:
            return False

        # 1. Ball außerhalb des sichtbaren Feldes
        for ball in self._world.balls:
            pos = ball.body.position
            if pos.y > WINDOW_HEIGHT + 70 or pos.x < -120 or pos.x > WINDOW_WIDTH + 120:
                return True

        # 2. Wenn mindestens 3.5s simuliert wurden und alle Bälle stillstehen
        if self._sim_time > 3.5:
            all_stopped = all(b.body.velocity.length < 15.0 for b in self._world.balls)
            if all_stopped and not self._level.check_victory(self._world, dt):
                self._fail_timer += dt
                if self._fail_timer >= 1.0:
                    return True
            else:
                self._fail_timer = 0.0
        return False

    def _on_success(self) -> None:
        if self._state == STATE_SUCCESS:
            return
        self._state = STATE_SUCCESS
        self._solution_active = False
        self._success_tween = Tween(0, 1, 0.55, ease_out_bounce)
        self._star_reveal_timer = 0.0


        # Sternebewertung
        thresh = getattr(self._level, "STAR_THRESHOLDS", (1, 3))
        if self._stroke_count <= thresh[0]:
            self._star_display_stars = 3
        elif self._stroke_count <= thresh[1]:
            self._star_display_stars = 2
        else:
            self._star_display_stars = 1

        # Fortschritt speichern
        self.game.save_data = save_manager.save_level_result(
            self.game.save_data, self.level_num, self._star_display_stars
        )
        save_manager.save(self.game.save_data)

        # Weiter-Button aufbauen
        cx, cy = WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2
        if self.level_num < TOTAL_LEVELS:
            label = "Nächstes Level"
            action = self._on_next_level
        else:
            label = "Alle Level gemeistert!"
            action = self._on_back_to_menu
        self._btn_next = RoundedButton(
            label,
            pygame.Rect(cx - 150, cy + 125, 300, 58),
            color=COLOR_CORAL,
            font_size=FONT_SIZE_SM,
            on_click=action,
        )

    def _on_back(self) -> None:
        self.game.pop_scene()

    def _on_next_level(self) -> None:
        self.game.pop_scene()
        self.game.push_scene(PlayScene(self.game, self.level_num + 1))

    def _on_back_to_menu(self) -> None:
        while len(self.game.scene_stack) > 1:
            self.game.pop_scene()

    # ------------------------------------------------------------------
    # Hilfsmethoden
    # ------------------------------------------------------------------

    def _reset_world(self) -> None:
        """Erstellt eine frische Physik-Welt mit dem Level-Setup."""
        self._world = PhysicsWorld()
        self._level.setup(self._world)
        self._drawing.cancel()
        self._stroke_count = 0
        self._sim_time = 0.0
        self._success_timer = 0.0
        self._state = STATE_DRAWING
        self._show_hint = False

    def _check_ball_oob(self) -> None:
        """Prüft, ob Bälle aus dem Spielfeld gefallen sind."""
        for ball in self._world.balls:
            pos = ball.body.position
            # Weit unterhalb des Spielfelds → Reset-Hinweis
            if pos.y > WINDOW_HEIGHT + 100:
                pass  # Ball kommt durch Border-Wall nicht raus, aber sicher ist sicher
