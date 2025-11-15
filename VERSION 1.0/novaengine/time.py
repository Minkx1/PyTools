"""===== time.py ====="""

import threading
from .engine import NovaEngine

class Time:
    @staticmethod
    def time_freeze():
        NovaEngine.Engine.time_froze = True  # type: ignore
        NovaEngine.Engine.previous_time = NovaEngine.Engine.in_game_time # type: ignore
    
    @staticmethod
    def time_unfreeze():
        NovaEngine.Engine.time_froze = False # type: ignore
        NovaEngine.Engine.time_spent_frozed = (NovaEngine.Engine.time - NovaEngine.Engine.previous_time) # type: ignore

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
            import threading
            def cycle():
                import time
                if count == -1:
                    while True:
                        func()
                        time.sleep(cooldown)
                else:
                    for _ in range(count):
                        func()
                        time.sleep(cooldown)
            
            threading.Thread(target=cycle, daemon=True).run()

            return func

        return decorator
    
    class Cooldown:
        """Check or create a cooldown for a key."""
        def __init__(self, duration):
            """Initializes Cooldown. Duration must be in seconds."""
            self.engine = NovaEngine.Engine

            self.duration = duration*1000
            self.state = True
            self.start_time = 0

            self.engine.cooldowns.append(self) # type: ignore

        def check(self):
            # Checks if coolodown is ready
            self.now = self.engine.time # type: ignore
            self.state = self.now - self.start_time >= self.duration
            return self.state
        
        def start(self):
            # Called one time and starts cooldown
            self.start_time = self.engine.time # type: ignore
            self.state = False
            return self