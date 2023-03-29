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

class Font:
    menu = pygame.font.SysFont(None, 30)

class Sprite:
    @staticmethod
    def add_sprite_frame(frame_list, image, size = None):
        """Adds a sprite frame to the given list.

        Args:
            frame_list (list): List of sprite frames.
            image (str): Path to image file.
            size (tuple, optional): Desired size of the image. Defaults to None.
        """
        loaded_image = pygame.image.load(image)
        width_multiplier, height_multiplier = render.get_size_multiplier()
        if size:
            frame_list.append(pygame.transform.smoothscale(loaded_image, (size[0] * width_multiplier, size[1] * height_multiplier)))
        else:
            frame_list.append(pygame.transform.smoothscale(loaded_image, (loaded_image.get_width() * width_multiplier, loaded_image.get_height() * height_multiplier)))
    
    @staticmethod
    def add_sprite(name, image, size = None):
        """Adds a sprite to the class.

        Args:
            name (str): Name of the sprite.
            image (str): Path to image file.
            size (tuple, optional): Desired size of the image. Defaults to None.
        """
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
    """Exits the server and game."""
    pygame.quit()
    sys.exit()

# ----- Class -----

class Button:
    """Represents a button on the screen."""

    def __init__(self, text, pos, size, color, font, callback):
        """Initialize the button.

        Args:
            text (str): Text to display on the button.
            pos (tuple): Position of the button.
            size (tuple): Size of the button.
            color (tuple): Color of the button.
            font (pygame.font.Font): Used font of the button.
            callback (function): Function to execute when the button is clicked.
        """
        # Assigning button attributes
        self.text = text
        self.render_pos = render.get_render_pos(pos)
        self.game_pos = pos
        self.size = size
        self.color = color
        self.callback = callback
        
        # Create a surface for the button
        self.button_surface = pygame.Surface(self.size)
        self.button_surface.fill(self.color)
        
        # Render the button's text onto the surface
        text = font.render(self.text, True, (255, 255, 255))
        text_rect = text.get_rect(center=(self.size[0]/2, self.size[1]/2))
        self.button_surface.blit(text, text_rect)
        
        # Scale the button surface to match the screen resolution
        width_multiplier, height_multiplier = render.get_size_multiplier()
        self.button_surface = pygame.transform.smoothscale(self.button_surface, (self.button_surface.get_width() * width_multiplier, self.button_surface.get_height() * height_multiplier))
    
    def display(self):
        """Displays the button on the screen."""
        render.blit(self.button_surface, self.render_pos)

    def update(self, mouse_pos, mouse_down):
        """
        Updates the button state based on the mouse input.

        Args:
            mouse_pos (tuple): Current mouse position.
            mouse_down (tuple): Current mouse button states.
        """
        # Check if the mouse is hovering over the button and the left mouse button is down
        if pygame.Rect(*self.render_pos, *self.button_surface.get_size()).collidepoint(mouse_pos) and mouse_down[0]:
            self.callback()


class Scene:
    @classmethod
    def add_button(cls, button):
        """
        A class method which adds a button to the list of buttons in the Scene class.

        Args:
            button (Button): A Button instance to be added.
        """
        cls.buttons.append(button)


class World(Scene):
    buttons = []

    @classmethod
    def update(cls, mouse_pos, mouse_down):
        """
        A class method that updates all buttons in the World and then displays them.

        Args:
            mouse_pos (tuple): Current position of the mouse.
            mouse_down (tuple): Current state of the mouse buttons.
        """
        for button in cls.buttons:
            button.update(mouse_pos, mouse_down)
        
        cls.display()

    @classmethod
    def display(cls): 
        """
        A class method that displays all buttons in the World.
        """
        for button in cls.buttons:
            button.display()


class MainMenu(Scene):
    buttons = []
    enabled = True
    
    @classmethod
    def toggle(cls):
        """Toggles the enabled status of the MainMenu."""
        cls.enabled = not cls.enabled
    
    @classmethod
    def enable(cls):
        """Enables the MainMenu."""
        cls.enabled = True
    
    @classmethod
    def disable(cls):
        """Disables the MainMenu."""
        cls.enabled = False
    
    @classmethod
    def update(cls, mouse_pos, mouse_down):        
        """Updates the MainMenu.

        Args:
            mouse_pos (tuple): Current mouse position.
            mouse_down (tuple): Indicates if the mouse button is being pressed.
        """
        for button in cls.buttons:
            button.update(mouse_pos, mouse_down)
        
        cls.display()
               
    @classmethod
    def display(cls):
        """Displays the MainMenu."""
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
        """
        Initializes a Render object with the game resolution and the display resolution.

        Args:
            game_resolution (tuple): Game resolution.
        """
        self.screen = pygame.display.set_mode((self.DISPLAY_WIDTH, self.DISPLAY_HEIGHT), pygame.NOFRAME)
        pygame.display.set_caption("Shadow Fare")
        self.game_resolution = game_resolution
        
        self.WIDTH_MULTIPLIER = self.DISPLAY_WIDTH/GAME_WIDTH
        self.HEIGHT_MULTIPLIER = self.DISPLAY_HEIGHT/GAME_HEIGHT
    
    def blit(self, *image):
        """
        Adds an image to the queue of images to be blitted later.

        Args:
            *image (tuple): Tuple containing the surface to be blitted and its position.
        """
        self.queued_images.append(image)
    
    def scale_image(self, surface):
        pass
    
    def update(self):
        """
        Handles events and updates the display.
        """
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                exit()
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                exit()
    
    def display(self):
        """
        Blits all queued images and updates the display.
        """
        self.screen.fill(self.BACKGROUND_COLOR)
        
        for i, image in enumerate(self.queued_images):
            self.screen.blit(*image)
            
        pygame.display.update()
        self.queued_images = []
    
    def get_inputs(self):
        """
        Gets the mouse position and mouse button states.

        Returns:
            tuple: A tuple containing the mouse position and the mouse button states.
        """
        return pygame.mouse.get_pos(), pygame.mouse.get_pressed()

    def tick(self):
        """
        Waits for the appropriate amount of time to meet the target FPS.
        """
        clock.tick(FPS)
            
    def get_size_multiplier(self):
        """
        Returns the width and height multipliers for scaling game elements.
        """
        return (self.WIDTH_MULTIPLIER, self.HEIGHT_MULTIPLIER)
    
    def get_game_pos(self, pos):
        """
        Converts a screen position to a game position.

        Args:
            pos (tuple): The screen position.

        Returns:
            tuple: The game position.
        """
        pos = list(pos)
        pos[0] /= self.WIDTH_MULTIPLIER
        pos[1] /= self.HEIGHT_MULTIPLIER
        
        return pos
    
    def get_render_pos(self, pos):
        """
        Converts a game position to a screen position.

        Args:
            pos (tuple): The game position.

        Returns:
            tuple: The screen position.
        """
        pos = list(pos)
        pos[0] *= self.WIDTH_MULTIPLIER
        pos[1] *= self.HEIGHT_MULTIPLIER
        
        return pos
        
            
render = Render((GAME_WIDTH, GAME_WIDTH))

Sprite.add_sprite_frame(Sprite.Player.frames, "images/player/f0.png")
Sprite.add_sprite(Sprite.UI.Menu.Background, "images/UI/menu/Background.png", (GAME_WIDTH, GAME_HEIGHT))

button = Button("Play", (GAME_WIDTH / 2 - 100, 150), (200, 80), (255, 0, 0), Font.menu, MainMenu.toggle)
MainMenu.add_button(button)

button = Button("ll", (20, 20), (60, 60), (255, 0, 0), Font.menu, MainMenu.toggle)
World.add_button(button)

running = True
while running:
    mouse_pos, mouse_down = render.get_inputs()

    if MainMenu.enabled:
        MainMenu.update(mouse_pos, mouse_down)
    else:
        World.update(mouse_pos, mouse_down)
    
    render.update()
    render.display()