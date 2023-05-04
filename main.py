# ----- Setup ------
import pygame, os, sys, random, math
pygame.init()

# Imports lots of colors as RGB
from src import color as Color

# Clear screen
if os.name == "posix":
    os.system("clear")
else:
    os.system("cls")

# ----- Constant Variables -----
FPS = 120

GAME_WIDTH = 1920
GAME_HEIGHT = 1080

settings = {"ShowStats":True}

class Font:
    menu = pygame.font.SysFont(None, 100)
    symbol = pygame.font.SysFont(None, 80)
    debug = pygame.font.Font("fonts/RobotoMono.ttf", 60)
          
        
# ----- Variables -----
clock = pygame.time.Clock()

# ----- Function ------
def exit():
    """Exits the server and game."""
    pygame.quit()
    sys.exit()

def load_image(path, size = None):
        """Returns the loaded image.

        Args:
            paths (str): path to a single image.
            
        Returns:
            pygame.Surface: A pygame surface of the image.
        """
        width_multiplier, height_multiplier = render.get_size_multiplier()
        image = pygame.image.load(path)
        
        if size:
            return pygame.transform.smoothscale(image, (size[0] * width_multiplier, size[1] * height_multiplier))
        return pygame.transform.smoothscale(image, (image.get_width() * width_multiplier, image.get_height() * height_multiplier))
    
def load_images(paths, size = None):
        """Returns the loaded images.

        Args:
            paths (list): List of paths to sprite frames.
            
        Returns:
            list: A list of loaded images.
        """        
        return [load_image(path, size) for path in paths]

# ----- Class -----
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
        """
        Scales a Pygame surface to a size relative to the screen.

        Args:
            surface (pygame.Surface): The surface to be scaled.

        Returns:
            pygame.Surface: The scaled surface.
        """
        width_multiplier, height_multiplier = render.get_size_multiplier()
        
        surface_resize = pygame.transform.smoothscale(surface, (surface.get_width() * width_multiplier, surface.get_height() * height_multiplier))
        
        return surface_resize
    
    def update(self):
        """
        Handles events and updates the display.
        """
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                exit()
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                exit()
    
    def show_stats(self):
        """
        Blits game statistics like FPS to the screen. Useful for debugging.
        """
        fps = clock.get_fps()
        fps_text = Font.debug.render(f"FPS: {fps:.1f}", True, (255, 255, 255))
        fps_text = render.scale_image(fps_text)
        fps_rect = fps_text.get_rect()
        fps_rect.topright = render.get_render_pos((GAME_WIDTH - 10, 10))
        
        self.blit(fps_text, fps_rect)
    
    def display(self):
        """
        Blits all queued images and updates the display.
        """
        self.screen.fill(self.BACKGROUND_COLOR)
        
        if settings["ShowStats"]:
            self.show_stats()
        
        for i, image in enumerate(self.queued_images):
            self.screen.blit(*image)
            
        pygame.display.update()
        self.queued_images = []
    
    def get_mouse(self):
        """
        Gets the mouse position and mouse button states.

        Returns:
            tuple: A tuple containing the mouse position and the mouse button states.
        """
        return pygame.mouse.get_pos(), pygame.mouse.get_pressed()
    
    def get_keys(self):
        """
        Gets the keyboard button states.

        Returns:
            pygame.key.ScancodeWrapper: Contains the keyboard button states.
        """
        return pygame.key.get_pressed()

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

class Sprite:    
    class Player:
        frames = load_images(["images/player/f0.png"], (100, 100))
    
    class Guns:
        class Shotgun:
            frames = []
    
    class UI:
        class Menu:
            class Background:
                image = load_image("images/UI/menu/Background.png", (GAME_WIDTH, GAME_HEIGHT))
    
    class Scenery:
        class Foilage:
            class Tree:
                frames = load_images(["images/scenery/foilage/tree/f0.png"], (300, 500))
                

class Scene:
    buttons = []
    objects = []
    @classmethod
    def add_button(cls, button):
        """
        A class method which adds a button to the list of buttons in the Scene class.

        Args:
            button (Button): A Button instance to be added.
        """
        cls.buttons.append(button)
    
    @classmethod
    def add_object(cls, object):
        """
        A class method which adds an object to the list of objects in the Scene class.
        
        Args:
            object (Object): A Object instance to be added.
        """
        cls.objects.append(object)
        
    @classmethod
    def update_buttons(cls, mouse_pos, mouse_down):        
        """Updates the Buttons.

        Args:
            mouse_pos (tuple): Current mouse position.
            mouse_down (tuple): Indicates if the mouse button is being pressed.
        """
        for button in cls.buttons:
            button.update(mouse_pos, mouse_down)


class Player:
    game_pos = [0, 0]
    render_pos = render.get_render_pos([GAME_WIDTH/2 - Sprite.Player.frames[0].get_width()/2, GAME_HEIGHT/2 - Sprite.Player.frames[0].get_height()/2])
    base_speed = 2.5

    @classmethod
    def update(cls, mouse_pos, mouse_down, keys_pressed: pygame.key.ScancodeWrapper):
        """
        Updates the player and handles movement.

        Args:
            mouse_pos (tuple): Current mouse position.
            mouse_down (tuple): Current mouse button states.
            keys_pressed (pygame.key.ScancodeWrapper): Current keyboard button states.
        """
        # Calculate the player's movement vector
        move_vector = [0, 0]
        if keys_pressed[pygame.K_w]:
            move_vector[1] -= cls.base_speed
        if keys_pressed[pygame.K_a]:
            move_vector[0] -= cls.base_speed
        if keys_pressed[pygame.K_s]:
            move_vector[1] += cls.base_speed
        if keys_pressed[pygame.K_d]:
            move_vector[0] += cls.base_speed

        # Normalize the movement vector if it is diagonal
        if move_vector[0] != 0 and move_vector[1] != 0:
            move_vector = [x / math.sqrt(2) for x in move_vector]

        # Update the player's position
        cls.game_pos = (cls.game_pos[0] + move_vector[0], cls.game_pos[1] + move_vector[1])

        cls.display()

    @classmethod
    def display(cls):
        """Displays the player on the screen."""
        render.blit(Sprite.Player.frames[0], cls.render_pos)


class Object:
    def __init__(self, image, game_pos, size = None):
        """
        Initializes an Object with its game position and image.

        Args:
            game_pos (tuple): The game position of the object.
            image (pygame.Surface): The image of the object.
        """
        if size:
            width_multiplier, height_multiplier = render.get_size_multiplier()
            self.image = pygame.transform.smoothscale(image, (size[0] * width_multiplier, size[1] * height_multiplier))
        else:
            self.image = image
        self.game_pos = game_pos

    def update(self):
        """
        Updates and displays the object.
        """
        self.display()

    def display(self):
        """Displays the object on the screen."""
        render.blit(self.image, (self.game_pos[0] - Player.game_pos[0], self.game_pos[1] - Player.game_pos[1]))


class World(Scene):
    buttons = []

    @classmethod
    def update(cls, mouse_pos, mouse_down, keys_pressed):
        """
        A class method that updates all events in the World and then displays them.

        Args:
            mouse_pos (tuple): Current position of the mouse.
            mouse_down (tuple): Current state of the mouse buttons.
        """
        cls.update_buttons(mouse_pos, mouse_down)
        
        cls.display_objects()
        Player.update(mouse_pos, mouse_down, keys_pressed)
        cls.display_overlay()

    @classmethod
    def display_objects(cls): 
        """
        A class method that displays all objects in the World.
        """
        for object in cls.objects:
            object.display()
            
    @classmethod
    def display_overlay(cls): 
        """
        A class method that displays all buttons and UI elements in the World.
        """        
        for button in cls.buttons:
            button.display()
            

class Button:
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
        self.button_surface = render.scale_image(self.button_surface)

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

    def display(self):
        """Displays the button on the screen."""
        render.blit(self.button_surface, self.render_pos)


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
        cls.update_buttons(mouse_pos, mouse_down)
        
        cls.display()
        
    @classmethod
    def display(cls):
        """Displays the MainMenu."""
        render.blit(Sprite.UI.Menu.Background.image, (0, 0))
        
        for button in cls.buttons:
            button.display()
                

# World Scene Overlay
MainMenu.add_button(Button("Play", (GAME_WIDTH / 2 - 400, 450), (800, 180), (255, 0, 0), Font.menu, MainMenu.toggle)) # Play Button
MainMenu.add_button(Button("Exit", (GAME_WIDTH / 2 - 400, 650), (800, 180), (255, 0, 0), Font.menu, exit)) # Exit Button

# Menu Scene Overlay
World.add_button(Button("ll", (10, 10), (100, 100), (255, 0, 0), Font.symbol, MainMenu.toggle)) # Pause Button

# World Scene Objects
World.add_object(Object(Sprite.Scenery.Foilage.Tree.frames[0], (500, 50)))
World.add_object(Object(Sprite.Scenery.Foilage.Tree.frames[0], (200, 150), (40, 70)))

running = True
while running:
    mouse_pos, mouse_down = render.get_mouse()
    keys_pressed = render.get_keys()

    if MainMenu.enabled:
        MainMenu.update(mouse_pos, mouse_down)
    else:
        World.update(mouse_pos, mouse_down, keys_pressed)
    
    render.update()
    render.tick()
    render.display()