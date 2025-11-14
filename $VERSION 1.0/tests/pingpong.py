import pygame
import random
from tests.__nova_setup__ import novaengine as nova

SCREEN_W, SCREEN_H = (750, 500)

app = nova.NovaEngine((SCREEN_W, SCREEN_H), "NovaTest", "assets/icon.png", 60).set_debug(True)

class Panel(nova.Sprite):
    def __init__(self, img_path, width = None, height = None, movement="w"):
        super().__init__(img_path, width, height, solid=True)
        self.movement = movement
        self.speed = 10
        self.ball = None
        
        if self.movement=="w":
            self.x = 20
            self.place_centered(self.x+self.width/2, SCREEN_H/2)
        elif self.movement=="^":
            self.x = SCREEN_W-20
            self.place_centered(self.x-self.width/2, SCREEN_H/2)

    def draw(self):
        if self.img: super().draw()
        else:
            pygame.draw.rect(self.surface, (0,0,0), (self.x, self.y, self.width, self.height))

    def update(self):
        if self.alive:
            self.draw()

            dy = 0
            if self.movement == "w":
                if self.engine.KeyHold(pygame.K_w): dy -= self.speed
                if self.engine.KeyHold(pygame.K_s): dy += self.speed
            elif self.movement == "^":
                if self.engine.KeyHold(pygame.K_UP): dy -= self.speed
                if self.engine.KeyHold(pygame.K_DOWN): dy += self.speed

            self.move(0, dy)
            self.stay_in_rect(self.surface.get_rect())

            # if not self.ball:
            #     for obj in self.engine.get_scene().objects:
            #         if isinstance(obj, Ball):
            #             self.ball = obj

class Ball(nova.Sprite):
    def __init__(self, img_path=None, width = None, height = None, vel_x=5, vel_y=5):
        super().__init__(img_path, width, height, False)

        self.vel_x, self.vel_y = vel_x, vel_y
        self.radius = 15
        self.height = 2*self.radius
        self.width = 2*self.radius
        # self.set_collide_immunity(0.1)
    
    def draw(self):
        self.rect = pygame.draw.circle(self.surface, (255, 0, 0), (self.x+self.width/2, self.y+self.height/2), self.radius)

    def update(self):
        if self.alive:
            self.draw()
            self.move(self.vel_x, self.vel_y)
            self.stay_in_rect(self.surface.get_rect())

            if self.collide_any(solids=True):
                self._change_direction()

            if self.y - self.radius <= 0 or self.y + self.radius >= SCREEN_H:
                self.vel_y = -self.vel_y  # змінюємо напрямок по Y

    def _change_direction(self):
        rand_delta = random.choice([-1, 1])
        self.vel_x = -self.vel_x + rand_delta
        self.vel_y = -self.vel_y + rand_delta
        
        # cap
        cap_x = [3, 7]
        cap_y = [3, 7] 
        if self.vel_x != 0:
            x_sym = abs(self.vel_x)/self.vel_x
            if abs(self.vel_x) < cap_x[0]: self.vel_x = x_sym*cap_x[0]
            elif abs(self.vel_x) > cap_x[1]: self.vel_x = x_sym* cap_x[1]
        if self.vel_y != 0:
            y_sym = abs(self.vel_y)/self.vel_y
            if abs(self.vel_y) < cap_y[0]: self.vel_y = y_sym*cap_y[0]
            elif abs(self.vel_y) > cap_y[1]: self.vel_y = y_sym* cap_y[1]

class Wall(nova.Sprite):
    def __init__(self, img_path=None, width = 3, height = SCREEN_H,color=(255, 0, 0), score=0):
        super().__init__(img_path, width, height, solid=True)
        self.score = score
        self.color = color
        self.ball = None
        
        self.cd = nova.Time.Cooldown(1.5)

    def update(self):
        self.rect = pygame.draw.line(self.surface, self.color, (self.x, 0), (self.x, self.height), self.width)
        if self.collide_any():
            if self.cd.check():
                self.cd.start()
                self.score += 1

s = nova.Scene()
with s.sprites():

    ball = Ball(vel_x=random.choice([-1, 1])*random.randint(3, 5), vel_y=random.choice([-1, 1])*random.randint(3, 5)).place_centered(SCREEN_W/2, SCREEN_H/2)
    
    l_pan = Panel(None, 50, 200, "w")
    r_pan = Panel(None, 50, 200, "^") 

    left_wall = Wall()
    right_wall = Wall(color=nova.Colors.BLUE).set_position(SCREEN_W-1)

    app.score = f"{right_wall.score} : {left_wall.score}"

    score = nova.TextLabel(size=30, center=True).place_centered(SCREEN_W/2, 50)
    score.bind("app.score")

@s.function()
def s_u():
    s.update()
    app.score = f"{right_wall.score} : {left_wall.score}"

app.run()