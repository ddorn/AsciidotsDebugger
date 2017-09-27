from functools import lru_cache

import pygame

from dots.vector import Pos


class Font:
    """A wrapper around the pygame font system that caches the surfaces."""

    def __init__(self, name, size):
        self.font_name = name
        self.font_size = round(size)
        self.char_size = None
        self.font = self.set_size(size)  # type: pygame.font.FontType

    def set_size(self, new_size):
        """Chage the size of the font but keep it between 80 and 2."""
        # clamp the size
        self.font_size = min(80, max(2, round(new_size)))

        # clear all caches
        self.render_char.cache_clear()
        self.render_text.cache_clear()

        font = pygame.font.Font(self.font_name, self.font_size)
        self.char_size = Pos(font.size("."))
        self.font = font
        return font

    def change_size(self, delta):
        """Increase or decrease the font size by delta."""
        self.set_size(self.font_size + delta)

    def size(self, text):
        """Determine the amount of space needed to render text."""
        return self.font.size(text)

    @lru_cache(maxsize=None)
    def render_char(self, char, color, bg=None):
        """Draw char on a new surface. The result is allways cached."""
        return self.font.render(char, True, color, bg)  # type: pygame.SurfaceType

    @lru_cache(maxsize=128)
    def render_text(self, text, color, bg):
        """Draw text on a new surface. The last texts are cached."""
        return self.font.render(text, True, color, bg)  # type: pygame.SurfaceType
