"""===== scenes.py ====="""

from contextlib import contextmanager
from .sprite import Sprite, Group
from .core import NovaEngine

class Scene:
    """
    Scene class for organizing game objects.
    - Holds all sprites, buttons, players, etc.
    - Manages solid objects for collision detection.
    - Provides context manager for automatic sprite registration.
    """

    def __init__(self):
        """
        Initialize a new scene.
        """
        
        self.engine = NovaEngine.Engine
        self.objects = []  # all sprites in scene
        self.solids = []  # only solid sprites
        self.run = self.update  # main update function

        # Register scene in engine
        self.engine.scenes.append(self)

    # ========================
    # OBJECT MANAGEMENT
    # ========================
    def add_sprite(self, *sprites):
        """Add sprites to the scene manually."""
        sprites_list = list(sprites)
        for obj in sprites_list:
            self.objects.append(obj)
            if getattr(obj, "solid", False):
                self.solids.append(obj)

    @contextmanager
    def sprites(self):
        """
        Context manager to auto-register newly created sprites.
        Usage:
            with scene.sprites():
                sprite1 = Sprite(...)

                @sprite1.set_update()
                def _(): ...
        """
        import inspect

        frame = inspect.currentframe().f_back.f_back
        before_vars = set(frame.f_locals.keys())

        yield  # user creates sprites inside this block

        after_vars = frame.f_locals
        new_vars = set(after_vars.keys()) - before_vars

        for name in new_vars:
            obj = after_vars[name]
            if isinstance(obj, (Sprite, Group)):
                self.objects.append(obj)
                if getattr(obj, "solid", False):
                    self.solids.append(obj)
        
        self.objects.sort(key=lambda o: getattr(o, "layer", 0))
        self.solids.sort(key=lambda o: getattr(o, "layer", 0))

    # ========================
    # SCENE LOOP
    # ========================
    def function(self):
        """Decorator to register the main update function for the scene."""

        def decorator(func):
            self.run = func
            return func

        return decorator

    def update(self):
        """Call update() on all scene objects."""
        for obj in self.objects:
            try:
                obj.update()
                    
            except Exception as e:
                from .core import log

                log(e, "SceneManager | Update", True)