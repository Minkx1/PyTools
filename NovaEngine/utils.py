"""===== utils.py ====="""

import pygame
from typing import Tuple, Union
from .core import NovaEngine

class Colors:
    """Predefined RGB colors."""

    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)
    RED = (255, 0, 0)
    GREEN = (0, 255, 0)
    BLUE = (0, 0, 255)

class Utils:
    @staticmethod
    def fill_background(
        color: Union[Colors, Tuple[int, int, int]] = Colors.BLACK,
        image: pygame.Surface = None,
    ):
        """Fill the screen with a color or an image."""
        if image:
            NovaEngine.Engine.screen.blit(image, (0, 0))
        else:
            if isinstance(color, Colors):
                color = color.value
            NovaEngine.Engine.screen.fill(color)

    @staticmethod
    def render_text(
        text: str,
        x: float,
        y: float,
        font: Union[str, "pygame.font.Font"] = "TimesNewRoman",
        size: int = 14,
        color: Union[Colors, Tuple[int, int, int]] = Colors.BLACK,
        center: bool = False,
    ):
        """Render text on screen with caching.
        font can be str (name) or pygame.font.Font object.
        """
        if isinstance(color, Colors):
            color = color.value

        if isinstance(font, str):
            font_obj = pygame.font.SysFont(font, size)
        else:
            font_obj = font
            size = font.get_linesize()
        cache_key = (text, font_obj, size, color)
        text_surf = NovaEngine.Engine._text_cache.get(cache_key)

        if text_surf is None:
            text_surf = font_obj.render(text, True, color)
            NovaEngine.Engine._text_cache[cache_key] = text_surf

        rect = text_surf.get_rect()
        if center:
            rect.center = (x, y)
        else:
            rect.topleft = (x, y)

        NovaEngine.Engine.screen.blit(text_surf, rect)
        return rect
