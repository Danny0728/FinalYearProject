import csv
import os
import random

import pygame
import pygame_menu

import button

pygame.mixer.init()
pygame.init()
pygame.font.init()

# players remaining lives
lives = 5
# score of the player
score = 0
# Resolution
SCREEN_WIDTH = 800
SCREEN_HEIGHT = int(0.8 * SCREEN_WIDTH)

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Death Quest')

# define game variables
start_game = False
start_intro = False
game_controls = False
GRAVITY = 0.75
SCROLL_THRESHOLD = 200

# TILE_SIZE = 40
ROWS = 16
COLS = 150
# this is the new tile size as the screen should be divided in equal parts of pixel
TILE_SIZE = SCREEN_HEIGHT // ROWS
TILE_TYPES = 21
MAX_LEVEL = 3
screen_scroll = 0
bg_scroll = 0
level = 1
congratulations_counter = MAX_LEVEL

# set framerate
clock = pygame.time.Clock()
FPS = 60
# define player action variables
moving_left = False
moving_right = False
shoot = False
grenade = False
grenade_in_air = False

# load music
pygame.mixer.music.load('audio/music2.mp3')
pygame.mixer.music.set_volume(0.2)
pygame.mixer.music.play(-1, 0.0, 5000)

# Sounds
jump_sound = pygame.mixer.Sound('audio/jump.wav')
jump_sound.set_volume(0.5)
shoot_sound = pygame.mixer.Sound('audio/shot.wav')
shoot_sound.set_volume(0.5)
explosion_sound = pygame.mixer.Sound('audio/grenade.wav')
explosion_sound.set_volume(0.5)
congratulations_sound = pygame.mixer.Sound('audio/congratulations.mp3')
congratulations_sound.set_volume(0.5)
gameover_sound = pygame.mixer.Sound('audio/gameover2.wav')
gameover_sound.set_volume(0.5)

# load images
pine1_img = pygame.image.load('img/Background/pine1.png').convert_alpha()
pine2_img = pygame.image.load('img/Background/pine2.png').convert_alpha()
mountain_img = pygame.image.load('img/Background/mountain.png').convert_alpha()
sky_img = pygame.image.load('img/Background/sky_cloud.png').convert_alpha()
gamover_img = pygame.image.load('img/other images/gameover.png').convert_alpha()
gamover_img = pygame.transform.scale(gamover_img, (400, 400))

# congratulations image
congratulations_img = pygame.image.load('img/other images/congratulations.jpg').convert_alpha()
congratulations_img = pygame.transform.scale(congratulations_img, (SCREEN_WIDTH, SCREEN_HEIGHT))
# button images
start_img = pygame.image.load('img/other images/start.jpg').convert_alpha()
exit_img = pygame.image.load('img/other images/exit.jpg').convert_alpha()
restart_img = pygame.image.load('img/other images/restart_btn.png').convert_alpha()
control_img = pygame.image.load('img/other images/control.jpg').convert_alpha()
score_img = pygame.image.load('img/other images/score.jpeg').convert_alpha()

# store icons in list
img_list = []
for x in range(TILE_TYPES):
    img = pygame.image.load(f'img/tile/{x}.png').convert_alpha()
    img = pygame.transform.scale(img, (TILE_SIZE, TILE_SIZE))
    img_list.append(img)

# bullet
bullet_img = pygame.image.load('img/icons/bullet.png').convert_alpha()
# grenade
grenade_img = pygame.image.load('img/icons/grenade.png').convert_alpha()
# reload image
bullet_img_display = pygame.image.load('img/icons/bullet_show.png').convert_alpha()

# item boxes
health_box_img = pygame.image.load('img/icons/health_box.png').convert_alpha()
ammo_box_img = pygame.image.load('img/icons/ammo_box.png').convert_alpha()
grenade_box_img = pygame.image.load('img/icons/grenade_box.png').convert_alpha()

item_boxes = {
    'Health': health_box_img,
    'Ammo': ammo_box_img,
    'Grenade': grenade_box_img
}

# define colors
BG = (144, 201, 120)
RED = (255, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
BLACK = (0, 0, 0)

# remaining lives image
lives_img = pygame.image.load('img/other images/heart3.png').convert_alpha()

# define fonts
font = pygame.font.SysFont('Futura', 30)


def draw_text(text, text_font, text_color, x, y):
    img = text_font.render(text, True, text_color)
    screen.blit(img, (x, y))


def draw_bg():
    screen.fill(BG)
    width = sky_img.get_width()
    for x in range(5):
        screen.blit(sky_img, (x * width - bg_scroll * 0.5, 0))
        screen.blit(mountain_img, (x * width - bg_scroll * 0.6, SCREEN_HEIGHT - mountain_img.get_height() - 300))
        screen.blit(pine1_img, (x * width - bg_scroll * 0.7, SCREEN_HEIGHT - pine1_img.get_height() - 150))
        screen.blit(pine2_img, (x * width - bg_scroll * 0.8, SCREEN_HEIGHT - pine2_img.get_height()))


def reset_level():
    # we want to reset all the required variables to start the game to the value which was before
    decoration_group.empty()
    water_group.empty()
    explosion_group.empty()
    exit_group.empty()
    bullet_group.empty()
    grenade_group.empty()
    item_box_group.empty()
    enemy_group.empty()

    # now we have to reset the world data list that we have set to see the world map
    # create a empty tile list
    data = []
    for row in range(ROWS):
        r = [-1] * COLS
        data.append(r)
    return data


# **************************************** Soldier Class *******************************************************
class Soldier(pygame.sprite.Sprite):
    def __init__(self, char_type, x, y, scale, velocity, ammo, grenades):
        pygame.sprite.Sprite.__init__(self)
        self.ammo = ammo
        self.start_ammo = ammo
        self.grenades = grenades
        self.alive = True
        self.velocity = velocity
        self.direction = 1
        self.shoot_cooldown = 0
        self.health = 100
        self.max_health = self.health
        self.jump = False
        self.in_air = True
        self.flip = False
        self.vel_y = 0
        self.char_type = char_type
        self.animation_list = []
        self.frame_index = 0
        self.action = 0
        self.update_time = pygame.time.get_ticks()

        # ai specific variables
        self.move_counter = 0
        self.idling = False
        self.idling_counter = 0
        self.vision = pygame.Rect(0, 0, 150, 20)
        # the third variable is the main attribute as it decides how far enemy can see

        # for player
        if self.char_type == 'player':
            animation_list = ['Idle', 'Run', 'Jump', 'Death']
            for animation in animation_list:
                temp_list = []
                # check for number of frames in a folder
                num_of_frames = len(os.listdir(f"./img/deadpool/{animation}"))
                for i in range(num_of_frames):
                    img = pygame.image.load(f"./img/deadpool/{animation}/{i}.png").convert_alpha()
                    img = pygame.transform.scale(img, (int(img.get_width() * scale), int(img.get_height() * scale)))
                    temp_list.append(img)
                self.animation_list.append(temp_list)

            self.image = self.animation_list[self.action][self.frame_index]
            self.rect = self.image.get_rect()
            self.rect.center = (x, y)
            self.width = self.image.get_width()
            self.height = self.image.get_height()

        # for enemy's
        elif self.char_type == 'enemy':
            animation_list = ['Idle', 'Run', 'Jump', 'Death']
            for animation in animation_list:
                temp_list = []
                # check for number of frames in a folder
                num_of_frames = len(os.listdir(f"./img/enemy/{animation}"))
                for i in range(num_of_frames):
                    img = pygame.image.load(f"./img/enemy/{animation}/{i}.png").convert_alpha()
                    img = pygame.transform.scale(img, (int(img.get_width() * scale), int(img.get_height() * scale)))
                    temp_list.append(img)
                self.animation_list.append(temp_list)

            self.image = self.animation_list[self.action][self.frame_index]
            self.rect = self.image.get_rect()
            self.rect.center = (x, y)
            self.width = self.image.get_width()
            self.height = self.image.get_height()

    def move(self, mov_left, mov_right):
        # reset movement variables
        global score
        screen_scroll = 0
        dx = 0
        dy = 0

        # assign movement variables if moving left or right
        if mov_left:
            dx = -self.velocity
            self.flip = True
            self.direction = -1

        if mov_right:
            dx = self.velocity
            self.flip = False
            self.direction = 1

        # Jump    should the player be allowed to shoot when he is in the air
        if self.jump and self.in_air == False:
            self.vel_y = -11
            self.jump = False
            self.in_air = True

        # apply gravity
        self.vel_y += GRAVITY
        if self.vel_y > 10:
            self.vel_y = 10
        dy += self.vel_y

        # check collision
        for tile in world.obstacle_list:
            # check for collision in x direction
            if tile[1].colliderect(self.rect.x + dx, self.rect.y, self.width, self.height):
                dx = 0
                # flip ur direction whenever u can't go further ahead due to obstacle (only for enemy's)
                enemy.direction *= -1
            if tile[1].colliderect(self.rect.x, self.rect.y + dy, self.width, self.height):
                # check if the player is jumping
                if self.vel_y < 0:
                    self.vel_y = 0
                    # check if he had bump his head somewhere
                    # tile[1] contains the x and y co-ordinates of the obstacle
                    dy = tile[1].bottom - self.rect.top
                # check if the player is falling
                elif self.vel_y >= 0:
                    self.vel_y = 0
                    self.in_air = False
                    # check if his legs i.e bottom part of the player collides with other objects
                    dy = tile[1].top - self.rect.bottom

        # check if the player comes in contact with the water
        if pygame.sprite.spritecollide(self, water_group, False):
            self.health = 0
            score -= 100 if score - 100 >= 0 else score  # This checks if the score is not negative

        # check if the player fall of the map
        if self.rect.y > SCREEN_HEIGHT:
            self.health = 0
            score -= 100 if score - 100 >= 0 else score  # This checks if the score is not negative

        # check if the player collides with the exit group (end of the level)
        level_complete = False
        if pygame.sprite.spritecollide(self, exit_group, False):
            level_complete = True
            score += 250

        # check if the player goes off the screen
        if self.char_type == 'player' and player.alive:
            if self.rect.left + dx < 0 or self.rect.right + dx > SCREEN_WIDTH:
                dx = 0
                # check if the player has reached the exit mark
                # if the player has reached the exit mark send player to the next level
                '''if tile[1].colliderect(player.rect.x, player.self.y, self.width, self.height):
                    level += 1'''
        # update rectangle position
        self.rect.x += dx
        self.rect.y += dy

        # check is only for the player part of the instance
        if self.char_type == 'player' and player.alive:
            if (self.rect.right > SCREEN_WIDTH - SCROLL_THRESHOLD and bg_scroll < (
                    world.level_length * TILE_SIZE) - SCREEN_WIDTH) or \
                    (self.rect.left < SCROLL_THRESHOLD and bg_scroll > abs(dx)):
                self.rect.x -= dx
                screen_scroll = -dx  # cause we need to keep the player stationary but the screen and the background
                # should move
        return screen_scroll, level_complete

    def shoot(self):
        if self.shoot_cooldown == 0 and self.ammo > 0:  # This section is not met as the shoot_cooldown is never zero
            # after it enters
            # this if loop so we need to decrease this countdown so that it can shoot again (in update method)
            self.shoot_cooldown = 20
            bullet = Bullet(self.rect.centerx + (0.75 * self.rect.size[0] * self.direction),
                            self.rect.centery, self.direction)
            bullet_group.add(bullet)
            self.ammo -= 1  # reducing the bullets each time
            shoot_sound.play()

    def ai(self):
        # first we just have to make the enemy's move back and forth
        if self.alive and player.alive:
            if self.idling == False and random.randint(1, 200) == 1:
                self.idling = True
                self.update_action(0)
                self.idling_counter = 100
            # check if the player is in the vision
            if self.vision.colliderect(player.rect):
                # stop running
                self.update_action(0)  # 0: IDLE
                # shoot
                self.shoot()
            else:
                if not self.idling:  # i.e self.idling == False
                    if self.direction == 1:
                        ai_moving_right = True
                    else:
                        ai_moving_right = False

                    ai_moving_left = not ai_moving_right
                    self.move(ai_moving_left, ai_moving_right)
                    self.update_action(1)
                    self.move_counter += 1
                    self.vision.center = (self.rect.centerx + 75 * self.direction, self.rect.centery)
                    # THis is the vision of each enemy
                    # pygame.draw.rect(screen, RED, self.vision)

                    if self.move_counter > TILE_SIZE:
                        self.direction *= -1
                        self.move_counter *= -1
                else:
                    self.idling_counter -= 1
                    if self.idling_counter == 0:
                        self.idling = False

        # scroll
        self.rect.x += screen_scroll

    def update(self):
        self.update_animation()
        self.check_alive()

        # check for cooldown
        if self.shoot_cooldown > 0:  # This is the countdown for shooting another bullet
            self.shoot_cooldown -= 1

    def update_animation(self):

        # updating our game animation here
        ANIMATION_COOLDOWN = 100
        # update the given image
        try:
            self.image = self.animation_list[self.action][self.frame_index]
        except:
            pass
        '''start_frame = time.time()
        if self.char_type == 'player' and (self.action == 4 or self.action == 5):
            ANIMATION_COOLDOWN = 1000
            current_image = int((time.time() - start_frame) * (FPS // 3) % len(self.animation_list[self.action]))
            self.image = self.animation_list[self.action][current_image]'''

        if pygame.time.get_ticks() - self.update_time > ANIMATION_COOLDOWN:
            self.update_time = pygame.time.get_ticks()
            self.frame_index += 1

        # if the animation comes to an end reset the list of animation
        try:
            if self.frame_index >= len(self.animation_list[self.action]):
                if self.action == 3:
                    self.frame_index = len(self.animation_list[self.action]) - 1
                elif player.action == 4:
                    self.frame_index = len(self.animation_list[self.action]) - 1
                else:
                    self.frame_index = 0
        except:
            pass

    def update_action(self, new_action):
        # check if the new action is different from the previous
        if new_action != self.action:
            self.action = new_action
            # update the animation list
            self.frame_index = 0
            self.update_time = pygame.time.get_ticks()

    def check_alive(self):
        if self.health <= 0:
            self.health = 0
            self.velocity = 0
            self.alive = False
            self.update_action(3)

    def draw(self):
        screen.blit(pygame.transform.flip(self.image, self.flip, False),
                    self.rect)
        # pygame.draw.rect(screen, RED, self.rect, 1)


# **************************** End of Soldier Class ***********************************************

class World:
    def __init__(self):
        self.obstacle_list = []

    def process_data(self, data):
        self.level_length = len(data[0])  # cause every item has same number of columns
        global player, health_bar
        # iterate through each value in level data file
        for y, row in enumerate(data):
            for x, tile in enumerate(row):
                if tile >= 0:  # i.e if it has something in that pixel
                    img = img_list[tile]
                    img_rect = img.get_rect()
                    img_rect.x = x * TILE_SIZE
                    img_rect.y = y * TILE_SIZE
                    tile_data = (img, img_rect)
                    # Only the tile from 0 to 8 are obstacles to the soldier class
                    if 0 <= tile <= 8:
                        self.obstacle_list.append(tile_data)
                    elif tile == 9 or tile == 10:
                        water = Water(img, x * TILE_SIZE, y * TILE_SIZE)
                        water_group.add(water)
                    elif 11 <= tile <= 14:  # decorations
                        decoration = Decoration(img, x * TILE_SIZE, y * TILE_SIZE)
                        decoration_group.add(decoration)
                    elif tile == 15:  # create player
                        player = Soldier('player', x * TILE_SIZE, y * TILE_SIZE, 1.9, 5, 20, 10)
                        # (char_type, x, y, scale, velocity, ammo, grenades)
                        health_bar = HealthBar(10, 10, player.health, player.health)
                    elif tile == 16:  # create enemy
                        enemy = Soldier('enemy', x * TILE_SIZE, y * TILE_SIZE, 1.65, 2, 20, 0)
                        enemy_group.add(enemy)
                    elif tile == 17:  # create ammo box
                        itembox = ItemBlocks('Ammo', x * TILE_SIZE, y * TILE_SIZE)
                        item_box_group.add(itembox)
                    elif tile == 18:  # create grenade box
                        itembox = ItemBlocks('Grenade', x * TILE_SIZE, y * TILE_SIZE)
                        item_box_group.add(itembox)
                    elif tile == 19:  # create heal box
                        itembox = ItemBlocks('Health', x * TILE_SIZE, y * TILE_SIZE)
                        item_box_group.add(itembox)
                    elif tile == 20:  # create exit
                        exit = Exit(img, x * TILE_SIZE, y * TILE_SIZE)
                        exit_group.add(exit)
        return player, health_bar

    def draw_world_map(self):
        for tile in self.obstacle_list:
            tile[1][0] += screen_scroll
            screen.blit(tile[0], tile[1])


class Decoration(pygame.sprite.Sprite):
    def __init__(self, img, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = img
        self.rect = self.image.get_rect()  # this creates a rectangle out of the image
        self.rect.midtop = (x + TILE_SIZE // 2, y + (TILE_SIZE - self.image.get_height()))

    def update(self):
        self.rect.x += screen_scroll


class Water(pygame.sprite.Sprite):
    def __init__(self, img, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = img
        self.rect = self.image.get_rect()  # this creates a rectangle out of the image
        self.rect.midtop = (x + TILE_SIZE // 2, y + (TILE_SIZE - self.image.get_height()))

    def update(self):
        self.rect.x += screen_scroll


class Exit(pygame.sprite.Sprite):
    def __init__(self, img, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = img
        self.rect = self.image.get_rect()  # this creates a rectangle out of the image
        self.rect.midtop = (x + TILE_SIZE // 2, y + (TILE_SIZE - self.image.get_height()))

    def update(self):
        self.rect.x += screen_scroll


class ItemBlocks(pygame.sprite.Sprite):
    def __init__(self, item_type, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.item_type = item_type
        self.image = item_boxes[self.item_type]
        self.rect = self.image.get_rect()
        self.rect.midtop = (x + TILE_SIZE // 2, y + (TILE_SIZE - self.image.get_height()))

    def update(self):
        # scroll
        self.rect.x += screen_scroll
        # check if the player has collide with the item box
        if pygame.sprite.collide_rect(self, player):  # self means itembox rectangle and player is rect for player
            # check type of item box : heal, grenades, ammo
            if self.item_type == 'Health':
                player.health += 30
                if player.health > player.max_health:
                    player.health = player.max_health
            elif self.item_type == 'Ammo':
                player.ammo += 20
            elif self.item_type == 'Grenade':
                player.grenades += 5
            self.kill()


class HealthBar:
    def __init__(self, x, y, health, max_health):
        self.x = x
        self.y = y
        self.health = health
        self.max_health = max_health

    def draw(self, health):
        self.health = health
        curve = 2
        rect_fill = 10
        ratio = self.health / self.max_health
        pygame.draw.rect(screen, BLACK, (self.x - 2, self.y - 2, 154, 24), 2, 3)
        if player.health <= 0:
            pygame.draw.rect(screen, RED, (self.x, self.y, 150, 20), rect_fill, curve)
        else:
            pygame.draw.rect(screen, RED, (self.x, self.y, 150, 20), rect_fill, curve)
            pygame.draw.rect(screen, GREEN, (self.x, self.y, int(150 * ratio), 20), rect_fill, curve)


class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, direction):
        pygame.sprite.Sprite.__init__(self)
        self.speed = 10
        self.image = bullet_img
        # now we need to create a rectangle for the image
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.direction = direction

    def update(self):
        global score
        self.rect.x += (self.direction * self.speed) + screen_scroll

        # check for the bullet on screen
        if self.rect.right < 0 or self.rect.left > SCREEN_WIDTH:
            self.kill()

        # check for the characters collision
        if pygame.sprite.spritecollide(player, bullet_group, False):
            if player.alive:
                player.health -= 5
                self.kill()

        # check for the obstacle collision
        for tile in world.obstacle_list:
            if tile[1].colliderect(self.rect):
                self.kill()

        damage = 25
        for Enemy in enemy_group:
            if pygame.sprite.spritecollide(Enemy, bullet_group, False):
                if Enemy.alive:
                    Enemy.health -= damage
                    if Enemy.health <= 0:
                        score += 100
                    else:
                        score = score
                    self.kill()


class Grenade(pygame.sprite.Sprite):
    def __init__(self, x, y, direction):
        pygame.sprite.Sprite.__init__(self)
        self.timer = 100
        self.vel_y = -11
        self.speed = 7
        self.image = grenade_img
        # now we need to create a rectangle for the image
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.direction = direction
        self.width = self.image.get_width()
        self.height = self.image.get_height()

    def update(self):

        global score
        self.vel_y += GRAVITY
        dx = self.direction * self.speed
        dy = self.vel_y

        # check for the collision with the floor
        for tile in world.obstacle_list:
            # check collision in x direct
            # check for the collision with walls
            if tile[1].colliderect(self.rect.x + dx, self.rect.y, self.width, self.height):
                self.direction *= -1
                dx = self.direction * self.speed
            # check for the collusion in y direction
            if tile[1].colliderect(self.rect.x, self.rect.y + dy, self.width, self.height):
                self.speed = 0
                # check if the player is throwing
                if self.vel_y < 0:
                    self.vel_y = 0
                    # check if grenade had bumped
                    dy = tile[1].bottom - self.rect.top
                # check if the player is falling
                elif self.vel_y >= 0:
                    self.vel_y = 0
                    # check if his legs i.e bottom part of the player collides with other objects
                    dy = tile[1].top - self.rect.bottom

        # update grenade position
        self.rect.x += dx + screen_scroll  # change in x coordinate
        self.rect.y += dy  # change in y coordinate

        '''# check for the enemy collisions
        if pygame.sprite.spritecollide(enemy, grenade_group, False):
            if enemy.alive:
                enemy.health -= 50
                self.kill()'''

        # countdown timer
        self.timer -= 1
        if self.timer <= 0:
            self.kill()
            explosion = Explosion(self.rect.x, self.rect.y, 0.75)
            explosion_group.add(explosion)
            explosion_sound.play()

            # do damage to anyone near grenade
            # for player
            if abs(self.rect.centerx - player.rect.centerx) < TILE_SIZE and \
                    abs(self.rect.centery - player.rect.centery) < TILE_SIZE:
                player.health -= 80

            elif abs(self.rect.centerx - player.rect.centerx) < TILE_SIZE * 2 and \
                    abs(self.rect.centery - player.rect.centery) < TILE_SIZE * 2:
                player.health -= 50

            elif abs(self.rect.centerx - player.rect.centerx) < TILE_SIZE * 3 and \
                    abs(self.rect.centery - player.rect.centery) < TILE_SIZE * 3:
                player.health -= 20

            # if enemy is closer to the grenade explosion then it will damage more and vice versa
            # for enemy
            damage = 0
            for each_enemy in enemy_group:
                if abs(self.rect.centerx - each_enemy.rect.centerx) < TILE_SIZE and \
                        abs(self.rect.centery - each_enemy.rect.centery) < TILE_SIZE:
                    damage = 80
                    if each_enemy.health - damage > 0:
                        each_enemy.health -= damage
                        score += damage
                    else:
                        score += each_enemy.health
                        each_enemy.health -= damage

                elif abs(self.rect.centerx - each_enemy.rect.centerx) < TILE_SIZE * 2 and \
                        abs(self.rect.centery - each_enemy.rect.centery) < TILE_SIZE * 2:
                    damage = 50

                    if each_enemy.health - damage > 0:
                        each_enemy.health -= damage
                        score += damage
                    else:
                        score += each_enemy.health
                        each_enemy.health -= damage

                elif abs(self.rect.centerx - each_enemy.rect.centerx) < TILE_SIZE * 3 and \
                        abs(self.rect.centery - each_enemy.rect.centery) < TILE_SIZE * 3:
                    damage = 30
                    if each_enemy.health - damage > 0:
                        each_enemy.health -= damage
                        score += damage
                    else:
                        score += each_enemy.health
                        each_enemy.health -= damage


# ***************** END of class GRENADE ************************


class Explosion(pygame.sprite.Sprite):
    def __init__(self, x, y, scale):
        pygame.sprite.Sprite.__init__(self)
        self.images = []
        for num in range(1, 6):
            image = pygame.image.load(f"img/explosion/exp{num}.png").convert_alpha()
            image = pygame.transform.scale(image, (int(image.get_width() * scale), int(image.get_height() * scale)))
            self.images.append(image)
        self.frame_index = 0
        self.image = self.images[self.frame_index]
        # now we need to create a rectangle for the image
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.counter = 0

    def update(self):
        # scroll the explosion of grenade
        self.rect.x += screen_scroll
        # the explosion is going to run in a constant speed through images
        # so let's make a variable to handle the speed of the explosion animation

        EXPLOSION_SPEED = 4
        self.counter += 1
        if self.counter >= EXPLOSION_SPEED:
            self.counter = 0
            self.frame_index += 1
            # if the animation is complete then reset or delete
            if self.frame_index >= len(self.images):
                self.kill()
            else:
                self.image = self.images[self.frame_index]


class Transition:
    def __init__(self, direction, color, speed):
        self.direction = direction
        self.color = color
        self.speed = speed
        self.transition_counter = 0

    def screen_transition(self):
        transition_complete = False
        self.transition_counter += self.speed
        if self.direction == 1:  # starting new game
            pygame.draw.rect(screen, self.color,
                             (0 - self.transition_counter, 0, SCREEN_WIDTH // 2, SCREEN_HEIGHT))  # left
            pygame.draw.rect(screen, self.color, (SCREEN_WIDTH // 2 + self.transition_counter, 0,
                                                  SCREEN_WIDTH // 2, SCREEN_HEIGHT))  # right
            # self.transition = screenheight and screen width
            # THis is for the animation to go up
            pygame.draw.rect(screen, self.color, (0, 0 - self.transition_counter, SCREEN_WIDTH, SCREEN_HEIGHT // 2))
            # this is the animation to go down
            pygame.draw.rect(screen, self.color,
                             (0, SCREEN_HEIGHT // 2 + self.transition_counter, SCREEN_WIDTH, SCREEN_HEIGHT // 2))
        if self.direction == 2:  # when player dies
            pygame.draw.rect(screen, self.color, (0, 0, SCREEN_WIDTH, 0 + self.transition_counter))
        if self.direction == 3:  # control transition
            pygame.draw.rect(screen, self.color, (0, 0, SCREEN_WIDTH - self.transition_counter, SCREEN_HEIGHT))
        if self.transition_counter >= SCREEN_HEIGHT:
            transition_complete = True

        return transition_complete


# create a instance of Transition class
death_transition = Transition(2, (200, 0, 12), 5)
new_game_transition = Transition(1, (0, 0, 0), 5)
congratulations_transition = Transition(3, (255, 255, 255), 5)
end_game_transition = Transition(2, BLACK, 5)

# create buttons
start_button = button.Button(SCREEN_WIDTH // 2 - 130, SCREEN_HEIGHT // 2 - 100, start_img, 0.75)
control_button = button.Button(SCREEN_WIDTH // 2 - 130, SCREEN_HEIGHT // 2 - 30, control_img, 0.75)
score_button = button.Button(SCREEN_WIDTH // 2 - 130, SCREEN_HEIGHT // 2 + 40, score_img, 0.75)
exit_button = button.Button(SCREEN_WIDTH // 2 - 130, SCREEN_HEIGHT // 2 + 110, exit_img, 0.75)
restart_button = button.Button(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2, restart_img, 1.5)

# creation of  groups
enemy_group = pygame.sprite.Group()
bullet_group = pygame.sprite.Group()
grenade_group = pygame.sprite.Group()
explosion_group = pygame.sprite.Group()
item_box_group = pygame.sprite.Group()
decoration_group = pygame.sprite.Group()
water_group = pygame.sprite.Group()
exit_group = pygame.sprite.Group()
# enemy_health_bar_group = pygame.sprite.Group()

# create an empty list
world_data = []

for row in range(ROWS):
    # this is just for 1 row which has 150 columns but we have 16 ROWS so we need to iterate
    r = [-1] * COLS
    # This is the list of lists for the whole grid (map)
    world_data.append(r)

# load in world_map data
with open(f"level{level}_data.csv", newline='') as csvfile:
    reader = csv.reader(csvfile, delimiter=',')
    for x, row in enumerate(reader):
        for y, tile in enumerate(row):
            world_data[x][y] = int(tile)  # we are converting into int cause csv gives string as output

world = World()
player, health_bar = world.process_data(world_data)

run = True
while run:
    clock.tick(FPS)
    # This is the MENU OF THE GAME
    if not start_game:
        # draw main-menu
        screen.fill(BG)

        if start_button.draw(screen):
            start_game = True
            start_intro = True
        if control_button.draw(screen):
            font = pygame_menu.font.FONT_8BIT

            menu = pygame_menu.Menu('Controls', SCREEN_WIDTH, SCREEN_HEIGHT)
            menu.add.label("Press 'SPACEBAR' to shoot ", font, underline_color=(255, 255, 0))
            menu.add.label("Press 'Q' to launch Grenades ")
            menu.add.label("Press 'W' to Jump ")
            menu.add.label("Press 'A & D' to move")

            menu.add.button("EXIT", pygame_menu.events.EXIT, back_count=2, background_color=(120, 240, 120),
                            border_color=BLACK, font_name=font)

            menu.mainloop(screen)
        if score_button.draw(screen):
            pass
        if exit_button.draw(screen):
            run = False
    else:
        # update background
        draw_bg()
        # draw world map
        world.draw_world_map()
        health_bar.draw(player.health)
        # show ammo
        draw_text('Ammo: ', font, WHITE, 10, 40)
        for x in range(player.ammo):
            screen.blit(bullet_img_display, (90 + (x * 10), 40))

        # show grenades
        draw_text('Grenade: ', font, WHITE, 10, 60)
        for x in range(player.grenades):
            screen.blit(grenade_img, (120 + (x * 15), 60))

        # show lives
        for x in range(lives):
            screen.blit(lives_img, (680 + (x * 20), 5))
        # show score
        draw_text(f'Score: {score}', font, WHITE, 680, 30)

        player.update()
        player.draw()

        for enemy in enemy_group:
            enemy.ai()
            enemy.update()
            enemy.draw()

        # update and draw groups
        bullet_group.update()
        grenade_group.update()
        explosion_group.update()
        item_box_group.update()
        decoration_group.update()
        water_group.update()
        exit_group.update()

        grenade_group.draw(screen)
        bullet_group.draw(screen)
        explosion_group.draw(screen)
        item_box_group.draw(screen)
        decoration_group.draw(screen)
        water_group.draw(screen)
        exit_group.draw(screen)

        # check if the start button is being clicked
        if start_intro:
            if new_game_transition.screen_transition():
                start_intro = False
                new_game_transition.transition_counter = 0

        if player.alive:
            if shoot:
                player.shoot()
            elif grenade and grenade_in_air == False and player.grenades > 0:
                grenade = Grenade(player.rect.centerx + (0.5 * player.rect.size[0] * player.direction),
                                  player.rect.top,
                                  player.direction)
                grenade_group.add(grenade)
                player.grenades -= 1
                grenade_in_air = True
            if player.in_air:
                player.update_action(2)  # 2:jump
            # update player actions
            elif moving_left or moving_right:
                player.update_action(1)  # 1 means run and 0 means idle
            else:
                player.update_action(0)
            screen_scroll, level_complete = player.move(moving_left, moving_right)
            bg_scroll -= screen_scroll

            # Moving on to the next level
            if congratulations_counter == 0:
                screen.fill(BG)
                screen.blit(congratulations_img, (0, 0))
                pygame.mixer.music.stop()
                congratulations_sound.play()
            else:
                if level_complete:
                    start_intro = True
                    new_game_transition.transition_counter = 0
                    level += 1
                    congratulations_counter -= 1
                    bg_scroll = 0
                    world_data = reset_level()

                    # load in world_map data
                    if level <= MAX_LEVEL:
                        with open(f"level{level}_data.csv", newline='') as csvfile:
                            reader = csv.reader(csvfile, delimiter=',')
                            for x, row in enumerate(reader):
                                for y, tile in enumerate(row):
                                    world_data[x][y] = int(tile)

                        world = World()
                        player, health_bar = world.process_data(world_data)
        else:
            screen_scroll = 0
            # i have typed screen scroll outside the if statement cause until the button is clicked other characters
            # should not move
            """I have to draw the restart button when the transition is complete 
            and the transition is completed when it's height reaches about same as the screen height"""
            if lives > 1:
                if death_transition.screen_transition():
                    if restart_button.draw(screen):
                        lives -= 1
                        death_transition.transition_counter = 0
                        start_intro = True
                        bg_scroll = 0
                        world_data = reset_level()
                        # load in world_map data
                        with open(f"level{level}_data.csv", newline='') as csvfile:
                            reader = csv.reader(csvfile, delimiter=',')
                            for x, row in enumerate(reader):
                                for y, tile in enumerate(row):
                                    world_data[x][y] = int(tile)
                        world = World()
                        player, health_bar = world.process_data(world_data)

            else:
                if end_game_transition.screen_transition():
                    screen.fill(BLACK)
                    pygame.mixer.music.stop()
                    gameover_sound.play()
                    screen.blit(gamover_img, (180, 130))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False

        # Keyboard process
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_a:
                moving_left = True
            if event.key == pygame.K_d:
                moving_right = True
            if event.key == pygame.K_SPACE:
                """player.action = 4  # This is the part i just change
                player.update_animation()"""
                shoot = True
            if event.key == pygame.K_q:
                """player.action = 5
                player.update_animation()  # This is the part i just change"""
                grenade = True
            if event.key == pygame.K_w and player.alive:
                player.jump = True
                jump_sound.play()
            if event.key == pygame.K_ESCAPE:
                run = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            player.update_action(4)

        # button release
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_a:
                moving_left = False
            if event.key == pygame.K_d:
                moving_right = False
            if event.key == pygame.K_SPACE:
                shoot = False
            if event.key == pygame.K_q:
                grenade = False
                grenade_in_air = False

    pygame.display.update()

"""NOTE 1. Add the dracula story at the start
NOTE 2 . Put controls in the main menu section
NOTE 3 Score should be displayed
NOTE 4: THe player doesnt do the following animation properly while shooting
    He just swaps through the animation cause the space bar key is unpressed so quickly
    (We can )
NOTE 5: We need to add the sound for death and add some other sounds too
NOTE 6 : Let's make a new window in help about controls and how to score"""
