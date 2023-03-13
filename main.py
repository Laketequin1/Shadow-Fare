# ----- Setup ------
import pygame, os, sys, random
pygame.init()

# Imports lots of colors as RGB
from src import color as Color

os.system("cls")

# ----- Constant Variables -----
FPS = 120

GAME_WIDTH = 1920
GAME_HEIGHT = 1080

class Sprite:
    @staticmethod
    def add_sprite_frame(frame_list, image, size = None):
        loaded_image = pygame.image.load(image)
        width_multiplier, height_multiplier = render.get_size_multiplier()
        if size:
            frame_list.append(pygame.transform.smoothscale(loaded_image, (size[0] * width_multiplier, size[1] * height_multiplier)))
        else:
            frame_list.append(pygame.transform.smoothscale(loaded_image, (loaded_image.get_width() * width_multiplier, loaded_image.get_height() * height_multiplier)))
    
    @staticmethod
    def add_sprite(name, image, size = None):
        loaded_image = pygame.image.load(image)
        width_multiplier, height_multiplier = render.get_size_multiplier()
        if size:
            setattr(name, "image", pygame.transform.smoothscale(loaded_image, (size[0] * width_multiplier, size[1] * height_multiplier)))
        else:
            setattr(name, "image", pygame.transform.smoothscale(loaded_image, (loaded_image.get_width() * width_multiplier, loaded_image.get_height() * height_multiplier)))
    
    class Player:
        frames = []
    
    class Guns:
        class Shotgun:
            frames = []
    
    class UI:
        class Menu:
            class Background:
                image = None
            
        
# ----- Variables -----
clock = pygame.time.Clock()

# ----- Function ------
def exit():
    # Exit server here
    pygame.quit()
    sys.exit()

# ----- Class -----

class Button:
    def __init__(self, text, pos, size, color, callback):
        self.text = text
        self.render_pos = render.get_render_pos(pos)
        self.game_pos = pos
        self.size = size
        self.color = color
        self.callback = callback
        
        self.button_surface = pygame.Surface(self.size)
        self.button_surface.fill(self.color)
        
        font = pygame.font.SysFont(None, 24)
        text = font.render(self.text, True, (255, 255, 255))
        text_rect = text.get_rect(center=(self.size[0]/2, self.size[1]/2))
        
        self.button_surface.blit(text, text_rect)
        
        width_multiplier, height_multiplier = render.get_size_multiplier()
        self.button_surface = pygame.transform.smoothscale(self.button_surface, (self.button_surface.get_width() * width_multiplier, self.button_surface.get_height() * height_multiplier))
    
    def display(self):
        render.blit(self.button_surface, self.render_pos)

    def update(self, mouse_pos, mouse_down):
        if pygame.Rect(*self.render_pos, *self.button_surface.get_size()).collidepoint(mouse_pos) and mouse_down[0]:
            self.callback(mouse_pos)


class MainMenu:
    enabled = True
    buttons = []
    
    @classmethod
    def toggle(cls):
        cls.enabled = not cls.enabled
    
    @classmethod
    def enable(cls):
        cls.enabled = True
    
    @classmethod
    def disable(cls):
        cls.enabled = False
    
    @classmethod
    def add_button(cls, button):
        cls.buttons.append(button)
    
    @classmethod
    def update(cls):
        if cls.enabled:
            mouse_pos = pygame.mouse.get_pos()
            mouse_down = pygame.mouse.get_pressed()
            
            for button in cls.buttons:
                button.update(mouse_pos, mouse_down)
            
            cls.display()
               
    @classmethod
    def display(cls):
        render.blit(Sprite.UI.Menu.Background.image, (0, 0))
        
        for button in cls.buttons:
            button.display()


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
    
    def scale_image(self, surface):
        pass
    
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
            
    def get_size_multiplier(self):
        return (self.WIDTH_MULTIPLIER, self.HEIGHT_MULTIPLIER)
    
    def get_game_pos(self, pos):
        pos = list(pos)
        pos[0] /= self.WIDTH_MULTIPLIER
        pos[1] /= self.HEIGHT_MULTIPLIER
        
        return pos
    
    def get_render_pos(self, pos):
        pos = list(pos)
        pos[0] *= self.WIDTH_MULTIPLIER
        pos[1] *= self.HEIGHT_MULTIPLIER
        
        return pos
        
            
render = Render((GAME_WIDTH, GAME_WIDTH))

Sprite.add_sprite_frame(Sprite.Player.frames, "images/player/f0.png")
Sprite.add_sprite(Sprite.UI.Menu.Background, "images/UI/menu/Background.png", (GAME_WIDTH, GAME_HEIGHT))

def test(x):
    print(f"Button clicked: {x}")
    button.button_surface.fill((0, random.randint(1, 255), 0))

button = Button("Click me!", (GAME_WIDTH / 2 - 100, 150), (200, 80), (255, 0, 0), test)
MainMenu.add_button(button)

running = True
while running:
    MainMenu.update()
    
    render.update()
    render.display()