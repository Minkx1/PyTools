import pygame, random
import pygame_engine as pge 

BLOCK_SIZE, COLS, ROWS = 20, 20, 20
SCREEN_W, SCREEN_H = 400, 400
Engine = pge.PyGameEngine((SCREEN_W, SCREEN_H), "Snake Game")

STARTED_GAME = True
GAME_SPEED = 0.18

class coord:
    __slots__ = ("x", "y")
    def __init__(self, x: int, y: int):
        self.x, self.y = x, y

    @property
    def pos(self): return self.x, self.y
    def mult(self, v): return coord(self.x*v, self.y*v)
    def __add__(self, o): return coord(self.x+o.x, self.y+o.y)
    def __eq__(self, o): return isinstance(o, coord) and self.pos == o.pos

class Snake(pge.Sprite):
    def __init__(self):
        super().__init__()

        self.score = 1
        self.body = [coord(random.randrange(ROWS), random.randrange(COLS))]
        self.speed = coord(0, 1)
        self.pending_direction = self.speed
        self.movement_cooldown = Engine.Time.Cooldown(GAME_SPEED).start()

        self.generate_apple()

        # eyes
        b = BLOCK_SIZE
        o, e = b//4, b//5
        self.eye_map = {
            ( 1, 0): [(b-o-e, o),          (b-o-e, b-o-e)],
            (-1, 0): [(o, o),              (o, b-o-e)],
            (0,  1): [(o, b-o-e),          (b-o-e, b-o-e)],
            (0, -1): [(o, o),              (b-o-e, o)]
        }

    # -----------------------------
    # APPLE
    # -----------------------------
    def generate_apple(self):
        while True:
            apple = coord(random.randrange(ROWS), random.randrange(COLS))
            if apple not in self.body:
                self.apple = apple
                return

    # -----------------------------
    # DRAW
    # -----------------------------
    def draw(self):
        ax, ay = self.apple.mult(BLOCK_SIZE).pos
        pygame.draw.rect(self.screen, "red", (ax, ay, BLOCK_SIZE, BLOCK_SIZE))

        for i, part in enumerate(self.body):
            px, py = part.mult(BLOCK_SIZE).pos
            pygame.draw.rect(self.screen, "green", (px, py, BLOCK_SIZE, BLOCK_SIZE))

            if i == 0:
                for ex, ey in self.eye_map[self.speed.pos]:
                    pygame.draw.rect(
                        self.screen,
                        "black",
                        (px + ex, py + ey, BLOCK_SIZE//5, BLOCK_SIZE//5)
                    )

    # -----------------------------
    # UPDATE
    # -----------------------------
    def update(self):
        self.draw()

        if not self.alive:
            Engine.set_active_scene(MENU)
            return
        dirs = {
            pygame.K_w: coord(0, -1), pygame.K_UP: coord(0, -1),
            pygame.K_s: coord(0, 1),  pygame.K_DOWN: coord(0, 1),
            pygame.K_a: coord(-1, 0), pygame.K_LEFT: coord(-1, 0),
            pygame.K_d: coord(1, 0),  pygame.K_RIGHT: coord(1, 0)
        }
        for k, d in dirs.items():
            if Engine.Input.key_hold(k):
                if not (d.x == -self.speed.x and d.y == -self.speed.y):
                    self.pending_direction = d
                break

        # --- MOVEMENT ---
        if not self.movement_cooldown.check():
            return

        self.movement_cooldown.start()
        self.speed = self.pending_direction
        new_head = self.body[0] + self.speed

        if new_head == self.apple:
            self.body = [new_head] + self.body
            self.score += 1
            self.generate_apple()
            return

        # collision
        if (
            new_head in self.body or
            not (0 <= new_head.x < COLS) or
            not (0 <= new_head.y < ROWS)
        ):
            self.kill()
            return

        # normal movement
        self.body = [new_head] + self.body[:-1]

MAIN = pge.Scene()
with MAIN.content:
    snake = Snake()

MENU = pge.Scene()
@MENU.define
def menu():
    global STARTED_GAME, snake
    Engine.screen.fill("white" if STARTED_GAME else "black")

    if STARTED_GAME:
        pge.render_text("PRESS [ SPACE ] TO START", SCREEN_W/2, SCREEN_H/2, size=32, center=True, color="black")
        if Engine.Input.key_pressed(pygame.K_SPACE):
            STARTED_GAME = False
            Engine.set_active_scene(MAIN)
    else:
        pge.render_text(f"YOU DIED. SCORE: {snake.score}", SCREEN_W/2, SCREEN_H/2-25, size=28, center=True, color="red")
        pge.render_text("PRESS [ SPACE ] TO RESTART", SCREEN_W/2, SCREEN_H/2+25, size=20, center=True, color="red")
        if Engine.Input.key_pressed(pygame.K_SPACE):
            snake = Snake()
            MAIN.objects = [snake]
            Engine.set_active_scene(MAIN)

Engine.run(MENU)
