# ----- Setup ------
import pygame, os, sys
pygame.init()

# Imports lots of colors as RGB
from src import color

os.system("cls")

# ----- Constant Variables -----
FPS = 60

GAME_WIDTH = 1920
GAME_HEIGHT = 1080

class Sprite:
    class player:
        f0 = pygame.image.load("images/player/frame0.png")
    pass

# ----- Variables -----
clock = pygame.time.Clock()

# ----- Function ------
def exit():
    pygame.quit()
    sys.exit()
    
# ----- Class -----

class Render:
    info = pygame.display.Info()
    DISPLAY_WIDTH = info.current_w
    DISPLAY_HEIGHT = info.current_h
    
    print(DISPLAY_WIDTH, DISPLAY_HEIGHT)
    
    def __init__(self, game_resolution: tuple[int, int]):
        self.display = pygame.display.set_mode((self.DISPLAY_WIDTH, self.DISPLAY_HEIGHT), pygame.NOFRAME)
        self.game_resolution = game_resolution
        
        self.WIDTH_MULTIPLIER = self.DISPLAY_WIDTH/GAME_WIDTH
        self.HEIGHT_MULTIPLIER = self.DISPLAY_HEIGHT/GAME_HEIGHT
