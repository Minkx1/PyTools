import inspect
from typing import List, Callable
from .utils import log, get_engine

class Scene:
    """
    Scene class for ordering objects in game.
    Usage:
        scene = Scene(engine)
        with scene.content:
            obj1 = updatable_class(...)
            obj2 = updatable_class(...)
        
        @scene.define
        def main():
            print(f"Hello. I have {len(scene.objects)} objects.")
    """

    class SceneObjectsContext:
        def __init__(self, scene):
            self.scene = scene
            self._caller_locals = None

        def __enter__(self):
            frame = inspect.currentframe().f_back # type: ignore
            self._caller_locals = frame.f_locals # type: ignore
            return self

        def __exit__(self, exc_type, exc_val, exc_tb):
            for name, obj in self._caller_locals.items():  # type: ignore
                if isinstance(obj, type):
                    continue

                method = getattr(obj, "update", None)
                if not callable(method):
                    continue
                if not hasattr(method, "__self__") or method.__self__ is None:  # type: ignore
                    continue

                self.scene.objects.append(obj)

            return False


    class SceneDefineDecorator:
        """Defining main scene function"""
        def __init__(self, scene):
            self.scene = scene

        def __call__(self, func: Callable):
            self.scene.main = func
            return func

    def __init__(self):
        self.engine = get_engine()
        if self.engine == None:
            log("Engine IS NOT initialized! Please initialize PyGameEngine before.", error=True)
            raise PermissionError

        self.objects: List[object] = []

        self.main = self.update_all

        self.content = Scene.SceneObjectsContext(self)
        self.define = Scene.SceneDefineDecorator(self)

        self.engine.scenes.append(self)

    def update_all(self):
        try:
            for obj in self.objects:
                obj.update() # type: ignore
        except Exception as e:
            log(e, error=True)

    def run(self):
        """Engine_used"""
        self.main()
