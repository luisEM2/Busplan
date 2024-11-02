import pygame
import time
import xlsxwriter

from pygame.constants import MOUSEBUTTONDOWN
# pygame setup
pygame.init()
screen = pygame.display.set_mode((1920, 1080))
clock = pygame.time.Clock()
running = True
start = time.time()
bg = pygame.image.load("Background_Map.png")
bg = pygame.transform.scale(bg, (screen.get_width(), screen.get_height()))
positions = [[0.0265625, 0.65462963]]


while running:
    # poll for events
    # pygame.QUIT event means the user clicked X to close your window
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            with xlsxwriter.Workbook("File.xlsx") as workbook:
                sheet = workbook.add_worksheet()
                for i in range(len(positions)):
                    sheet.write(i, 0, positions[i][0])
                    sheet.write(i, 1, positions[i][1])
            running = False

        if event.type == pygame.MOUSEBUTTONDOWN:
            x, y = pygame.mouse.get_pos()
            x = x / screen.get_width()
            y = y / screen.get_height()
            print(x, y)
            positions.append((x, y))

    # fill the screen with a color to wipe away anything from last frame
    screen.blit(bg, (0, 0))
    for i in positions:
        pygame.draw.circle(screen, "red", (1920 * i[0], 1080 * i[1]), 10)

    # RENDER YOUR GAME HERE
    # flip() the display to put your work on screen
    pygame.display.update()

    clock.tick(60)  # limits FPS to 60

pygame.quit()