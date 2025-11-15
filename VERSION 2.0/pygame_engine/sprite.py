import pygame
from .utils import log, get_engine

class Sprite:
    """Main class for creating objects in game."""
    def __init__(self, img_path: str | None = None, size: tuple[float, float] | None = None) -> None:
        self.engine = get_engine()
        if self.engine == None:
            log("Engine IS NOT initialized! Please initialize PyGameEngine before.", error=True)
            raise PermissionError
            
        self.screen = self.engine.screen
        
        self.original_img:pygame.Surface | None = pygame.image.load(img_path).convert_alpha() if img_path else None
        self.size = None
        if size and self.original_img:
            self.size = size
            self.original_img = pygame.transform.scale(self.original_img, size)
        self.original_rect = self.original_img.get_rect() if self.original_img else pygame.Rect(0, 0, 0, 0)
        
        self.x, self.y = (0, 0)
        self.alive = True
    
    @property
    def pos(self):
        return (self.x, self.y)

    def draw(self):
        if self.alive:
            if self.original_img: 
                self.screen.blit(self.original_img, self.pos) 
    
    def move(self, dx, dy):
        self.x += dx; self.y += dy
    
    def place(self, x: int, y: int, centred:bool = False):
        if centred:
            if self.original_rect:
                self.original_rect.center = (x, y)
                self.x, self.y = self.original_rect.topleft
            else:
                self.x, self.y = x, y
        else:
            self.x, self.y = x, y
            
    def kill(self):
        self.alive = False

    def update(self):
        self.draw()
    
    def __str__(self) -> str:
        return f"Sprite object, position: {self.pos}"