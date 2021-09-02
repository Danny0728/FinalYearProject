"""import pygame
from pygame.locals import *

pygame.init()

SCREEN_WIDTH = 600
SCREEN_HEIGHT = 600

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Button')

font = pygame.font.SysFont('Constantia', 30)

# define colors
BG = (200, 200, 200)
RED = (255, 0, 0)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

# define global variables
clicked = False
counter = 0


class Button():
    # colors for button and text
    button_col = (25, 190, 225)
    hover_col = (25, 190, 225)
    click_col = (25, 190, 225)
    text_col = WHITE

    width = 180
    height = 40

    def __init__(self, x, y, text):
        self.x = x
        self.y = y
        self.text = text

    def draw_button(self, surface):
        global clicked
        action = False

        # get mouse position
        pos = pygame.mouse.get_pos()

        # create pygame REct object for the button
        button_rect = Rect(self.x, self.y, self.width, self.height)

        # check mouse over and clicked conditions
        if button_rect.collidepoint(pos):
            if pygame.mouse.get_pressed(5)[0] == 1:
                clicked = True
                pygame.draw.rect(screen, self.click_col, button_rect)
            elif pygame.mouse.get_pressed(5)[0] == 0 and clicked == True:
                clicked = False
                action = True
            else:
                pygame.draw.rect(screen, self.hover_col, button_rect)
        else:
            pygame.draw.rect(screen, self.button_col, button_rect)

        # add shading to button
        pygame.draw.line(screen, WHITE, (self.x, self.y), (self.x + self.width, self.y), 2)
        pygame.draw.line(screen, WHITE, (self.x, self.y), (self.x, self.y + self.height), 2)
        pygame.draw.line(screen, BLACK, (self.x, self.y + self.height), (self.x + self.width, self.y + self.height), 2)
        pygame.draw.line(screen, BLACK, (self.x + self.width, self.y), (self.x + self.width, self.y + self.height), 2)

        # add text to button
        text_img = font.render(self.text, True, self.text_col)
        text_len = text_img.get_width()
        screen.blit(text_img, (self.x + int(self.width / 2) - int(text_len / 2), self.y + 5))
        return action


again = Button(75, 200, 'Play Again?')
quit = Button(325, 200, "QUIT?")
down = Button(75, 350, "DOWN")
up = Button(325, 350, "UP")

run = True
while run:

    screen.fill(BG)

    if again.draw_button():
        print("Again")
        counter = 0
    if quit.draw_button():
        print("QUIT")
    if down.draw_button():
        counter -= 1
    if up.draw_button():
        counter += 1

    counter_img = font.render(str(counter), True, RED)
    screen.blit(counter_img, (280, 450))


    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
    pygame.display.update()
pygame.quit()"""

import pygame


# button class
class Button():
    def __init__(self, x, y, image, scale):
        width = image.get_width()
        height = image.get_height()
        self.image = pygame.transform.scale(image, (int(width * scale), int(height * scale)))
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)
        self.clicked = False

    def draw(self, surface):
        action = False

        # get mouse position
        pos = pygame.mouse.get_pos()

        # check mouseover and clicked conditions
        if self.rect.collidepoint(pos):
            if pygame.mouse.get_pressed()[0] == 1 and self.clicked == False:
                action = True
                self.clicked = True

        if pygame.mouse.get_pressed()[0] == 0:
            self.clicked = False

        # draw button
        surface.blit(self.image, (self.rect.x, self.rect.y))

        return action
