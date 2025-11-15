"""===== scenes.py ====="""

from contextlib import contextmanager
from .sprite import Sprite, Group
from .engine import NovaEngine

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
        self.loop_function = self.update  # main update function

        # Register scene in engine
        if self.engine: self.engine.scenes.append(self)
    
    def get_objects(self, solids=False):
        if solids: return self.solids
        return self.objects

    # ========================
    # OBJECT MANAGEMENT
    # ========================
    def add_object(self, *sprites):
        """Add sprites to the scene manually."""
        sprites_list = list(sprites)
        for obj in sprites_list:
            self.objects.append(obj)
            if getattr(obj, "solid", False):
                self.solids.append(obj)

    def remove_object(self, obj):
        """Remove a sprite from the scene."""
        templ = self.objects.copy()
        if obj in templ:
            templ.remove(obj)
            self.objects = templ # to avoid modifying list during iteration

    @contextmanager
    def set_objects(self):
        """
        Context manager to auto-register newly created sprites.
        Usage:
            with scene.set_objects():
                sprite1 = Sprite(...)

                @sprite1.set_update()
                def update_of_sprite1(): ...
        """
        import inspect

        frame = inspect.currentframe().f_back.f_back # type: ignore
        before_vars = set(frame.f_locals.keys()) # type: ignore

        yield  # user creates sprites inside this block

        after_vars = frame.f_locals # type: ignore
        new_vars = set(after_vars.keys()) - before_vars

        for name in new_vars:
            obj = after_vars[name]
            if isinstance(obj, (Sprite, Group)) or (hasattr(obj, 'update') and callable(getattr(obj, 'update', None))):
                self.objects.append(obj)
                if getattr(obj, "solid", False):
                    self.solids.append(obj)
        
        self.objects.sort(key=lambda o: getattr(o, "layer", 0))
        self.solids.sort(key=lambda o: getattr(o, "layer", 0))

    # ========================
    # SCENE LOOP
    # ========================
    def set_loop(self):
        """ Funtion, send in decorator, will be called in main game loop """

        def decorator(func):
            self.loop_function = func
            return func

        return decorator

    def update(self):
        """Call update() on all scene objects."""
        for obj in self.objects:
            try:
                obj.update()  
            except Exception as e:
                from .utils import log
                log(str(e), "SceneManager | Update", True)