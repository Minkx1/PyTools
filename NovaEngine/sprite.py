"""===== sprite.py =====
Module for managing 2D sprites with Pygame.

Provides the Sprite class for handling transformations,
drawing, collisions, and animations, and a Group class
for batch management of multiple sprites.
"""

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

    # Counter for ordering sprite initialization
    _counter = 0

    def __init__(
        self,
        img_path: str,
        width: float | None = None,
        height: float | None = None,
        solid: bool = False,
    ):
        """
        Initialize a new Sprite.

        Args:
            img_path (str): Path to image file.
            width (float | None): Optional width for scaling.
            height (float | None): Optional height for scaling.
            solid (bool): Whether sprite is solid (collidable).
        """
        from .core import NovaEngine
        from .time import Time

        self.engine = NovaEngine.Engine
        self.surface = self.engine.screen
        self.solid = solid
        self.alive = True

        self.force_update = False
        self.update_func = None

        self.debug_color = (
            random.randint(0, 255),
            random.randint(0, 255),
            random.randint(0, 255),
        )
        self.debug = self.engine.debug

        Sprite._counter += 1
        self.layer = Sprite._counter

        # Load original image (keep for transformations)
        if img_path:
            self.original_img = pygame.image.load(img_path).convert_alpha()
            if width and height:
                self.original_img = pygame.transform.scale(
                    self.original_img, (width, height)
                )
        else:
            if width and height:
                self.original_img = pygame.Surface((width, height))
            else:
                self.original_img = pygame.Surface((0, 0))

        self.width = self.original_img.get_width()
        self.height = self.original_img.get_height()

        self.collide_immun_time = 0.1
        self.collide_immun = Time.Cooldown(self.collide_immun_time)

        # Current image (may be transformed)
        self.img = self.original_img
        self.angle: float = 0
        self.rect = self.img.get_rect()
        self.x, self.y = self.rect.topleft
        self.scaling_size = (self.width, self.height)

        # Animations
        self.animations: dict[str, dict] = {}
        self.current_animation: str | None = None

    def set_collide_immunity(self, duration):
        from .time import Time
        self.collide_immun_time = duration
        self.collide_immun = Time.Cooldown(self.collide_immun_time)
    
    def set_layer(self, layer):
        self.layer = layer
        return self

    def change_layer(self, value:int = None):
        self.layer += value or 1
        return self

    def draw(self):
        """
        Draw sprite to the screen surface.

        Returns:
            Sprite: Returns self for chaining.
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

    def hover(self, special_point: tuple[float, float] = None):
        """
        If sprite's rect is hovered by mouse, returns True.
        Else, returns False.
        """
        val = self.rect.collidepoint(pygame.mouse.get_pos())
        if special_point:
            try: 
                val = self.rect.collidepoint(special_point)
            except Exception as e:
                from .utils import log
                log(e, "Sprite | Hover", True)

        return val

    def set_update(self, force=False):
        """
        Decorator to set custom update logic for the sprite.

        Returns:
            Callable: The decorated function.
        """

        def decorator(func):
            self.force_update = force
            self.update_func = func
            return func

        return decorator

    def set_position(self, x: float | None = None, y: float | None = None):
        """
        Set top-left position of the sprite.
        """
        if x is not None:
            self.x = x
        if y is not None:
            self.y = y
        self.rect.topleft = (self.x, self.y)
        return self

    def place_centered(self, x: float, y: float):
        """
        Set sprite's cetner coordinates. 
        """
        self.rect.center = (x, y)
        self.x, self.y = self.rect.topleft
        return self

    def move(self, dx: float = 0, dy: float = 0):
        """
        Move sprite by (dx, dy).
        """
        self.rect.move_ip(dx, dy)
        self.x, self.y = self.rect.topleft
        return self

    def move_to(self, target, speed: float):
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
            self.rect.x += dx * speed * self.engine.dt
            self.rect.y += dy * speed * self.engine.dt

    def move_angle(self, speed: float):
        """
        Moves Sprite with its angle(basic angle is 0 deg)
        """
        ang = self.angle + 90
        dx = math.sin(math.radians(ang)) * speed
        dy = math.cos(math.radians(ang)) * speed

        self.move(dx, dy)

    def scale(self, width: int, height: int):
        """
        Scale sprite to (width, height).
        """
        self.scaling_size = (width, height)
        return self

    def stay_in_rect(self, rect: pygame.Rect):
        """
        Clamp sprite inside the given rect.
        """
        self.rect.clamp_ip(rect)
        return self

    def rotate(self, angle: float):
        """
        Makes Sprite.angle equal to angle argument.
        In basic Sprite.draw() original sprite's img is rotated by the sprite.angle.
        """
        self.angle = (self.angle - angle) % 360
        return self

    def look_at(self, target):
        """
        Rotate sprite to face target.
        """
        if isinstance(target, Sprite):
            tx, ty = target.rect.center
        else:
            tx, ty = target

        dx, dy = tx - self.rect.centerx, ty - self.rect.centery
        self.angle = -math.degrees(math.atan2(dy, dx))

    def collide(self, other: "Sprite" = None, rect: pygame.Rect = None) -> bool:
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

    def collide_any(self, solids=False):
        """
        If Sprite's rect collides with any other sprite's rect in the scene : returns True 
        """
        if self.collide_immun.check():
            self.collide_immun.start()
            scene = self.engine.get_scene()      
            objs = scene.objects
            if solids:
                objs = scene.solids

            for sp in objs:
                if sp != self:
                    if self.rect.colliderect(sp.rect):
                        return True
        return False

    def rect_update(self):
        """
        Update the rect based on the current image size.
        """
        self.rect = self.img.get_rect(topleft=self.rect.topleft)
        self.x, self.y = self.rect.topleft
        return self.rect

    def kill(self):
        """
        Mark sprite as dead (not drawn or updated).

        Returns:
            Sprite: Returns self for chaining.
        """

        self.alive = False
        return self

    def update(self):
        """
        Call custom update function or draw by default.
        """
        
        if not self.force_update:
            if self.alive:
                self.draw()
                if self.update_func:
                    self.update_func()
        else:
            self.update_func()

    # ====== ANIMATIONS ======
    def set_animation(self, name: str, frames: list, speed: float = 0.1, loop: bool = True):
        """
        Register a new animation for the sprite.

        Args:
            name (str): Animation name.
            frames (list): List of frame surfaces.
            speed (float): Time per frame.
            loop (bool): Whether animation loops.

        Returns:
            Sprite: Returns self for chaining.
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

    def play_animation(self, name: str | None = None):
        """
        Play or update animation each frame.

        Args:
            name (str | None): Switch to this animation if given.
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

        anim = self.animations[self.current_animation]
        dt = self.engine.dt

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
    def create_image(path: str = "", width: int | None = None, height: int | None = None):
        """
        Returns pygame.Surface object, rendered from path
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

    def __init__(self, *sprites: Sprite):
        """
        Initialize a group of sprites.

        Args:
            *sprites (Sprite): Sprites to add.
        """
        self.sprites: list[Sprite] = list(sprites)
        Sprite._counter += 1
        self.layer = Sprite._counter

    def add(self, *sprites: Sprite):
        """
        Add sprites to the group.

        Args:
            *sprites (Sprite): Sprites to add.

        Returns:
            Group
        """
        for sprite in sprites:
            if sprite not in self.sprites:
                self.sprites.append(sprite)
        return self

    def remove(self, *sprites: Sprite):
        """
        Remove sprites from the group.

        Args:
            *sprites (Sprite): Sprites to remove.

        Returns:
            Group
        """
        for sprite in sprites:
            if sprite in self.sprites:
                self.sprites.remove(sprite)
        return self

    def draw(self):
        """
        Draw all sprites in the group.

        Returns:
            Group
        """
        for sprite in self.sprites:
            sprite.draw()
        return self

    def update(self):
        """
        Update all sprites in the group.

        Returns:
            Group
        """
        self.sprites.sort(key=lambda o: getattr(o, "layer", 0))
        for sprite in self.sprites:
            sprite.draw()
            sprite.update()
        return self

    def move(self, dx: float = None, dy: float = None):
        """
        Move all sprites in the group.

        Args:
            dx (float): Change in X.
            dy (float): Change in Y.

        Returns:
            Group
        """
        for sprite in self.sprites:
            sprite.move(dx, dy)
        return self

    def scale(self, width: int, height: int):
        """
        Scale all sprites in the group.

        Args:
            width (int): New width.
            height (int): New height.

        Returns:
            Group: Returns self for chaining.
        """
        for sprite in self.sprites:
            sprite.scale(width, height)
        return self

    def rotate(self, angle: float):
        """
        Rotate all sprites in the group.

        Args:
            angle (float): Degrees to rotate.

        Returns:
            Group: Returns self for chaining.
        """
        for sprite in self.sprites:
            sprite.rotate(angle)
        return self

    def kill(self):
        """
        Mark all sprites as dead.

        Returns:
            Group: Returns self for chaining.
        """
        for sprite in self.sprites:
            sprite.kill()
        return self

    def __iter__(self):
        """Iterate over sprites."""
        return iter(self.sprites)

    def __len__(self):
        """Return number of sprites in the group."""
        return len(self.sprites)

    def __getitem__(self, idx: int):
        """Return sprite at index."""
        return self.sprites[idx]

    def collide(self, sprite: Sprite):
        """
        Get list of sprites colliding with given sprite.

        Args:
            sprite (Sprite): Sprite to check against.

        Returns:
            list[Sprite]: Colliding sprites.
        """
        return [s for s in self.sprites if s.collide(sprite)]
