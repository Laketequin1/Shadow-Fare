# ----- Settings -----
settings = {
            "ShowDebug":True,            # [Bool]   (Default: False)  Shows debug and stat information like FPS.
            "NoFullscreen": True,         # [Bool]   (Default: False)  Disables fullscreen mode on Linux.
            "DisplayHeightMultiplier": 1, # [Float]  (Default: 1)      Scales the screen height, making it taller or shorter. It is suggested to enable NoFullscreen if using Linux.
            "DisplayWidthMultiplier": 1,  # [Float]  (Default: 1)      Scales the screen width, making it wider or thinner. It is suggested to enable NoFullscreen if using Linux.
            "TPS": 64,                    # [Int]    (Default: 64)     Modify the game ticks per second, making everythng update faster or slower. Intended for 64 tps.
            "FPS": 400,                   # [Int]    (Default: 120)    Limit rendering frames per second.
            "SpeedMultiplier": 1,         # [Float]  (Default: 1)      Scales the player speed, making it faster or slower.
            "AndroidBuild": False          # [Bool]   (Default: False)  Changes some sections to work for android.
            }

if settings["AndroidBuild"]:
    settings["NoFullscreen"] = False


# ----- Setup ------
import pygame, os, sys, random, math, time, threading
import numpy as np

pygame.init()

# Imports lots of colors as RGB
from src import color as Color

if settings["ShowDebug"]:
    from src.tools import DClock

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
    debug = pygame.font.Font(os.path.abspath("fonts/RobotoMono.ttf"), 50)
    arrows = pygame.font.Font(os.path.abspath("fonts/seguisym.ttf"), 100)
        
        
# ----- Variables -----


# ----- Functions ------
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
    path = os.path.abspath(path)

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

def calculate_hand_position(BODY_RADIUS, HAND_RADIUS, angle_offset, render_center_pos, game_center_pos, mouse_pos):
    # Calculate the distance between the mouse position and the render center position
    distance_x = mouse_pos[0] - render_center_pos[0]
    distance_y = mouse_pos[1] - render_center_pos[1]

    # Calculate the distance to the mouse position using the oval equation
    distance_to_mouse = math.sqrt(distance_x * distance_x / (BODY_RADIUS[0] * BODY_RADIUS[0]) + distance_y * distance_y / (BODY_RADIUS[1] * BODY_RADIUS[1]))

    # Normalize the distance to get the direction vector
    normalized_distance_x = distance_x / (BODY_RADIUS[0] * distance_to_mouse)
    normalized_distance_y = distance_y / (BODY_RADIUS[1] * distance_to_mouse)

    # Calculate the angle based on the normalized direction vector and the angle offset
    angle = math.atan2(normalized_distance_y, normalized_distance_x) + angle_offset

    # Calculate the cosine and sine of the angle
    cos_angle = math.cos(angle)
    sin_angle = math.sin(angle)

    # Calculate the position of the hand based on the game center position, body radius, hand radius, and angle
    hand_pos_x = game_center_pos[0] + BODY_RADIUS[0] * cos_angle - HAND_RADIUS[0]
    hand_pos_y = game_center_pos[1] + BODY_RADIUS[1] * sin_angle - HAND_RADIUS[1]

    # Return the calculated hand position
    return (hand_pos_x, hand_pos_y)

# ----- Class -----
class Render:
    info = pygame.display.Info()
    DISPLAY_WIDTH = info.current_w * settings["DisplayWidthMultiplier"]
    DISPLAY_HEIGHT = info.current_h * settings["DisplayHeightMultiplier"]
    
    BACKGROUND_COLOR = Color.BLACK

    # Debugging
    DEBUG_DOT = pygame.Surface((6, 6))
    DEBUG_DOT.fill(Color.RED1)
    previous_show_debug_time = -1
    
    queued_images = []
    finger_positions = {}

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
            self.screen = pygame.display.set_mode((self.DISPLAY_WIDTH, self.DISPLAY_HEIGHT), pygame.FULLSCREEN | pygame.HWSURFACE | pygame.DOUBLEBUF)
            if settings["AndroidBuild"]:
                self.info = pygame.display.Info()
                self.DISPLAY_WIDTH = self.info.current_w * settings["DisplayWidthMultiplier"]
                self.DISPLAY_HEIGHT = self.info.current_h * settings["DisplayHeightMultiplier"]
                self.screen = pygame.display.set_mode((self.DISPLAY_WIDTH, self.DISPLAY_HEIGHT), pygame.FULLSCREEN | pygame.HWSURFACE | pygame.DOUBLEBUF)
        else:
            self.screen = pygame.display.set_mode((self.DISPLAY_WIDTH, self.DISPLAY_HEIGHT), pygame.NOFRAME | pygame.HWSURFACE | pygame.DOUBLEBUF)
        
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
        for event in pygame.event.get(exclude=[pygame.FINGERDOWN, pygame.FINGERMOTION, pygame.FINGERUP]):
            if event.type == pygame.QUIT:
                exit()
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                exit()
    
    def show_debug(self, compute = True):
        """
        Blits game statistics like FPS to the screen. Useful for debugging.
        """
        if compute:
            self.fps_text = Font.debug.render(f"FPS: {self.average_running_fps:.1f}", True, Color.BLACK, Color.WHITE).convert()
            self.fps_text = render.scale_image(self.fps_text)
            self.fps_rect = self.fps_text.get_rect()
            self.fps_rect.topright = render.get_render_pos((GAME_WIDTH - 10, 10))

            self.tps_text = Font.debug.render(f"TPS: {self.average_running_tps:.1f}", True, Color.BLACK, Color.WHITE).convert()
            self.tps_text = render.scale_image(self.tps_text)
            self.tps_rect = self.tps_text.get_rect()
            self.tps_rect.topright = render.get_render_pos((GAME_WIDTH - 10, 20 + self.fps_rect.height / render.HEIGHT_MULTIPLIER))

            self.machine_text = Font.debug.render(f"Machine: {os.uname().machine}", True, Color.BLACK, Color.WHITE).convert()
            self.machine_text = render.scale_image(self.machine_text)
            self.machine_rect = self.machine_text.get_rect()
            self.machine_rect.topright = render.get_render_pos((GAME_WIDTH - 10, 30 + self.machine_rect.height * 2 / render.HEIGHT_MULTIPLIER))

        self.blit(self.fps_text, self.fps_rect.topleft)
        self.blit(self.tps_text, self.tps_rect.topleft)
        self.blit(self.machine_text, self.machine_rect.topleft)
        self.blit(self.DEBUG_DOT, (self.DISPLAY_WIDTH / 2 - self.DEBUG_DOT.get_width() / 2, self.DISPLAY_HEIGHT / 2 - self.DEBUG_DOT.get_height() / 2))
    
    def display(self):
        """
        Blits all queued images and updates the display.
        """
        self.screen.fill(self.BACKGROUND_COLOR)
        DClock.start("Debug")
        current_time = time.time()
        if settings["ShowDebug"]:
            if self.previous_show_debug_time + 0.5 < current_time:
                self.previous_show_debug_time = time.time()
                self.show_debug()
            else:
                self.show_debug(False)

        DClock.finish("Debug", True)
        DClock.start("BlitLoop")
        for i, image in enumerate(self.queued_images):
            image = list(image)
            image[1] = (round(image[1][0]), round(image[1][1]))
            self.screen.blit(*image)
        DClock.finish("BlitLoop", True)
        DClock.start("Display")
        pygame.display.update()
        DClock.finish("Display", True)
        self.queued_images = []
    
    def get_mouse(self):
        """
        Gets the mouse position and mouse button states.

        Returns:
            tuple: A tuple containing the mouse position and the mouse button states.
        """
        return pygame.mouse.get_pos(), pygame.mouse.get_pressed()
    
    def get_fingers(self):
        """
        Gets the finger positions.

        Returns:
            tuple: A tuple containing the finger positions.
        """
        for event in pygame.event.get(eventtype=[pygame.FINGERDOWN, pygame.FINGERMOTION, pygame.FINGERUP]):
            if event.type == pygame.FINGERDOWN or event.type == pygame.FINGERMOTION:
                finger_x, finger_y = event.x * self.DISPLAY_WIDTH, event.y * self.DISPLAY_HEIGHT
                
                self.finger_positions[event.finger_id] = (finger_x, finger_y)
            elif event.type == pygame.FINGERUP:
                del self.finger_positions[event.finger_id]
        return self.finger_positions.values()

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
                image = load_image("images/UI/menu/Background.png", size, transparent)
    
    class Scenery:
        class Foilage:
            class Tree:
                size = (300, 300)
                transparent = True
                frames = load_images(["images/scenery/foilage/tree/f0.png"], size, transparent)


class Scene:
    mobile_buttons = {}
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
    def add_mobile_button(cls, name, mobile_button):
        """
        A class method which adds a mobile button to the dict of mobile buttons in the Scene class.

        Args:
            name (String): The name of the button in the list.
            mobile_button (MobileButton): A MobileButton instance to be added.
        """
        cls.mobile_buttons[name] = mobile_button
    
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
        """
        Updates the Buttons.

        Args:
            mouse_pos (tuple): Current mouse position.
            mouse_down (tuple): Indicates if the mouse button is being pressed.
        """
        for button in cls.buttons:
            button.update(mouse_pos, mouse_down)

    @classmethod
    def update_mobile_buttons(cls, finger_positions):
        """
        Updates the mobile Buttons, and returns a dict of pressed buttons.

        Args:
            finger_positions (tuple): A list of finger positions..
        """
        pressed_buttons = {}

        for button_name, mobile_button in cls.mobile_buttons.items():
            pressed_buttons[button_name] = mobile_button.update(finger_positions)

        return pressed_buttons


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
    def update(cls, mouse_pos, mouse_down, keys_pressed: pygame.key.ScancodeWrapper, movement_arrows):
        """
        Updates the player and handles movement.

        Args:
            mouse_pos (tuple): Current mouse position relative to the screen.
            mouse_down (tuple): Current mouse button states.
            keys_pressed (pygame.key.ScancodeWrapper): Current keyboard button states.
        """
        # Calculate the player's movement vector
        move_vector = [0, 0]
        if keys_pressed[pygame.K_w] or movement_arrows["up"]:
            move_vector[1] -= cls.base_speed
        if keys_pressed[pygame.K_a] or movement_arrows["left"]:
            move_vector[0] -= cls.base_speed
        if keys_pressed[pygame.K_s] or movement_arrows["down"]:
            move_vector[1] += cls.base_speed
        if keys_pressed[pygame.K_d] or movement_arrows["right"]:
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
    @classmethod
    def update(cls, mouse_pos, mouse_down, keys_pressed, finger_positions):
        """
        A class method that updates all events in the World and then displays them.

        Args:
            mouse_pos (tuple): Current position of the mouse relative to the screen.
            mouse_down (tuple): Current state of the mouse buttons.
        """
        cls.update_buttons(mouse_pos, mouse_down)
        if settings["AndroidBuild"]:
            movement_arrows = cls.update_mobile_buttons(finger_positions)
        else:
            movement_arrows = {"left": False, "right": False, "up": False, "down": False}
        Player.update(mouse_pos, mouse_down, keys_pressed, movement_arrows)

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

        for mobile_button in cls.mobile_buttons.values():
            mobile_button.display()
            

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

        self.button_surface = pygame.Surface(self.size, pygame.SRCALPHA)
        self.button_surface.fill((0, 0, 0, 0))
        
        if not settings["AndroidBuild"]:
            border_radius = 30
        else:
            border_radius = 0
        
        # Draw rounded rectangle
        pygame.draw.rect(self.button_surface, self.color, (0, 0, self.size[0], self.size[1]), border_radius=border_radius)
        
        text = font.render(self.text, True, Color.WHITE)
        text_rect = text.get_rect(center=(self.size[0]/2, self.size[1]/2))
        self.button_surface.blit(text, text_rect)

        self.button_surface = render.scale_image(self.button_surface)
        if settings["AndroidBuild"]:
            self.button_surface = self.button_surface.convert()

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


class MobileButton(Button):
    def __init__(self, text, pos, size, color, font):
        super().__init__(text, pos, size, color, font, None)

    def update(self, finger_positions):
        # Check if any finger is on the button
        for finger_pos in finger_positions:
            if pygame.Rect(*self.render_pos, *self.button_surface.get_size()).collidepoint(finger_pos):
                return True
        return False


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
MainMenu.add_button(Button("Play", (GAME_WIDTH / 2 - 400, 400), (800, 180), Color.RED1, Font.menu, MainMenu.toggle)) # Play Button
MainMenu.add_button(Button("Exit", (GAME_WIDTH / 2 - 400, 650), (800, 180), Color.RED1, Font.menu, exit)) # Exit Button

# Menu Scene Overlay
World.add_button(Button("ll", (10, 10), (100, 100), Color.RED1, Font.symbol, MainMenu.toggle)) # Pause Button

# World Scene Objects
World.add_object(Object(Sprite.Scenery.Foilage.Tree.frames[0], (0, 0)))
World.add_object(Object(Sprite.Scenery.Foilage.Tree.frames[0], (350, 180), (60, 60)))

# Mobile Buttons
if settings["AndroidBuild"]:
    #pass
    World.add_mobile_button("up", MobileButton("⇑", (100, GAME_HEIGHT - 500), (450, 150), Color.RED1, Font.arrows))
    World.add_mobile_button("down", MobileButton("⇓", (100, GAME_HEIGHT - 200), (450, 150), Color.RED1, Font.arrows))
    World.add_mobile_button("left", MobileButton("⇐", (100, GAME_HEIGHT - 500), (150, 450), Color.RED1, Font.arrows))
    World.add_mobile_button("right", MobileButton("⇒", (400, GAME_HEIGHT - 500), (150, 450), Color.RED1, Font.arrows))

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

        if settings["AndroidBuild"]:
            finger_positions = render.get_fingers()
        else:
            finger_positions = None

        if MainMenu.enabled:
            MainMenu.update(mouse_pos, mouse_down)
        else:
            World.update(mouse_pos, mouse_down, keys_pressed, finger_positions)
        
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
        else:
            World.display()

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
    game_logic = threading.Thread(target=game_logic)
    game_logic.start()

    render_loop()

    game_logic.join()

    pygame.quit()