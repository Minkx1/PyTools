"""===== additional_classes.py ====="""

import pygame
from .sprite import Sprite
from .gui import TextLabel

__all__ = ["ProgressBar", "Projectile", "Dummy", "Rect", "Popup"]

class ProgressBar(Sprite):
    def __init__(
        self,
        width,
        height,
        max_value=100,
        start_value=0,
        bg_color=(50, 50, 50),
        fill_color=(0, 200, 0),
        border_color=(0, 0, 0),
        border_width=2,
    ):
        """
        Клас прогрес-бара
        :param x, y: позиція
        :param width, height: розміри
        :param max_value: максимальне значення
        :param value: початкове значення
        :param bg_color: колір фону
        :param fg_color: колір прогресу
        :param border_color: колір рамки
        :param border_width: товщина рамки
        """
        super().__init__(None, width, height)

        self.max_value = max_value
        self.value = start_value

        self.bg_color = bg_color
        self.fg_color = fill_color
        self.border_color = border_color
        self.border_width = border_width

    def set_value(self, value):
        """Встановити значення прогрес-бара"""
        self.value = max(0, min(self.max_value, value))
    
    def set_max_value(self, max_value):
        """Встановити максимальне значення прогрес-бара"""
        self.max_value = max_value

    def add_value(self, delta):
        """Додати/відняти значення"""
        self.set_value(self.value + delta)

    def draw(self):
        """Draws progress-bar on the screen"""
        if self.alive:
            # bg
            pygame.draw.rect(self.surface, self.bg_color, self.rect)
            # filled
            fill_w = int((self.value / self.max_value) * self.width)
            pygame.draw.rect(
                self.surface,
                self.fg_color,
                (self.rect.x, self.rect.y, fill_w, self.height),
            )
            # Border
            if self.border_width > 0:
                pygame.draw.rect(
                    self.surface,
                    self.border_color,
                    (self.rect.x, self.rect.y, self.width, self.height),
                    self.border_width,
                )

            # text
            from .utils import Utils
            Utils.render_text(
                f"{self.value} / {self.max_value}",
                self.rect.centerx,
                self.rect.centery,
                center=True
            )


class Projectile(Sprite):
    def __init__(
        self,
        img_path,
        width=None,
        height=None,
        start=None,
        target=None,
        speed: int = 100,
    ):
        super().__init__(img_path, width, height)
        self.start = start
        self.target = target
        self.speed = speed

        try:
            sx, sy = start[0], start[1]
            self.place_centered(sx, sy)
        except Exception as e:
            print(f"[NovaEngine] Error: {e}")

        try:
            self.look_at(pygame.mouse.get_pos())
        except Exception as e:
            print(f"[NovaEngine] Error: {e}")

    def update(self):
        if not self.collide(rect=self.engine.screen.get_rect()):
            self.kill()
        self.draw()
        self.move_angle(50)


class Dummy(Sprite):
    def __init__(self):
        super().__init__(img_path=None, width=0, height=0, solid=False)


class Rect(Sprite):

    def __init__(self, color=(0,0,0), border=0, rect=(0,0,0,0), solid = False):
        super().__init__(None, width=0, height=0, solid=solid)

        self.color = color
        self.border = border
        self.rect = pygame.Rect(rect[0], rect[1], rect[2], rect[3])
    
    def update(self):
        pygame.draw.rect(self.engine.screen, self.color, self.rect, self.border)


class Popup(TextLabel):
    def __init__(self, text="", time=3, font="TimesNewRoman", size=16, color=(0,0,0), center=True):
        super().__init__(text, font, size, color, center)
        from .time import Time

        self.time = time
        self.cd = Time.Cooldown(self.time)
        self.cd.start()

    def update(self):
        if self.alive: super().draw()
        if self.cd.check(): 
            self.kill()

