"""===== sound.py ====="""

import pygame

pygame.mixer.init()

class SoundManager:
    sounds = {}
    music_playing = False

    @staticmethod
    def load_sound(name, path):
        """Load sounds and give it a name"""
        SoundManager.sounds[name] = pygame.mixer.Sound(path)

    @staticmethod
    def play_sound(name, volume=1.0, count=1):
        """Play short sound"""
        if name in SoundManager.sounds:
            snd = SoundManager.sounds[name]
            snd.set_volume(volume)
            snd.play(count-1)
        else:
            from .utils import log

            log(f"Sound '{name}' not found", "SoundManager", True)
    
    @staticmethod
    def play_path_sound(path_or_bytes, volume=1.0, count=1):
        snd = pygame.mixer.Sound(path_or_bytes)
        snd.set_volume(volume)
        snd.play(count-1)

    @staticmethod
    def play_music(path, volume=1.0, loop=-1):
        """Play music in background"""
        pygame.mixer.music.load(path)
        pygame.mixer.music.set_volume(volume)
        pygame.mixer.music.play(loop)
        SoundManager.music_playing = True

    @staticmethod
    def stop_music():
        """Stops music, that is currently playing"""
        pygame.mixer.music.stop()
        SoundManager.music_playing = False

    @staticmethod
    def pause_music():
        """Pauses music"""
        pygame.mixer.music.pause()

    @staticmethod
    def continue_music():
        """Continues playing music"""
        pygame.mixer.music.unpause()

    @staticmethod
    def stop_all():
        """Stops all playing sounds"""
        pygame.mixer.stop()
        pygame.mixer.music.stop()
        SoundManager.music_playing = False
