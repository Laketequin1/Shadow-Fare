# ----- Settings -----
settings = {
            "ShowDebug":True,             # [Bool]   (Default: False)  Shows debug and stat information like FPS.
            "NoFullscreen": True,         # [Bool]   (Default: False)  Disables fullscreen mode on Linux.
            "DisplayHeightMultiplier": 1, # [Float]  (Default: 1)      Scales the screen height, making it taller or shorter. It is suggested to enable NoFullscreen if using Linux.
            "DisplayWidthMultiplier": 1,  # [Float]  (Default: 1)      Scales the screen width, making it wider or thinner. It is suggested to enable NoFullscreen if using Linux.
            "TPS": 64,                    # [Int]    (Default: 64)     Modify the game ticks per second, making everythng update faster or slower. Intended for 64 tps.
            "FPS": 120,                   # [Int]    (Default: 120)    Limit rendering frames per second.
            "SpeedMultiplier": 1          # [Float]  (Default: 1)      Scales the player speed, making it faster or slower.
            }

# ----- Setup ------
import pygame, os, sys, random, math, time, threading
import numpy as np
from src.hand import calculate_hand_position

pygame.init()

# Imports lots of colors as RGB
from src import color as Color

# Clear screen
if os.name == "posix":
    os.system("clear")
else:
    os.system("cls")

# ----- Constant Variables -----
# Ticks per second
TPS = settings["TPS"]
# Seconds per tick
SPT = 1/TPS

#Frames per second
FPS = settings["FPS"]
# Seconds per tick
SPF = 1/FPS

GAME_WIDTH = 1920
GAME_HEIGHT = 1080

class Font:
    menu = pygame.font.SysFont(None, 100)
    symbol = pygame.font.SysFont(None, 80)
    debug = pygame.font.Font("fonts/RobotoMono.ttf", 50)
        
        
# ----- Variables -----

# ----- Function ------
def exit():
    """Exits the server and game."""
    global running
    running = False
    sys.exit()

def load_image(path, size = None, transparent = False):
    """Returns the loaded image.

    Args:
        paths (str): path to a single image.
        size (array): Size to set the image.
        transparent (bool): Makes image alpha if set to True.
        
    Returns:
        pygame.Surface: A pygame surface of the image.
    """
    if transparent:
        image = pygame.image.load(path)
    else:
        image = pygame.image.load(path).convert()
    
    if size:
        return pygame.transform.smoothscale(image, (size[0] * render.WIDTH_MULTIPLIER, size[1] * render.HEIGHT_MULTIPLIER))
    return pygame.transform.smoothscale(image, (image.get_width() * render.WIDTH_MULTIPLIER, image.get_height() * render.HEIGHT_MULTIPLIER))
    
def load_images(paths, size = None, transparent = False):
    """Returns the loaded images.

    Args:
        paths (list): List of paths to sprite frames.
        size (array): Size to set the image frames.
        transparent (bool): Makes image frames alpha if set to True.
        
    Returns:
        list: A list of loaded images.
    """        
    return [load_image(path, size, transparent) for path in paths]
        
# ----- Class -----
class Render:
    info = pygame.display.Info()
    DISPLAY_WIDTH = info.current_w * settings["DisplayWidthMultiplier"]
    DISPLAY_HEIGHT = info.current_h * settings["DisplayHeightMultiplier"]
    
    BACKGROUND_COLOR = Color.BLACK

    # Debugging
    DEBUG_DOT = pygame.Surface((6, 6))
    DEBUG_DOT.fill((255, 0, 0))
    
    queued_images = []

    running_spt = np.array([SPT])
    average_running_tps = TPS

    running_spf = np.array([SPF])
    average_running_fps = FPS
    
    def __init__(self, game_resolution):
        """
        Initializes a Render object with the game resolution and the display resolution.

        Args:
            game_resolution (tuple [int, int]): Game resolution.
        """
        if os.name == "posix" and not settings["NoFullscreen"]:
            self.screen = pygame.display.set_mode((self.DISPLAY_WIDTH, self.DISPLAY_HEIGHT), pygame.FULLSCREEN)
        else:
            self.screen = pygame.display.set_mode((self.DISPLAY_WIDTH, self.DISPLAY_HEIGHT), pygame.NOFRAME)
        pygame.display.set_caption("Shadow Fare")
        self.game_resolution = game_resolution
        
        self.WIDTH_MULTIPLIER = self.DISPLAY_WIDTH/GAME_WIDTH
        self.HEIGHT_MULTIPLIER = self.DISPLAY_HEIGHT/GAME_HEIGHT

        self.DEBUG_DOT = self.DEBUG_DOT.convert()
    
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
        surface_resize = pygame.transform.smoothscale(surface, (surface.get_width() * render.WIDTH_MULTIPLIER, surface.get_height() * render.HEIGHT_MULTIPLIER))
        return surface_resize
    
    def handle_events(self):
        """
        Handles events and updates the display.
        """
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                exit()
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                exit()
    
    def show_debug(self):
        """
        Blits game statistics like FPS to the screen. Useful for debugging.
        """
        fps_text = Font.debug.render(f"FPS: {self.average_running_fps:.1f}", True, (255, 255, 255))
        fps_text = render.scale_image(fps_text)
        fps_rect = fps_text.get_rect()
        fps_rect.topright = render.get_render_pos((GAME_WIDTH - 10, 10))

        tps_text = Font.debug.render(f"TPS: {self.average_running_tps:.1f}", True, (255, 255, 255))
        tps_text = render.scale_image(tps_text)
        tps_rect = tps_text.get_rect()
        tps_rect.topright = render.get_render_pos((GAME_WIDTH - 10, 20 + fps_rect.height))

        self.blit(fps_text, fps_rect.topleft)
        self.blit(tps_text, tps_rect.topleft)
        self.blit(self.DEBUG_DOT, (self.DISPLAY_WIDTH / 2 - self.DEBUG_DOT.get_width() / 2, self.DISPLAY_HEIGHT / 2 - self.DEBUG_DOT.get_height() / 2))
    
    def display(self):
        """
        Blits all queued images and updates the display.
        """
        self.screen.fill(self.BACKGROUND_COLOR)
        
        if settings["ShowDebug"]:
            self.show_debug()
        
        for i, image in enumerate(self.queued_images):
             self.screen.blit(*image)
            
        pygame.display.update() # Needs optimized
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

    def update_game_loop_duration(self, duration):
        """
        Updates the game loop duration list and calculates the average TPS (ticks per second).

        Args:
            duration (float): The duration of the game loop iteration in seconds.
        """
        self.running_spt = np.append(self.running_spt, duration)
        if len(self.running_spt) > 100:
            self.running_spt = self.running_spt[1:]
        self.average_running_tps = 1 / np.mean(self.running_spt)

    def update_render_loop_duration(self, duration):
        """
        Updates the render loop duration list and calculates the average FPS (frames per second).

        Args:
            duration (float): The duration of the render loop iteration in seconds.
        """
        self.running_spf = np.append(self.running_spf, duration)
        if len(self.running_spf) > min(SPF * 3, 1000):
            self.running_spf = self.running_spf[1:]
        self.average_running_fps = 1 / np.mean(self.running_spf)


render = Render((GAME_WIDTH, GAME_WIDTH))

class Sprite:    
    class Player:
        class Body:
            size = (80, 80)
            frame_interval = 150 # ms
            transperent = True
            frames = load_images([f"images/player/body/f{x}.png" for x in range(4)], size, transperent)
        class Hand:
            size = (30, 30)
            transparent = True
            image = load_image("images/player/hands/f0.png", size, transparent)
    
    class Guns:
        class Shotgun:
            frames = []
    
    class UI:
        class Menu:
            class Background:
                size = (GAME_WIDTH, GAME_HEIGHT)
                transparent = False
                image = load_image("images/UI/menu/Background.png", size)
    
    class Scenery:
        class Foilage:
            class Tree:
                size = (300, 500)
                transparent = False
                frames = load_images(["images/scenery/foilage/tree/f0.png"], size)


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


class Hand:
    GAME_CENTER_POS = np.array([GAME_WIDTH / 2, GAME_HEIGHT / 2], dtype=np.double)
    RENDER_CENTER_POS = np.array([render.DISPLAY_WIDTH / 2, render.DISPLAY_HEIGHT / 2], dtype=np.double)
    BODY_RADIUS = np.array((Sprite.Player.Body.size[0] / 2, Sprite.Player.Body.size[1] / 2), dtype=np.double)
    HAND_RADIUS = np.array((Sprite.Player.Hand.size[0] / 2, Sprite.Player.Hand.size[1] / 2), dtype=np.double)

    def __init__(self, angle_offset):
        """
        Initializes a Hand object with the angle offset for the left/right hand.

        Args:
            angle_offset (int): The angle offset around the player radius from pointing at the mouse. Measured in radians.
        """
        self.angle_offset = angle_offset
        self.pos = (0, 0)

    def update(self, mouse_pos):
        """
        Calculates the hand position using a cython module, then sets its position.
        
        Args:
            mouse_pos (tuple): Current mouse position relative to the screen.
        """
        mouse_pos = np.array(mouse_pos, dtype=np.double)
        pos = calculate_hand_position(self.BODY_RADIUS, self.HAND_RADIUS, self.angle_offset, self.RENDER_CENTER_POS, self.GAME_CENTER_POS, mouse_pos)
        
        if pos:
            self.pos = pos

    def display(self):
        """Displays the hand on the screen."""
        render.blit(Sprite.Player.Hand.image, render.get_render_pos(self.pos))


class Player:
    game_pos = [0, 0]
    render_pos = render.get_render_pos([GAME_WIDTH/2 - Sprite.Player.Body.frames[0].get_width() / 2 / render.WIDTH_MULTIPLIER, GAME_HEIGHT/2 - Sprite.Player.Body.frames[0].get_height() / 2 / render.HEIGHT_MULTIPLIER])
    base_speed = 6 * settings["SpeedMultiplier"]
    hands = {"left":Hand(-0.5), "right":Hand(0.5)}
    current_frame = 0
    last_frame_time = pygame.time.get_ticks()

    @classmethod
    def update(cls, mouse_pos, mouse_down, keys_pressed: pygame.key.ScancodeWrapper):
        """
        Updates the player and handles movement.

        Args:
            mouse_pos (tuple): Current mouse position relative to the screen.
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

        # Update the hands's render positions
        cls.hands["left"].update(mouse_pos)
        cls.hands["right"].update(mouse_pos)

    @classmethod
    def display(cls):
        """Displays the player and hands on the screen."""
        cls.hands["left"].display()
        cls.hands["right"].display()

        current_time = pygame.time.get_ticks()
        if current_time - cls.last_frame_time >= Sprite.Player.Body.frame_interval:
            cls.last_frame_time = current_time
            cls.current_frame = (cls.current_frame + 1) % len(Sprite.Player.Body.frames)
        render.blit(Sprite.Player.Body.frames[cls.current_frame], cls.render_pos)


class Object:
    def __init__(self, image, game_pos, size = None):
        """
        Initializes an Object with its game position and image.

        Args:
            game_pos (tuple): The game position of the object.
            image (pygame.Surface): The image of the object.
        """
        if size:
            self.image = pygame.transform.smoothscale(image, (size[0] * render.WIDTH_MULTIPLIER, size[1] * render.HEIGHT_MULTIPLIER))
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
        render.blit(self.image, render.get_render_pos((self.game_pos[0] - Player.game_pos[0] + GAME_WIDTH / 2, self.game_pos[1] - Player.game_pos[1] + GAME_HEIGHT / 2)))


class World(Scene):
    buttons = []

    @classmethod
    def update(cls, mouse_pos, mouse_down, keys_pressed):
        """
        A class method that updates all events in the World and then displays them.

        Args:
            mouse_pos (tuple): Current position of the mouse relative to the screen.
            mouse_down (tuple): Current state of the mouse buttons.
        """
        cls.update_buttons(mouse_pos, mouse_down)
        Player.update(mouse_pos, mouse_down, keys_pressed)

    @classmethod
    def display(cls):
        """
        A class method that displays everything in tbe World.
        """
        cls.display_objects()
        Player.display()
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
        self.text = text
        self.render_pos = render.get_render_pos(pos)
        self.game_pos = pos
        self.size = size
        self.color = color
        self.callback = callback
        
        self.button_surface = pygame.Surface(self.size)
        self.button_surface.fill(self.color)
        
        text = font.render(self.text, True, (255, 255, 255))
        text_rect = text.get_rect(center=(self.size[0]/2, self.size[1]/2))
        self.button_surface.blit(text, text_rect)
        
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
World.add_object(Object(Sprite.Scenery.Foilage.Tree.frames[0], (0, 0)))
World.add_object(Object(Sprite.Scenery.Foilage.Tree.frames[0], (350, 180), (60, 60)))

running = True

def game_logic():
    """
    Main game loop. Handles user inputs and gameplay computing. Run at a set TPS.
    """
    global running, render, MainMenu, World
    while running:
        loop_start_time = time.perf_counter()

        mouse_pos, mouse_down = render.get_mouse()
        keys_pressed = render.get_keys()

        if MainMenu.enabled:
            MainMenu.update(mouse_pos, mouse_down)
        else:
            World.update(mouse_pos, mouse_down, keys_pressed)
        
        render.handle_events()
        
        # Get the average extra time the delay takes over its set TPS
        delay_overflow_time = np.average(render.running_spt) - SPT
        # Get time where loop finishes. Delay overflow time used to more accurately hit by accouting for the extra time
        target_time = loop_start_time + SPT - delay_overflow_time * SPT * 1000
        current_time = time.perf_counter()
        while current_time < target_time:
            # Sleep for most of the duration until target time, creating a partially busy delay loop
            time.sleep((target_time - current_time) * 0.9)
            current_time = time.perf_counter()
        render.update_game_loop_duration(current_time - loop_start_time)

def render_loop():
    """
    Render loop. Displays all objects on the screen at a set FPS.
    """
    global running, render, MainMenu, World
    while running:
        loop_start_time = time.perf_counter()

        if MainMenu.enabled:
            MainMenu.display()
            pass
        else:
            World.display()
            pass

        render.display()

        # Get time where loop finishes. Delay overflow time not used as accuracy is less important
        target_time = loop_start_time + SPF
        current_time = time.perf_counter()
        while current_time < target_time:
            # Sleep for most of the duration until target time, creating a partially busy delay loop
            time.sleep((target_time - current_time) * 0.98)
            current_time = time.perf_counter()
        
        render.update_render_loop_duration(current_time - loop_start_time)

if __name__ == "__main__":
    render_thread = threading.Thread(target=render_loop)
    render_thread.start()

    game_logic()

    render_thread.join()

    pygame.quit()