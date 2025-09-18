from _nova_setup import novaengine as nova 
import pygame, random

SCREEN_W, SCREEN_H = 900, 600

Engine = nova.NovaEngine(window_size=(SCREEN_W, SCREEN_H)) # initialization of main Engine and Window

asset_dir = "C:/Users/user/Desktop/Personal/Programming/PythonProjects/NovaEngine/assets"

Main = nova.Scene() # Creating Main scene, that contains Sprites in itself and Main's loop function will be called in game-cycle

# Initializing sprites in Main and Menu scenes
with Main.init():
    test = nova.Sprite(f"{asset_dir}/player.png", 100, 100).place_centered(450, 300)
    cool = nova.Time.Cooldown(0.1)
    @test.set_update()
    def _():
        test.look_at(pygame.mouse.get_pos())
        if cool.check():
            test.move(random.randrange(-5, 5), random.randrange(-5, 5))
            cool.start()

Engine.run() 