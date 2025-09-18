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
        
        self._engine = NovaEngine.Engine
        self._objects = []  # all sprites in scene
        self._solids = []  # only solid sprites
        self._loop_function = self.update  # main update function

        # Register scene in engine
        self._engine.scenes.append(self)
    
    def get_objects(self, solids=False):
        if solids: return self._solids
        return self._objects

    # ========================
    # OBJECT MANAGEMENT
    # ========================
    def add_sprite(self, *sprites):
        """Add sprites to the scene manually."""
        sprites_list = list(sprites)
        for obj in sprites_list:
            self._objects.append(obj)
            if getattr(obj, "solid", False):
                self._solids.append(obj)

    @contextmanager
    def init(self):
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
            if isinstance(obj, (Sprite, Group)) or (hasattr(obj, 'update') and callable(getattr(obj, 'update', None))):
                self._objects.append(obj)
                if getattr(obj, "solid", False):
                    self._solids.append(obj)
        
        self._objects.sort(key=lambda o: getattr(o, "layer", 0))
        self._solids.sort(key=lambda o: getattr(o, "layer", 0))

    # ========================
    # SCENE LOOP
    # ========================
    def loop(self):
        """ Funtion, send in decorator, will be called in main game loop """

        def decorator(func):
            self._loop_function = func
            return func

        return decorator

    def update(self):
        """Call update() on all scene objects."""
        for obj in self._objects:
            try:
                obj.update()
                    
            except Exception as e:
                from .utils import log
                log(e, "SceneManager | Update", True)