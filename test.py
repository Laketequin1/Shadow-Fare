# ----- Setup ------
import pygame, os, sys, random, math
pygame.init()

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

    def draw(self):
        pygame.draw.rect(screen, self.color, (self.x, self.y, self.size, self.size))

    def move(self, dx, dy):
        self.x += dx
        self.y += dy

# Create a Square object at the center of the screen
square = Square(GAME_WIDTH // 2 - 50, GAME_HEIGHT // 2 - 50, 100, (255, 0, 0))

screen = pygame.display.set_mode((GAME_WIDTH, GAME_HEIGHT))

running = True
while running:
    # ----- Main Event Loop -----
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            exit()

    # Get the state of all keyboard keys
    keys = pygame.key.get_pressed()

    # Move the square based on WASD key presses
    if keys[pygame.K_w]:
        square.move(0, -5)
    if keys[pygame.K_s]:
        square.move(0, 5)
    if keys[pygame.K_a]:
        square.move(-5, 0)
    if keys[pygame.K_d]:
        square.move(5, 0)

    # ----- Draw the Screen -----
    screen.fill((255, 255, 255))

    # Draw the square
    square.draw()

    # Update the screen
    pygame.display.update()

    # ----- Clock Tick -----
    clock.tick(FPS)

# Clean up pygame on exit
exit()