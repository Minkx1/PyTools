"""
NovaEngine.
NovaEngine is the small framework for simplifying creating games with PyGame library.   
"""

import pygame
from .engine import NovaEngine
from .time import Time
from .utils import Colors, Utils
from .dev_tools import DevTools, log, get_globals
from .sprite import Sprite, Group
from .additional_sprites import *   
from .gui import *           
from .scenes import Scene
from .sound import SoundManager
from .saves import SaveManager

__author__ = "Minkx1"
__version__ = "1.9.2"

# формуємо __all__ з усього, що точно експортується
__all__ = [
    "NovaEngine",
    "Time",
    "Utils",
    "Colors",
    "DevTools",
    "log",
    "get_globals",
    "Sprite",
    "Group",
    "Scene",
    "SoundManager",
    "SaveManager",
]

from .additional_sprites import __all__ as _additional_sprites_all
from .gui import __all__ as _gui_all    

__all__.extend(_additional_sprites_all)
__all__.extend(_gui_all)

# приберемо дублікати
__all__ = list(dict.fromkeys(__all__))