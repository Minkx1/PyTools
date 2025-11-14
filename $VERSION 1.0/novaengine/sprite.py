"""===== sprite.py =====
Module for managing 2D sprites with Pygame.

Provides the Sprite class for handling transformations,
drawing, collisions, and animations, and a Group class
for batch management of multiple sprites.
"""

from typing import Optional, Callable, Any, Tuple, List, Dict, Union
import math
import random
import pygame

class Sprite:
    """
    A helper class for working with sprites.

    Supports:
        * loading images
        * scaling, moving, rotating
        * drawing on the screen
        * custom updates
        * animation handling
    """

    _counter: int = 0

    def __init__(
        self,
        img_path: Optional[str],
        width: Optional[float] = None,
        height: Optional[float] = None,
        solid: bool = False,
    ) -> None:
        """
        Initialize a new Sprite.

        Args:
            img_path (str): Path to image file.
            width (float | None): Optional width for scaling.
            height (float | None): Optional height for scaling.
            solid (bool): Whether sprite is solid (collidable).
        """
        from .engine import NovaEngine
        from .time import Time

        self.engine = NovaEngine.Engine
        if self.engine is None:
            raise Exception("Engine not initialized. Create NovaEngine instance first.")
        self.surface : pygame.Surface = self.engine.get_screen()
        self.solid: bool = solid
        self.alive: bool = True

        self.force_update: bool = False
        self.update_func: Optional[Callable[[], None]] = None

        self.debug_color: Tuple[int, int, int] = (
            random.randint(0, 255),
            random.randint(0, 255),
            random.randint(0, 255),
        )
        self.debug: bool = self.engine.debug

        Sprite._counter += 1
        self.layer: int = Sprite._counter

        # Load original image (keep for transformations)
        if img_path:
            self.original_img: pygame.Surface = pygame.image.load(img_path).convert_alpha()
            if width and height:
                self.original_img = pygame.transform.scale(
                    self.original_img, (int(width), int(height))
                )
        else:
            if width and height:
                self.original_img = pygame.Surface((int(width), int(height)))
            else:
                self.original_img = pygame.Surface((0, 0))

        self.width: int = self.original_img.get_width()
        self.height: int = self.original_img.get_height()

        self.collide_immun_time: float = 0.1
        self.collide_immun = Time.Cooldown(self.collide_immun_time)

        self.img: pygame.Surface = self.original_img
        self.angle: float = 0
        self.rect: pygame.Rect = self.img.get_rect()
        self.x: float
        self.y: float
        self.x, self.y = self.rect.topleft
        self.scaling_size: Tuple[int, int] = (self.width, self.height)

        self.animations: Dict[str, Dict[str, Any]] = {}
        self.current_animation: Optional[str] = None

    def set_collide_immunity(self, duration: float) -> None:
        """
        Set immunity duration for collision checks.
        """
        from .time import Time
        self.collide_immun_time = duration
        self.collide_immun = Time.Cooldown(self.collide_immun_time)
    
    def set_layer(self, layer: int) -> "Sprite":
        """
        Set sprite's layer for rendering order.
        """
        self.layer = layer
        return self

    def change_layer(self, value: Optional[int] = None) -> "Sprite":
        """
        Change sprite's layer by value (default +1).
        """
        self.layer += value or 1
        return self

    def draw(self) -> "Sprite":
        """
        Draw sprite to the screen surface.
        """
        if self.alive:
            trans = pygame.transform.scale(self.original_img, self.scaling_size)
            self.img = pygame.transform.rotate(trans, self.angle)
            self.rect = self.img.get_rect(center=self.rect.center)
            self.surface.blit(self.img, self.rect.topleft)

        if self.debug:
            from .utils import Utils
            pygame.draw.rect(self.surface, self.debug_color, self.rect, 1)
            Utils.render_text(
                f"{round(self.rect.x)}, {round(self.rect.y)}",
                self.rect.x,
                self.rect.y,
                size=12,
                center=True,
            )
        return self

    def hover(self, special_point: Optional[Tuple[float, float]] = None) -> bool:
        """
        Check if sprite is hovered by mouse or special point.
        """
        val = self.rect.collidepoint(pygame.mouse.get_pos())
        if special_point:
            try: 
                val = self.rect.collidepoint(special_point)
            except Exception as e:
                from .utils import log
                log(str(e), "Sprite | Hover", True)
        return val

    def set_update(self, force: bool = False) -> Callable[[Callable[[], None]], Callable[[], None]]:
        """
        Decorator to set custom update logic for the sprite.
        """
        def decorator(func: Callable[[], None]) -> Callable[[], None]:
            self.force_update = force
            self.update_func = func
            return func
        return decorator

    def set_position(self, x: Optional[float] = None, y: Optional[float] = None) -> "Sprite":
        """
        Set top-left position of the sprite.
        """
        if x is not None:
            self.x = x
        if y is not None:
            self.y = y
        self.rect.topleft = (int(self.x), int(self.y))
        return self

    def place_centered(self, x: int, y: int) -> "Sprite":
        """
        Set sprite's center coordinates.
        """
        self.rect.center = (x, y)
        self.x, self.y = self.rect.topleft
        return self

    def move(self, dx: float = 0, dy: float = 0) -> "Sprite":
        """
        Move sprite by (dx, dy).
        """
        self.rect.move_ip(dx, dy)
        self.x, self.y = self.rect.topleft
        return self

    def move_to(self, target: Union["Sprite", Tuple[float, float]], speed: float) -> None:
        """
        Move sprite towards a target with given speed.
        """
        if isinstance(target, Sprite):
            tx, ty = target.rect.center
        else:
            tx, ty = target
        dx, dy = tx - self.rect.centerx, ty - self.rect.centery
        dist = math.hypot(dx, dy)
        if dist > 0:
            dx /= dist
            dy /= dist
            if self.engine != None:
                self.rect.x += int(dx * speed * self.engine.dt)
                self.rect.y += int(dy * speed * self.engine.dt)
            else:
                self.rect.x += int(dx * speed)
                self.rect.y += int(dy * speed)
                raise Exception("Engine not initialized. Create NovaEngine instance first.")

    def move_angle(self, speed: float) -> None:
        """
        Move sprite in the direction of its angle.
        """
        ang = self.angle + 90
        dx = math.sin(math.radians(ang)) * speed
        dy = math.cos(math.radians(ang)) * speed
        self.move(dx, dy)

    def scale(self, width: int, height: int) -> "Sprite":
        """
        Scale sprite to (width, height).
        """
        self.scaling_size = (width, height)
        return self

    def stay_in_rect(self, rect: pygame.Rect) -> "Sprite":
        """
        Clamp sprite inside the given rect.
        """
        self.rect.clamp_ip(rect)
        return self

    def rotate(self, angle: float) -> "Sprite":
        """
        Rotate sprite by angle.
        """
        self.angle = (self.angle - angle) % 360
        return self

    def look_at(self, target: Union["Sprite", Tuple[float, float]]) -> None:
        """
        Rotate sprite to face target.
        """
        if isinstance(target, Sprite):
            tx, ty = target.rect.center
        else:
            tx, ty = target
        dx, dy = tx - self.rect.centerx, ty - self.rect.centery
        self.angle = -math.degrees(math.atan2(dy, dx))

    def collide(self, other: Optional["Sprite"] = None, rect: Optional[pygame.Rect] = None) -> bool:
        """
        Check collision with another sprite or rect.
        """
        if self.collide_immun.check():
            self.collide_immun.start()
            if other and other.alive:
                return self.rect.colliderect(other.rect)
            if rect:
                return self.rect.colliderect(rect)                
        return False

    def collide_any(self, solids: bool = False) -> bool:
        """
        Check collision with any sprite in the scene.
        """
        if self.collide_immun.check():
            if self.engine is not None:
                self.collide_immun.start()
                scene = self.engine.get_scene() 
                objs = scene.objects # type: ignore
                if solids:
                    objs = scene.solids # type: ignore
                for sp in objs:
                    if sp != self:
                        if self.rect.colliderect(sp.rect):
                            return True
        return False

    def rect_update(self) -> pygame.Rect:
        """
        Update the rect based on the current image size.
        """
        self.rect = self.img.get_rect(topleft=self.rect.topleft)
        self.x, self.y = self.rect.topleft
        return self.rect

    def kill(self) -> "Sprite":
        """
        Mark sprite as dead (not drawn or updated).
        """
        self.alive = False
        return self

    def update(self) -> None:
        """
        Call custom update function or draw by default.
        """
        if not self.force_update:
            if self.alive:
                self.draw()
                if self.update_func:
                    self.update_func()
        else:
            if self.update_func:
                self.update_func()

    def set_animation(self, name: str, frames: List[pygame.Surface], speed: float = 0.1, loop: bool = True) -> "Sprite":
        """
        Register a new animation for the sprite.
        """
        self.animations[name] = {
            "frames": frames,
            "index": 0,
            "speed": speed,
            "timer": 0,
            "loop": loop,
        }
        if not self.current_animation:
            self.current_animation = name
            self.original_img = frames[0]
            self.rect_update()
        return self

    def play_animation(self, name: Optional[str] = None) -> None:
        """
        Play or update animation each frame.
        """
        if not self.animations:
            return
        if name and name != self.current_animation:
            self.current_animation = name
            self.animations[name]["index"] = 0
            self.animations[name]["timer"] = 0
            self.original_img = self.animations[name]["frames"][0]
            self.rect_update()
            return
        anim = self.animations[self.current_animation] # type: ignore
        dt = self.engine.dt # type: ignore
        anim["timer"] += dt
        if anim["timer"] >= anim["speed"]:
            anim["timer"] = 0
            anim["index"] += 1
            if anim["index"] >= len(anim["frames"]):
                if anim["loop"]:
                    anim["index"] = 0
                else:
                    anim["index"] = len(anim["frames"]) - 1
            self.img = anim["frames"][anim["index"]]
            self.rect_update()

    @staticmethod
    def create_image(path: str = "", width: Optional[int] = None, height: Optional[int] = None) -> pygame.Surface:
        """
        Returns pygame.Surface object, rendered from path.
        """
        img = pygame.image.load(path).convert_alpha()
        if width and height:
            img = pygame.transform.scale(img, (width, height))
        return img

class Group:
    """
    Container for managing multiple Sprite objects.

    Provides:
        * drawing
        * updating
        * movement
        * scaling
        * rotation
        * collision checks
    """

    def __init__(self, *sprites: Sprite) -> None:
        """
        Initialize a group of sprites.
        """
        self.sprites: List[Sprite] = list(sprites)
        Sprite._counter += 1
        self.layer: int = Sprite._counter

    def add(self, *sprites: Sprite) -> "Group":
        """
        Add sprites to the group.
        """
        for sprite in sprites:
            if sprite not in self.sprites:
                self.sprites.append(sprite)
        return self

    def remove(self, *sprites: Sprite) -> "Group":
        """
        Remove sprites from the group.
        """
        for sprite in sprites:
            if sprite in self.sprites:
                self.sprites.remove(sprite)
        return self

    def draw(self) -> "Group":
        """
        Draw all sprites in the group.
        """
        for sprite in self.sprites:
            sprite.draw()
        return self

    def update(self) -> "Group":
        """
        Update all sprites in the group.
        """
        self.sprites.sort(key=lambda o: getattr(o, "layer", 0))
        for sprite in self.sprites:
            sprite.draw()
            sprite.update()
        return self

    def move(self, dx: Optional[float] = None, dy: Optional[float] = None) -> "Group":
        """
        Move all sprites in the group.
        """
        for sprite in self.sprites:
            sprite.move(dx if dx is not None else 0, dy if dy is not None else 0)
        return self

    def scale(self, width: int, height: int) -> "Group":
        """
        Scale all sprites in the group.
        """
        for sprite in self.sprites:
            sprite.scale(width, height)
        return self

    def rotate(self, angle: float) -> "Group":
        """
        Rotate all sprites in the group.
        """
        for sprite in self.sprites:
            sprite.rotate(angle)
        return self

    def kill(self) -> "Group":
        """
        Mark all sprites as dead.
        """
        for sprite in self.sprites:
            sprite.kill()
        return self

    def __iter__(self) -> Any:
        """
        Iterate over sprites.
        """
        return iter(self.sprites)

    def __len__(self) -> int:
        """
        Return number of sprites in the group.
        """
        return len(self.sprites)

    def __getitem__(self, idx: int) -> Sprite:
        """
        Return sprite at index.
        """
        return self.sprites[idx]

    def collide(self, sprite: Sprite) -> List[Sprite]:
        """
        Get list of sprites colliding with given sprite.
        """
        return [s for s in self.sprites if s.collide(sprite)]