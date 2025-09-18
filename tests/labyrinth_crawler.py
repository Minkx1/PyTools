import pygame
import random
from _nova_setup import novaengine as nova

SCREEN_W, SCREEN_H = 640, 480

app = nova.NovaEngine((SCREEN_W, SCREEN_H), "Labyrinth Crawler", "assets/icon.png")

def generate_maze(width, height):
    maze = [[1 for _ in range(width)] for _ in range(height)]
    stack = [(1, 1)]
    maze[1][1] = 0

    while stack:
        x, y = stack[-1]
        directions = [(2, 0), (-2, 0), (0, 2), (0, -2)]
        random.shuffle(directions)

        moved = False
        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            if 1 <= nx < width-1 and 1 <= ny < height-1 and maze[ny][nx] == 1:
                maze[ny][nx] = 0
                maze[y + dy//2][x + dx//2] = 0
                stack.append((nx, ny))
                moved = True
                break

        if not moved:
            stack.pop()
    return maze

class Crawler(nova.Sprite):
    def __init__(self, img_path, width = None, height = None, speed = 5):
        super().__init__(img_path, width, height)
        self.speed = speed
    
    def update(self):
        if self.alive:
            self.draw()

            dx, dy = 0, 0
            if app.KeyHold(pygame.K_a): dx -= self.speed
            if app.KeyHold(pygame.K_d): dx += self.speed
            if app.KeyHold(pygame.K_w): dy -= self.speed
            if app.KeyHold(pygame.K_s): dy += self.speed

            self.in_bounds()

            self.move(dx, dy)

    def in_bounds(self):
        pass

Main = nova.Scene()
with Main.sprites():
    tile_size = 32

    player = Crawler("assets/hero.png", 32, 32).set_position(32, 32)

@Main.function()
def _():
    nova.Utils.fill_background((0, 0, 0))

    Main.update()

app.run()
