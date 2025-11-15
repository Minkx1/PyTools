import pygame 

def log(msg, sender:str = "PyGameEngine", error:bool = False) -> str:
    """
    Cool verison of Basic print(). =P
    """
    formated_msg = f"[{sender}] {str(msg)}" if not error else f"[{sender} | ERROR] {str(msg)}"
    print(formated_msg)
    return formated_msg

def get_globals() -> dict:
    """
    Return the global variables of the script that started the call chain (script __main__).
    Works even if called inside a method of a class or engine.
    """
    import inspect

    frame = inspect.currentframe()
    while frame:
        globs = frame.f_globals
        if globs.get("__name__") == "__main__":
            return globs
        frame = frame.f_back
    return {}

def get_engine():
    """Getting engine object"""
    from .engine import PyGameEngine
    return PyGameEngine.engine

def render_text(
        text: str,
        x: float,
        y: float,
        font: "str | pygame.font.Font" = "TimesNewRoman",
        size: int = 14,
        color: str| tuple[int, int, int] = "black",
        center: bool = False,
    ):
        """Render text on screen with caching.
        font can be str (name) or pygame.font.Font object.
        """
        if isinstance(font, str):
            font_obj = pygame.font.SysFont(font, size)
        else:
            font_obj = font
            size = font.get_linesize()
        text_surf = font_obj.render(text, True, color)

        rect = text_surf.get_rect()
        if center:
            rect.center = (x, y)
        else:
            rect.topleft = (x, y)

        pygame.display.get_surface().blit(text_surf, rect) # type: ignore
        return rect