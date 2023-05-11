# ----- Setup ------
import pygame, os, sys, time
pygame.init()

# Clear screen
if os.name == "posix":
    os.system("clear")
else:
    os.system("cls")

# ----- Constant Variables -----
FPS = 120

GAME_WIDTH = 1920
GAME_HEIGHT = 1080

# ----- Variables -----
clock = pygame.time.Clock()

# ----- Function ------
def exit():
    """Exits the server and game."""
    pygame.quit()
    sys.exit()

# ----- Class -----
class Square:
    def __init__(self, x, y, size, color):
        self.x = x
        self.y = y
        self.size = size
        self.color = color
        self.speed = 500  # pixels per second
        self.prev_x = x
        self.prev_y = y

    def draw(self):
        pygame.draw.rect(screen, self.color, (self.x, self.y, self.size, self.size))

    def move(self, dt, dx, dy):
        distance = self.speed * dt / (FPS*10)  # distance = speed * time
        self.x += dx * distance
        self.y += dy * distance

class Wall:
    def __init__(self, x, y, size, color):
        self.x = x
        self.y = y
        self.size = size
        self.color = color

    def draw(self):
        pygame.draw.rect(screen, self.color, (self.x, self.y, self.size[0], self.size[1]))

    def check_collision(self, square):
        # Calculate the square's new position after moving
        new_x = square.x
        new_y = square.y
        distance = square.speed * dt / (FPS*10)
        if keys[pygame.K_w]:
            new_y -= distance
        if keys[pygame.K_s]:
            new_y += distance
        if keys[pygame.K_a]:
            new_x -= distance
        if keys[pygame.K_d]:
            new_x += distance

        # Check if the square will intersect with the wall's bounding box
        if new_x + square.size > self.x and new_x < self.x + self.size[0]:
            if new_y + square.size > self.y and new_y < self.y + self.size[1]:
                # Move the square back to its previous position
                square.x = square.prev_x
                square.y = square.prev_y
                return True

        # If there is no collision, update the square's previous position
        square.prev_x = square.x
        square.prev_y = square.y
        return False
        

# Create a Square object at the center of the screen
square = Square(GAME_WIDTH // 2 - 50, GAME_HEIGHT // 2 - 50, 100, (255, 0, 0))
wall = Wall(GAME_WIDTH // 2 - 150, GAME_HEIGHT // 2 - 50, [20, 400], (0, 0, 255))

screen = pygame.display.set_mode((GAME_WIDTH, GAME_HEIGHT))

running = True
while running:
    # ----- Main Event Loop -----
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            exit()
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            exit()

    # Calculate time elapsed since the last frame
    time.sleep(1)
    dt = clock.tick(FPS)

    # Get the state of all keyboard keys
    keys = pygame.key.get_pressed()

    # Move the square based on WASD key presses
    if keys[pygame.K_w]:
        square.move(dt, 0, -1)
    if keys[pygame.K_s]:
        square.move(dt, 0, 1)
    if keys[pygame.K_a]:
        square.move(dt, -1, 0)
    if keys[pygame.K_d]:
        square.move(dt, 1, 0)

    # ----- Draw the Screen -----
    screen.fill((255, 255, 255))
    if wall.check_collision(square):
        screen.fill((100, 255, 100))

    # Draw the square
    square.draw()
    wall.draw()

    # Update the screen
    pygame.display.update()

    # ----- Clock Tick -----
    clock.tick()

# Clean up pygame on exit
exit()