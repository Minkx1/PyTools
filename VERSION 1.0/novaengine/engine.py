"""===== core.py =====
Модуль ядра NovaEngine. Містить головний клас рушія, керування сценами, обробку вводу та запуск циклу гри.
"""

import pygame
import threading
from typing import Callable, Optional, Any, List, Tuple, Dict

from .dev_tools import log, get_globals

ENGINE_VERSION: str = "V1.9.2"
APP_NAME_ENGINE_TEMPLATE: str = f" | Running with NovaEngine {ENGINE_VERSION}"
ALLOW_NO_TEMPLATE: bool = False

class NovaEngine:
    """
    Lightweight PyGame framework for Main Game Interaction.
    Handles and runs active scene, checks for pressed keys and mouse buttons.
    """

    Engine: Optional["NovaEngine"] = None

    def __init__(
        self,
        window_size: Tuple[int, int] = (500, 500),
        app_name: str = "Game",
        icon_path: Optional[str] = None,
        fps: int = 60,
    ) -> None:
        """
        Initialize the engine window and core systems.
        """
        pygame.init() 

        self.app_name: str = app_name
        self.icon_path: Optional[str] = icon_path
        self.screen: pygame.Surface = pygame.display.set_mode(window_size)
        if not ALLOW_NO_TEMPLATE:
            pygame.display.set_caption(self.app_name + APP_NAME_ENGINE_TEMPLATE)
        else:
            pygame.display.set_caption(self.app_name)
        if self.icon_path:
            pygame.display.set_icon(pygame.image.load(self.icon_path).convert_alpha())
        self.clock: pygame.time.Clock = pygame.time.Clock()
        self.fps: int = fps
        self.time: int = 0
        self.in_game_time: int = 0
        self.time_spent_frozed: int = 0
        self.time_froze: bool = False
        self.debug: bool = False
        self.dt: float = 0.0
        self.event_handlers: List[Any] = []
        self.m_clck: bool = False
        self.mouse_clicked: bool = False
        self.keys_pressed = None
        self.key_single_state: Dict[int, bool] = {}
        self._text_cache: Dict[Any, Any] = {}
        self.cooldowns: List[Any] = []
        self.intervals: List[Any] = []
        self.scenes: List[Any] = []
        self.active_scene: Optional[Any] = None
        self.main_run_func: Optional[Callable[[], None]] = None
        self.start_func: Optional[Callable[[], None]] = None
        self.end_func: Optional[Callable[[], None]] = None
        self.globals: Optional[Dict[str, Any]] = None
        self.threads: List[Callable[[], None]] = []
        self.terminal_allow: bool = True
        self.running: bool = False
        NovaEngine.Engine = self

    def run(self, first_scene: Optional[Any] = None, save_manager: Optional[Any] = None) -> "NovaEngine":
        """
        Run the main game loop and optional command input thread.
        """
        def setup() -> None:
            self.globals = get_globals()
            if self.terminal_allow:
                import sys
                import subprocess

                @self.new_thread()
                def run_cmd_input() -> None:
                    while True:
                        try:
                            cmd: str = input(">>> ")
                        except EOFError:
                            break
                        if cmd in ("kill()", "quit()"):
                            self.quit()
                            break
                        elif cmd == "restart()":
                            subprocess.Popen(
                                [sys.executable] + sys.argv,
                                creationflags=subprocess.CREATE_NEW_CONSOLE,
                            )
                            self.quit()
                            break
                        else:
                            try:
                                exec(cmd, getattr(self, "globals", {}))
                            except Exception as e:
                                log(str(e), error=True)

            if first_scene is not None:
                try:
                    self.active_scene = first_scene
                except Exception as e:
                    log(f"{e}", sender="SceneManager", error=True)
            if not self.active_scene and self.scenes:
                self.active_scene = self.scenes[0]

        setup()

        if save_manager is not None:
            save_manager.load()

        if self.start_func:
            self.start_func()

        if self.main_run_func:
            self.main_run_func()
        else:
            self.running = True
            while self.running:
                self.keys_pressed = pygame.key.get_pressed()
                self.mouse_clicked = self.mouse_clicked_event(first_iter=True)
                self.time = pygame.time.get_ticks()
                if not self.time_froze:
                    self.in_game_time = self.time - self.time_spent_frozed

                self.screen.fill((255, 255, 255))
                if self.active_scene is not None:
                    self.active_scene.loop_function()

                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        self.quit()
                    for handler in self.event_handlers:
                        try:
                            handler.handle_event(event)
                        except Exception as e:
                            log(str(e), "NovaEngine | Event Handler", True)

                pygame.display.flip()
                self.dt = self.clock.tick(self.fps) / 1000

        if self.end_func:
            self.end_func()

        if save_manager is not None:
            save_manager.save()
        
        return self

    def quit(self) -> None:
        """
        Stop engine and exit program.
        """
        self.running = False
        log("Quitting the game...")

    def set_main(self) -> Callable[[Callable[[], None]], Callable[[], None]]:
        """
        Decorator to register main game logic.
        """
        def decorator(func: Callable[[], None]) -> Callable[[], None]:
            self.main_run_func = func
            return func
        return decorator

    def set_start(self) -> Callable[[Callable[[], None]], Callable[[], None]]:
        """
        Decorator to register start game logic.
        """
        def decorator(func: Callable[[], None]) -> Callable[[], None]:
            self.start_func = func
            return func
        return decorator

    def set_end(self) -> Callable[[Callable[[], None]], Callable[[], None]]:
        """
        Decorator to register end game logic.
        """
        def decorator(func: Callable[[], None]) -> Callable[[], None]:
            self.end_func = func
            return func
        return decorator

    def new_thread(self) -> Callable[[Callable[[], None]], Callable[[], None]]:
        """
        Decorator to run function in a separate daemon thread.
        """
        def decorator(func: Callable[[], None]) -> Callable[[], None]:
            if func not in self.threads:
                self.threads.append(func)
                threading.Thread(target=func, daemon=True).start()
            return func
        return decorator

    def set_debug(self, value: bool = True) -> "NovaEngine":
        """
        Enable or disable debug rendering (FPS, mouse pos).
        """
        self.debug = value
        return self

    def mouse_clicked_event(self, button: int = 0, first_iter: bool = False) -> bool:
        """
        Return True only on first mouse click (not hold).
        """
        if not first_iter:
            pressed: bool = False
            if not self.m_clck and pygame.mouse.get_pressed()[button]:
                self.m_clck = True
                pressed = True
            if not pygame.mouse.get_pressed()[button]:
                self.m_clck = False
            return pressed
        else:
            return self.mouse_clicked

    def key_pressed(self, key: int) -> bool:
        """
        Return True only on first key press (not hold).
        """
        try:
            if self.keys_pressed:
                pressed: bool = bool(self.keys_pressed[key])
            else:
                pressed = False
                return False
        except (IndexError, TypeError):
            return False

        if pressed:
            if not self.key_single_state.get(key, False):
                self.key_single_state[key] = True
                return True
            return False
        else:
            self.key_single_state[key] = False
            return False

    def key_hold(self, key: int) -> bool:
        """
        Return True while key is held down.
        """
        try:
            if self.keys_pressed:
                return bool(self.keys_pressed[key])
            return False
        except (IndexError, TypeError):
            return False

    def set_active_scene(self, scene: Any) -> None:
        """
        Set active scene without running it immediately.
        """
        self.active_scene = scene

    def run_active_scene(self) -> None:
        """
        Run the currently active scene.
        """
        if self.active_scene is not None:
            try:
                self.active_scene.loop_function()
            except Exception as e:
                log(str(e), "SceneManager", True)

    def get_scene(self) -> Optional[Any]:
        """
        Get the currently active scene.
        """
        return self.active_scene

    def get_screen(self) -> pygame.Surface:
        """
        Get the main screen surface.
        """
        return self.screen


if __name__ == "__main__":
    # import novaengine as nova   

    app = NovaEngine()

    app.run()