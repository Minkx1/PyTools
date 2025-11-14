import novaengine as nova
import pygame, random

BLOCK_SIZE, ROWS, COLS = 25, 25, 25
SCREEN_W, SCREEN_H = BLOCK_SIZE*COLS, BLOCK_SIZE*ROWS + 150

Engine = nova.NovaEngine((SCREEN_W, SCREEN_H), "Snake").set_debug(True)
saver = nova.SaveManager(False, "saves/snake/")
Engine.max_score = saver.get_value("Engine.max_score") or 0

class coord:
    def __init__(self, x: int, y: int) -> None:
        self.x, self.y = x, y
    @property
    def pos(self) -> tuple[int, int]:
        return (self.x, self.y)
    
    def mult(self, val: int) -> "coord":
        x, y = self.x*val, self.y*val
        return coord(x, y)
    
    def div(self, val: int) -> "coord":
        x, y = self.x//val, self.y//val
        return coord(x, y)
    
    @staticmethod
    def list_decoordinate(list: list["coord"]) -> list[tuple]:
        new_list = []
        for c in list:
            new_list.append(c.pos)
        return new_list

    def __add__(self, other: "coord"):
        return coord(self.x+other.x, self.y+other.y)

    def __str__(self):
        return f"({self.x};{self.y}"

    def __eq__(self, other: object) -> bool:
        return isinstance(other, coord) and self.pos == other.pos

class Snake(nova.Sprite):    
    def __init__(self) -> None:
        super().__init__(None)
        self.score = 1
        self.head = coord(random.randrange(0, ROWS-1), random.randrange(0, COLS-1))
        self.body = [self.head]
        self.movement_cooldown = nova.Time.Cooldown(0.2).start()
        
        self.speed = coord(0, 1)
        self.generate_apple()
    
    def generate_apple(self):
        while True:
            new_apple = coord(random.randrange(0, ROWS), random.randrange(0, COLS))
            if new_apple not in self.body:
                self.apple = new_apple
                break

    def draw(self):  # type: ignore
        _apple = self.apple.mult(BLOCK_SIZE)
        pygame.draw.rect(self.surface, "red", (_apple.x, _apple.y, BLOCK_SIZE, BLOCK_SIZE))

        for i, part in enumerate(self.body):
            _part = part.mult(BLOCK_SIZE)
            pygame.draw.rect(self.surface, "green", (_part.x, _part.y, BLOCK_SIZE, BLOCK_SIZE))

            if i == 0:
                eye_size = BLOCK_SIZE // 5
                offset = BLOCK_SIZE // 4

                # eyes
                if self.speed.x == 1:  
                    eyes = [
                        (_part.x + BLOCK_SIZE - offset - eye_size, _part.y + offset),
                        (_part.x + BLOCK_SIZE - offset - eye_size, _part.y + BLOCK_SIZE - offset - eye_size)
                    ]
                elif self.speed.x == -1:
                    eyes = [
                        (_part.x + offset, _part.y + offset),
                        (_part.x + offset, _part.y + BLOCK_SIZE - offset - eye_size)
                    ]
                elif self.speed.y == 1:
                    eyes = [
                        (_part.x + offset, _part.y + BLOCK_SIZE - offset - eye_size),
                        (_part.x + BLOCK_SIZE - offset - eye_size, _part.y + BLOCK_SIZE - offset - eye_size)
                    ]
                else:  
                    eyes = [
                        (_part.x + offset, _part.y + offset),
                        (_part.x + BLOCK_SIZE - offset - eye_size, _part.y + offset)
                    ]

                for ex, ey in eyes:
                    pygame.draw.rect(self.surface, "black", (ex, ey, eye_size, eye_size))

        if not self.alive:
            nova.Utils.render_text("YOU ARE DEAD", SCREEN_W/2, SCREEN_H/2-45, font="Arial", size=96, color=nova.Colors.RED, center=True)
            nova.Utils.render_text("Press [SPACE] to retry.", SCREEN_W/2, SCREEN_H/2+45, font="Arial", size=36, color=nova.Colors.RED, center=True)
            if Engine.key_pressed(pygame.K_SPACE):
                self = self.__init__()

    def update(self):
        self.draw()
        if self.alive:
            def key_input() -> None:
                if (self.engine.key_hold(pygame.K_w) or self.engine.key_hold(pygame.K_UP) ):
                    if self.speed.pos!=coord(0, 1).pos:
                        self.speed = coord(0, -1)
                        return
                if self.engine.key_hold(pygame.K_s) or self.engine.key_hold(pygame.K_DOWN):
                    if self.speed.pos!=coord(0, -1).pos:
                        self.speed = coord(0, 1)
                        return
                if self.engine.key_hold(pygame.K_a) or self.engine.key_hold(pygame.K_LEFT):
                    if self.speed.pos!=coord(1, 0).pos:
                        self.speed = coord(-1, 0)
                        return
                if self.engine.key_hold(pygame.K_d) or self.engine.key_hold(pygame.K_RIGHT):
                    if self.speed.pos!=coord(-1, 0).pos:
                        self.speed = coord(1, 0)
                        return
            key_input()

            if self.movement_cooldown.check():
                self.movement_cooldown.start()

                head = self.body[0]
                new_head = head + self.speed
                if new_head == self.apple:
                    self.generate_apple()
                    self.body.insert(0, new_head)
                    self.score += 1
                    return
                else:
                    if (new_head in self.body) or (new_head.x<0 or new_head.x>COLS-1 or new_head.y<0 or new_head.y>ROWS-1):
                        self.kill()
                    else:
                        self.body.pop()
                        self.body.insert(0, new_head)

Main = nova.Scene()

with Main.set_objects():
    snake = Snake()

@Main.set_loop()
def main_update():   
    # drawing grid
    nova.Utils.fill_background(nova.Colors.BLACK)
    Main.update()

    pygame.draw.rect(Engine.screen, "white", (0, 0, SCREEN_W, ROWS*BLOCK_SIZE), 1)
    pygame.draw.rect(Engine.screen, "white", (0, 0, SCREEN_W, SCREEN_H), 1)
    nova.Utils.render_text(f"Score: {snake.score}", SCREEN_W//2, (SCREEN_H+COLS*BLOCK_SIZE)//2-20, size=48, color=(255, 255, 255), center=True)
    nova.Utils.render_text(f"Max Score: {Engine.max_score}", SCREEN_W//2, (SCREEN_H+COLS*BLOCK_SIZE)//2+20, size=48, color=(255, 255, 255), center=True)
    if snake.score > Engine.max_score:
        Engine.max_score = snake.score

saver.set_vars(["Engine.max_score"])

Engine.run(save_manager=saver)