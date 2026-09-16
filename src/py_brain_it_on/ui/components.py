"""
components.py — Wiederverwendbare UI-Komponenten für py-brain-it-on.
"""
from __future__ import annotations

import math
from typing import Callable, Optional

import pygame

from ..settings import (
    COLOR_BLACK,
    COLOR_CORAL,
    COLOR_CORAL_DARK,
    COLOR_STAR_EMPTY,
    COLOR_STAR_FILLED,
    COLOR_TEXT,
    COLOR_TEXT_LIGHT,
    COLOR_WHITE,
    COLOR_YELLOW,
    COLOR_YELLOW_DARK,
    FONT_SIZE_MD,
    FONT_SIZE_SM,
    FONT_SIZE_XS,
)
from .animations import Tween, ease_out_back, ease_out_cubic


# ---------------------------------------------------------------------------
# Font-Helper
# ---------------------------------------------------------------------------

_font_cache: dict[tuple, pygame.font.Font] = {}


def get_font(size: int, bold: bool = False) -> pygame.font.Font:
    """Gibt einen gecachten Font zurück. Versucht Fredoka One, fällt auf System-Font zurück."""
    key = (size, bold)
    if key not in _font_cache:
        from ..settings import FONTS_DIR
        ttf_path = FONTS_DIR / "FredokaOne-Regular.ttf"
        if ttf_path.exists():
            _font_cache[key] = pygame.font.Font(str(ttf_path), size)
        else:
            # Fallback: Pygame-Systemfont mit voller Umlaut-Unterstützung
            candidates = ["segoeui", "arialrounded", "arial", "comicsansms", None]
            font = None
            for name in candidates:
                try:
                    font = pygame.font.SysFont(name, size, bold=bold)
                    break
                except Exception:
                    continue
            _font_cache[key] = font or pygame.font.Font(None, size)
    return _font_cache[key]


# ---------------------------------------------------------------------------
# Hilfsfunktionen
# ---------------------------------------------------------------------------

def draw_rounded_rect(
    surface: pygame.Surface,
    color: tuple,
    rect: pygame.Rect,
    radius: int = 16,
    shadow_offset: int = 4,
    shadow_color: tuple = (0, 0, 0, 50),
) -> None:
    """Zeichnet ein abgerundetes Rechteck mit optionalem Schatten."""
    # Schatten
    if shadow_offset > 0:
        shadow_surf = pygame.Surface(
            (rect.width + shadow_offset * 2, rect.height + shadow_offset * 2),
            pygame.SRCALPHA,
        )
        shadow_rect = pygame.Rect(shadow_offset, shadow_offset, rect.width, rect.height)
        pygame.draw.rect(shadow_surf, shadow_color, shadow_rect, border_radius=radius)
        surface.blit(shadow_surf, (rect.x - shadow_offset, rect.y - shadow_offset))
    # Hauptform
    pygame.draw.rect(surface, color, rect, border_radius=radius)


def draw_text_centered(
    surface: pygame.Surface,
    text: str,
    font: pygame.font.Font,
    color: tuple,
    center: tuple[int, int],
    shadow: bool = False,
    shadow_color: tuple = (0, 0, 0, 80),
    shadow_offset: tuple = (2, 2),
) -> pygame.Rect:
    """Zeichnet Text zentriert an einer Position mit optionalem Schatten."""
    if shadow:
        shadow_surf = font.render(text, True, shadow_color[:3])
        shadow_surf.set_alpha(shadow_color[3] if len(shadow_color) > 3 else 80)
        sr = shadow_surf.get_rect(center=(center[0] + shadow_offset[0], center[1] + shadow_offset[1]))
        surface.blit(shadow_surf, sr)
    rendered = font.render(text, True, color)
    rect = rendered.get_rect(center=center)
    surface.blit(rendered, rect)
    return rect


def draw_star(
    surface: pygame.Surface,
    center: tuple[int, int],
    radius: float,
    filled: bool,
    color_filled: tuple = COLOR_STAR_FILLED,
    color_empty: tuple = COLOR_STAR_EMPTY,
    outline_color: tuple = (200, 160, 0),
) -> None:
    """Zeichnet einen 5-zackigen Stern."""
    color = color_filled if filled else color_empty
    points = []
    outer_r = radius
    inner_r = radius * 0.42
    for i in range(10):
        angle = math.radians(-90 + i * 36)
        r = outer_r if i % 2 == 0 else inner_r
        points.append((
            center[0] + r * math.cos(angle),
            center[1] + r * math.sin(angle),
        ))
    if filled:
        pygame.draw.polygon(surface, outline_color, points)
        # leicht kleiner für Rahmen-Effekt
        inner_points = []
        for i in range(10):
            angle = math.radians(-90 + i * 36)
            r = (outer_r - 2) if i % 2 == 0 else (inner_r - 1)
            inner_points.append((center[0] + r * math.cos(angle), center[1] + r * math.sin(angle)))
        pygame.draw.polygon(surface, color, inner_points)
    else:
        pygame.draw.polygon(surface, color, points)
        pygame.draw.polygon(surface, (170, 160, 148), points, 2)


# ---------------------------------------------------------------------------
# RoundedButton
# ---------------------------------------------------------------------------

class RoundedButton:
    """Abgerundeter Button mit Hover- und Press-Animation."""

    def __init__(
        self,
        text: str,
        rect: pygame.Rect,
        color: tuple = COLOR_CORAL,
        color_hover: tuple = COLOR_CORAL_DARK,
        text_color: tuple = COLOR_WHITE,
        font_size: int = FONT_SIZE_MD,
        radius: int = 20,
        on_click: Optional[Callable] = None,
        shadow: bool = True,
    ):
        self.text = text
        self.rect = rect.copy()
        self.color = color
        self.color_hover = color_hover
        self.text_color = text_color
        self.font_size = font_size
        self.radius = radius
        self.on_click = on_click
        self.shadow = shadow

        self._hovered = False
        self._pressed = False
        self._scale = 1.0
        self._scale_tween: Optional[Tween] = None
        self._enabled = True

    @property
    def enabled(self) -> bool:
        return self._enabled

    @enabled.setter
    def enabled(self, v: bool) -> None:
        self._enabled = v

    def handle_event(self, event: pygame.event.Event) -> bool:
        """Gibt True zurück, wenn der Button geklickt wurde."""
        if not self._enabled:
            return False
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self._get_scaled_rect().collidepoint(event.pos):
                self._pressed = True
                self._scale_tween = Tween(self._scale, 0.92, 0.08, ease_out_cubic)
                return False
        if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if self._pressed and self._get_scaled_rect().collidepoint(event.pos):
                self._pressed = False
                self._scale_tween = Tween(self._scale, 1.05, 0.1, ease_out_back,
                                          on_complete=lambda: setattr(self, '_scale_tween',
                                                                       Tween(self._scale, 1.0, 0.15)))
                if self.on_click:
                    self.on_click()
                return True
            self._pressed = False
            self._scale_tween = Tween(self._scale, 1.0, 0.15)
        return False

    def update(self, dt: float) -> None:
        mouse_pos = pygame.mouse.get_pos()
        self._hovered = self._get_scaled_rect().collidepoint(mouse_pos) and self._enabled
        if self._scale_tween:
            self._scale = self._scale_tween.update(dt)
            if self._scale_tween.done:
                self._scale_tween = None

    def draw(self, surface: pygame.Surface) -> None:
        scaled_rect = self._get_scaled_rect()
        color = self.color_hover if self._hovered else self.color
        if not self._enabled:
            color = COLOR_TEXT_LIGHT
        draw_rounded_rect(
            surface, color, scaled_rect, self.radius,
            shadow_offset=4 if self.shadow else 0,
            shadow_color=(0, 0, 0, 50),
        )
        font = get_font(self.font_size)
        draw_text_centered(surface, self.text, font, self.text_color, scaled_rect.center)

    def _get_scaled_rect(self) -> pygame.Rect:
        cx, cy = self.rect.center
        w = int(self.rect.width * self._scale)
        h = int(self.rect.height * self._scale)
        return pygame.Rect(cx - w // 2, cy - h // 2, w, h)


# ---------------------------------------------------------------------------
# TextInputField
# ---------------------------------------------------------------------------

class TextInputField:
    """Einzeiliges Texteingabefeld."""

    def __init__(
        self,
        rect: pygame.Rect,
        placeholder: str = "",
        font_size: int = FONT_SIZE_SM,
        max_chars: int = 30,
        on_submit: Optional[Callable[[str], None]] = None,
    ):
        self.rect = rect.copy()
        self.placeholder = placeholder
        self.font_size = font_size
        self.max_chars = max_chars
        self.on_submit = on_submit
        self.text = ""
        self.active = False
        self._cursor_timer = 0.0
        self._cursor_visible = True

    def handle_event(self, event: pygame.event.Event) -> bool:
        """Gibt True zurück, wenn Enter gedrückt wurde."""
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.active = self.rect.collidepoint(event.pos)
        if not self.active:
            return False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN or event.key == pygame.K_KP_ENTER:
                if self.on_submit:
                    self.on_submit(self.text)
                return True
            elif event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            elif len(self.text) < self.max_chars and event.unicode.isprintable():
                self.text += event.unicode
        return False

    def update(self, dt: float) -> None:
        self._cursor_timer += dt
        if self._cursor_timer >= 0.5:
            self._cursor_timer = 0.0
            self._cursor_visible = not self._cursor_visible

    def draw(self, surface: pygame.Surface) -> None:
        # Hintergrund
        bg_color = COLOR_WHITE if self.active else (245, 240, 235)
        border_color = COLOR_CORAL if self.active else (200, 190, 180)
        pygame.draw.rect(surface, bg_color, self.rect, border_radius=12)
        pygame.draw.rect(surface, border_color, self.rect, 3, border_radius=12)

        font = get_font(self.font_size)
        if self.text:
            text_surf = font.render(self.text, True, COLOR_TEXT)
        else:
            text_surf = font.render(self.placeholder, True, COLOR_TEXT_LIGHT)

        text_x = self.rect.x + 12
        text_y = self.rect.centery - text_surf.get_height() // 2
        surface.blit(text_surf, (text_x, text_y))

        # Cursor
        if self.active and self._cursor_visible and self.text:
            cursor_x = text_x + text_surf.get_width() + 2
            pygame.draw.line(surface, COLOR_TEXT,
                             (cursor_x, self.rect.y + 8),
                             (cursor_x, self.rect.bottom - 8), 2)

    def clear(self) -> None:
        self.text = ""


# ---------------------------------------------------------------------------
# StarDisplay
# ---------------------------------------------------------------------------

class StarDisplay:
    """Animierte Anzeige von 1–3 Sternen."""

    def __init__(self, center: tuple[int, int], star_count: int = 3, radius: float = 22):
        self.center = center
        self.star_count = star_count
        self.radius = radius
        self._scales = [0.0, 0.0, 0.0]
        self._tweens: list[Optional[Tween]] = [None, None, None]
        self._revealed = 0
        self._delay_timer = 0.0
        self._animating = False

    def start_animation(self, stars: int) -> None:
        """Startet die Stern-Enthüllungsanimation."""
        self.star_count = stars
        self._scales = [0.0, 0.0, 0.0]
        self._tweens = [None, None, None]
        self._revealed = 0
        self._delay_timer = 0.0
        self._animating = True

    def update(self, dt: float) -> None:
        if self._animating and self._revealed < 3:
            self._delay_timer += dt
            if self._delay_timer >= 0.2 and self._tweens[self._revealed] is None:
                idx = self._revealed
                self._tweens[idx] = Tween(0.0, 1.0, 0.4, ease_out_back)
                self._revealed += 1
                self._delay_timer = 0.0

        for i, tween in enumerate(self._tweens):
            if tween:
                self._scales[i] = tween.update(dt)
                if tween.done:
                    self._tweens[i] = None

    def draw(self, surface: pygame.Surface) -> None:
        spacing = int(self.radius * 2.6)
        start_x = self.center[0] - spacing
        for i in range(3):
            cx = start_x + i * spacing
            cy = self.center[1]
            scale = self._scales[i] if self._animating else 1.0
            r = self.radius * scale
            if r > 0.5:
                draw_star(surface, (cx, cy), r, filled=(i < self.star_count))


# ---------------------------------------------------------------------------
# HintButton
# ---------------------------------------------------------------------------

class HintButton:
    """Glühbirnen-Button mit Hinweis-Zähler."""

    def __init__(
        self,
        pos: tuple[int, int],
        hints_left: int,
        on_click: Optional[Callable] = None,
    ):
        self.pos = pos  # Mittelpunkt
        self.hints_left = hints_left
        self.on_click = on_click
        self._radius = 28
        self._hovered = False
        self._pulse_t = 0.0

    def handle_event(self, event: pygame.event.Event) -> bool:
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.hints_left > 0:
                dx = event.pos[0] - self.pos[0]
                dy = event.pos[1] - self.pos[1]
                if dx * dx + dy * dy <= self._radius ** 2:
                    if self.on_click:
                        self.on_click()
                    return True
        return False

    def update(self, dt: float) -> None:
        self._pulse_t += dt
        mx, my = pygame.mouse.get_pos()
        dx, dy = mx - self.pos[0], my - self.pos[1]
        self._hovered = (dx * dx + dy * dy <= self._radius ** 2) and self.hints_left > 0

    def draw(self, surface: pygame.Surface) -> None:
        px, py = self.pos
        # Pulsieren wenn Hinweise verfügbar
        if self.hints_left > 0:
            pulse = 1 + 0.06 * math.sin(self._pulse_t * 3)
            r = int(self._radius * pulse)
        else:
            r = self._radius

        # Kreis-Hintergrund
        color = COLOR_YELLOW if self.hints_left > 0 else (200, 195, 185)
        # Schatten
        shadow_surf = pygame.Surface((r * 2 + 8, r * 2 + 8), pygame.SRCALPHA)
        pygame.draw.circle(shadow_surf, (0, 0, 0, 50), (r + 4, r + 4), r)
        surface.blit(shadow_surf, (px - r - 4, py - r - 4))
        pygame.draw.circle(surface, color, (px, py), r)

        if self._hovered:
            pygame.draw.circle(surface, COLOR_YELLOW_DARK, (px, py), r, 3)

        # Glühbirnen-Symbol (vereinfacht als Text)
        font = get_font(int(r * 0.9))
        icon = "💡" if self.hints_left > 0 else "○"
        try:
            icon_surf = font.render("💡", True, COLOR_TEXT)
        except Exception:
            icon_surf = font.render("?", True, COLOR_TEXT)
        surface.blit(icon_surf, icon_surf.get_rect(center=(px, py - 2)))

        # Zähler-Badge
        if self.hints_left > 0:
            badge_r = 12
            badge_pos = (px + r - badge_r // 2, py - r + badge_r // 2)
            pygame.draw.circle(surface, COLOR_CORAL, badge_pos, badge_r)
            font_sm = get_font(FONT_SIZE_XS, bold=True)
            num_surf = font_sm.render(str(self.hints_left), True, COLOR_WHITE)
            surface.blit(num_surf, num_surf.get_rect(center=badge_pos))


# ---------------------------------------------------------------------------
# HintOverlay
# ---------------------------------------------------------------------------

class HintOverlay:
    """Halbtransparentes Overlay mit Hinweistext."""

    def __init__(self, hint_text: str, on_close: Optional[Callable] = None):
        self.hint_text = hint_text
        self.on_close = on_close
        self._alpha = 0
        self._tween = Tween(0, 220, 0.3, ease_out_cubic)
        self._active = True

    def handle_event(self, event: pygame.event.Event) -> bool:
        if not self._active:
            return False
        if event.type in (pygame.MOUSEBUTTONDOWN, pygame.KEYDOWN):
            self._active = False
            if self.on_close:
                self.on_close()
            return True
        return False

    def update(self, dt: float) -> None:
        if self._tween:
            self._alpha = int(self._tween.update(dt))

    def draw(self, surface: pygame.Surface) -> None:
        w, h = surface.get_size()
        # Dunkles Overlay
        overlay = pygame.Surface((w, h), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, min(self._alpha, 150)))
        surface.blit(overlay, (0, 0))

        # Hinweis-Karte
        card_w, card_h = 750, 300
        card_rect = pygame.Rect((w - card_w) // 2, (h - card_h) // 2, card_w, card_h)
        draw_rounded_rect(surface, COLOR_WHITE, card_rect, radius=24, shadow_offset=6)

        # Glühbirnen-Icon
        font_lg = get_font(FONT_SIZE_MD + 6, bold=True)
        title_surf = font_lg.render("💡 Hinweis", True, COLOR_YELLOW_DARK)
        surface.blit(title_surf, title_surf.get_rect(center=(w // 2, card_rect.y + 55)))

        # Hinweistext (umgebrochen)
        font_md = get_font(FONT_SIZE_SM)
        words = self.hint_text.split()
        lines = []
        current = ""
        for word in words:
            test = (current + " " + word).strip()
            if font_md.size(test)[0] < card_w - 80:
                current = test
            else:
                if current:
                    lines.append(current)
                current = word
        if current:
            lines.append(current)

        y = card_rect.y + 120
        for line in lines:
            line_surf = font_md.render(line, True, COLOR_TEXT)
            surface.blit(line_surf, line_surf.get_rect(center=(w // 2, y)))
            y += font_md.get_height() + 8

        # "Tippe zum Schließen"
        font_xs = get_font(FONT_SIZE_XS)
        close_surf = font_xs.render("Klick oder Taste zum Schließen", True, COLOR_TEXT_LIGHT)
        surface.blit(close_surf, close_surf.get_rect(center=(w // 2, card_rect.bottom - 28)))


# ---------------------------------------------------------------------------
# FeedbackText (Richtig / Falsch Anzeige)
# ---------------------------------------------------------------------------

class FeedbackText:
    """Kurzer Feedback-Text der animiert erscheint und wieder verschwindet."""

    def __init__(self, text: str, center: tuple[int, int], color: tuple, duration: float = 1.5):
        self.text = text
        self.center = center
        self.color = color
        self.duration = duration
        self._elapsed = 0.0
        self._alpha_tween = Tween(0, 255, 0.2, ease_out_cubic)
        self._y_offset = Tween(0, -30, duration, ease_out_cubic)
        self.done = False

    def update(self, dt: float) -> None:
        self._elapsed += dt
        self._alpha_tween.update(dt)
        self._y_offset.update(dt)
        if self._elapsed >= self.duration:
            self.done = True

    def draw(self, surface: pygame.Surface) -> None:
        if self.done:
            return
        progress = self._elapsed / self.duration
        alpha = int(255 * (1 - max(0, (progress - 0.7) / 0.3)))
        font = get_font(FONT_SIZE_LG if len(self.text) < 10 else FONT_SIZE_MD, bold=True)
        text_surf = font.render(self.text, True, self.color)
        text_surf.set_alpha(alpha)
        y = self.center[1] + int(self._y_offset.value)
        surface.blit(text_surf, text_surf.get_rect(center=(self.center[0], y)))


from ..settings import FONT_SIZE_LG
