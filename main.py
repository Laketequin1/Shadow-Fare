# ----- Setup ------
import pygame, os, sys
pygame.init()

# Imports lots of colors as RGB
from src import color as Color

os.system("cls")

# ----- Constant Variables -----
FPS = 120

GAME_WIDTH = 1920
GAME_HEIGHT = 1080

class Sprite:
    class Player:
        f0 = pygame.image.load("images/player/f0.png")
        
# ----- Variables -----
clock = pygame.time.Clock()

# ----- Function ------
def exit():
    # Exit server here
    pygame.quit()
    sys.exit()
    
# ----- Class -----

class Render:
    info = pygame.display.Info()
    DISPLAY_WIDTH = info.current_w
    DISPLAY_HEIGHT = info.current_h
    
    BACKGROUND_COLOR = Color.BLACK
    
    queued_images = []
    
    def __init__(self, game_resolution: tuple[int, int]):
        self.screen = pygame.display.set_mode((self.DISPLAY_WIDTH, self.DISPLAY_HEIGHT), pygame.NOFRAME)
        pygame.display.set_caption("Shadow Fare")
        self.game_resolution = game_resolution
        
        self.WIDTH_MULTIPLIER = self.DISPLAY_WIDTH/GAME_WIDTH
        self.HEIGHT_MULTIPLIER = self.DISPLAY_HEIGHT/GAME_HEIGHT

    def blit(self, *image):
        self.queued_images.append(image)
    
    def update(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                exit()
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                exit()
    
    def display(self):
        self.screen.fill(self.BACKGROUND_COLOR)
        for i, image in enumerate(self.queued_images):
            self.screen.blit(*image)
        pygame.display.update()
        self.queued_images = []
        
    def tick(self):
        clock.tick(FPS)
            
            
render = Render((GAME_WIDTH, GAME_WIDTH))

running = True
while running:
    render.update()
    render.blit(Sprite.Player.f0, (0, 0))
    render.display()