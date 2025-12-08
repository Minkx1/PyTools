"""
Engine.py 
"""
import pygame
import threading, time
from .utils import log, get_globals

class _Time:
    def __init__(self) -> None:
        self.actual_fps:float = 0 # actual fps that window runs
        self.dt:float = 0 # time in miliseconds that past after previous itteration.
        self.Clock = pygame.time.Clock()
        self.time:float = 0
        self.cooldowns:list = []
    
    @staticmethod
    def Timer(duration):
        """Decorator to run function after $duration$ seconds."""

        def decorator(func):
            threading.Timer(duration, func).start()
            return func

        return decorator
    
    @staticmethod
    def Interval(count, cooldown):
        """Call function `count` times with delay `cooldown` seconds (use -1 for infinite)."""
        def decorator(func):
            def cycle():
                try:
                    if count == -1:
                        while True:
                            func()
                            time.sleep(cooldown)
                    else:
                        for _ in range(count):
                            func()
                            time.sleep(cooldown)
                except Exception as e:
                    pass        
            threading.Thread(target=cycle, daemon=True).run()

            return func

        return decorator
    
    class TimeCooldown:
        def __init__(self, time, duration):
            """Initializes Cooldown. Duration must be in seconds."""
            self.time = time
            self.duration = duration*1000
            self.start_time = 0

            time.cooldowns.append(self) # type: ignore

        def check(self):
            return self.time.time - self.start_time >= self.duration

        def start(self):
            # Called one time and starts cooldown
            self.start_time = self.time.time # type: ignore
            return self

    def Cooldown(self, delay):
        return _Time.TimeCooldown(self, delay)

class _Input:
    def __init__(self):
        self._prev_keys = pygame.key.get_pressed()
        self._keys = self._prev_keys

        self._prev_mouse = pygame.mouse.get_pressed(num_buttons=5)
        self._mouse = self._prev_mouse

    def update_input(self):
        """Must be called once per frame, before game logic."""
        # Save previous state
        self._prev_keys = self._keys
        self._prev_mouse = self._mouse

        # Read current state
        self._keys = pygame.key.get_pressed()
        self._mouse = pygame.mouse.get_pressed(num_buttons=5)

    def key_hold(self, *keys) -> bool:
        """Returns True as long as key is held."""
        return any(self._keys[k] for k in keys)

    def key_pressed(self, *keys) -> bool:
        """Returns True only on the frame the key was pressed."""
        return any(self._keys[k] and not self._prev_keys[k] for k in keys)

    def mouse_pressed(self, mouse_button: int = 0) -> bool:
        """mouse_button: 0=LMB, 1=RMB, 2=MMB"""
        return self._mouse[mouse_button] and not self._prev_mouse[mouse_button]

    def mouse_hold(self, mouse_button: int = 0) -> bool:
        return self._mouse[mouse_button]


class PyGameEngine:
    engine: 'None | PyGameEngine' = None

    def __init__(self, 
                 screen_size: tuple[int, int] = (500, 500),
                 window_caption: str = "Game",
                 icon: str | pygame.Surface | None = None,
                 fps: float = 60,
                 debug: bool = True) -> None:
        
        pygame.init()
        PyGameEngine.engine = self

        try:
            self.screen = pygame.display.set_mode(screen_size)
            self._window_caption = window_caption; pygame.display.set_caption(self._window_caption)
            if icon: 
                if isinstance(icon, str):
                    pygame.display.set_icon(pygame.image.load(icon).convert_alpha())
                if isinstance(icon, pygame.Surface):
                    pygame.display.set_icon(icon)
        except Exception as e:
            log(e, error=True)
        
        self.running = True
        self.FPS = fps
        self.debug = debug

        self.Time = _Time() 
        self.Input = _Input()

        self.scenes:list = []
        self.active_scene = None
        self.logic_functions = {"main": None, "start": None, "end": None}
        self.event_handlers = []
        
    def quit(self, exit_code:int = 0) -> int:
        log(f"Quitting...")
        self.running = False
        return exit_code

    def _console(self) -> None:
        while True:
            cmd = input(">>>")
            try:
                if cmd in ["quit()", "kill()"]:
                    self.quit()
                    break
                else:
                    exec(cmd, getattr(self, "globals", {}))
            except Exception as e:
                log(e, error=True)
    
    def set_active_scene(self, scene) -> None:
        self.active_scene = scene
        return 

    def logic(self, mode: str = "start"):
        """Decorator called, to init some logic. Mode in ['main', 'start', 'end']"""
        def decorator(func):
            def wrapper():
                if mode not in self.logic_functions.keys():
                    raise PermissionError("Error in registering Engine's logic 'Inapropriate logic mode'.")
                else:
                    self.logic_functions[mode] = func
                return func
            return wrapper
        return decorator 


    def handle_event(self, event=None):
        if event:
            for hndl in self.event_handlers:
                if callable(hndl):
                    hndl(event)
        return
            

    def run(self, first_scene = None) -> None:
        if self.debug:
            self.globals = get_globals()
            threading.Thread(target=self._console, daemon=True).start()

        self.active_scene = first_scene or self.scenes[0]

        if callable(self.logic_functions["start"]):
            self.logic_functions["start"]()

        while self.running:
            for event in pygame.event.get():
                self.handle_event(event)
                if event.type == pygame.QUIT:
                    self.quit(1)
            self.screen.fill("white")
            self.Input.update_input()

            try:
                if callable(self.logic_functions["main"]):
                    self.logic_functions["main"]()
                else:
                    if self.active_scene != None: 
                        self.active_scene.run()
            except Exception as e:
                log(e, error=True)
            
            self.dt = self.Time.Clock.tick(self.FPS)
            self.Time.time = pygame.time.get_ticks()
            self.Time.actual_fps = self.Time.Clock.get_fps()
            pygame.display.update()

        if callable(self.logic_functions["end"]):
            self.logic_functions["end"]()

        return