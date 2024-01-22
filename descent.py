import pygame
from pygame.constants import QUIT, K_DOWN, K_UP, K_LEFT, K_RIGHT, K_SPACE
import random
import os
from screeninfo import get_monitors

pygame.init()

IMAGE_PATH = "img"

PLAYER_IMAGES = pygame.image.load(os.path.join(IMAGE_PATH, "player1.png"))
ENEMY_IMAGES = pygame.image.load(os.path.join(IMAGE_PATH, "enemy3.png"))

def get_screen_resolution():
    monitors = get_monitors()
    resolutions = [(monitor.width, monitor.height) for monitor in monitors]
    return resolutions


FPS = pygame.time.Clock()
resolutions = get_screen_resolution()
WIDTH, HEIGHT = resolutions[0][0], resolutions[0][1] - 50

FONT = pygame.font.SysFont("Verdana", 25)

COLOR_WHITE = (255, 255, 255)
COLOR_BLACK = (0, 0, 0)
COLOR_BLUE = (0, 0, 255)
COLOR_YELLOW = (255, 255, 0)

main_display = pygame.display.set_mode((WIDTH, HEIGHT))

bg_original = pygame.image.load(os.path.join(IMAGE_PATH, "background.jpg"))
bg_aspect_ratio = bg_original.get_width() / bg_original.get_height()
bg_height = int(HEIGHT)
bg_width = int(bg_height * bg_aspect_ratio)
bg = pygame.transform.scale(bg_original, (bg_width, bg_height))
bg_X1, bg_X2 = 0, bg.get_width()
bg_move = 1.2

original_player_size = PLAYER_IMAGES.get_size()
original_aspect_ratio = original_player_size[0] / original_player_size[1]
player_size = (int(WIDTH / 10), int(WIDTH / 10 / original_aspect_ratio))
player = pygame.transform.scale(
    pygame.image.load(os.path.join(IMAGE_PATH, "player1.png")), player_size
)
print(player_size)
print(player)
# player = pygame.image.load(os.path.join(IMAGE_PATH,"player1.png")).convert_alpha() # pygame.Surface(player_size)
# player_rect = player.get_rect()
player_rect = pygame.Rect(0, (HEIGHT / 2.5), *player_size)
player_move_down = [0, 4]
player_move_up = [0, -4]
player_move_right = [4, 0]
player_move_left = [-4, 0]


score = 0
image_index = 0
enemy_rotation_speed = 0.7


def create_enemy():
    enemy_image = pygame.image.load(
        os.path.join(IMAGE_PATH, "enemy3.png")
    ).convert_alpha()
    original_enemy_size = enemy_image.get_size()
    original_aspect_ratio = original_enemy_size[0] / original_enemy_size[1]
    enemy_size = (int(WIDTH / 14), int(WIDTH / 14 / original_aspect_ratio))
    enemy_original = pygame.transform.scale(enemy_image, enemy_size)
    enemy_angle = 0
    enemy = pygame.transform.rotate(enemy_original, enemy_angle)
    enemy_rect = pygame.Rect(
        WIDTH, random.randint(0, HEIGHT - enemy_size[1]), *enemy_size
    )
    enemy_move = [random.randint(-5, -2), 0]
    return [enemy, enemy_rect, enemy_move, enemy_angle, enemy_size]


def create_bonus():
    bonus_image = pygame.image.load(
        os.path.join(IMAGE_PATH, "bonus13.png")
    ).convert_alpha()
    original_bonus_size = bonus_image.get_size()
    original_aspect_ratio = original_bonus_size[0] / original_bonus_size[1]
    bonus_size = (int(WIDTH / 30), int(WIDTH / 30 / original_aspect_ratio))
    bonus = pygame.image.load(
        os.path.join(IMAGE_PATH, "bonus13.png")
    ).convert_alpha()  # pygame.Surface(bonus_size)
    bonus = pygame.transform.scale(bonus_image, bonus_size)
    bonus_rect = pygame.Rect(
        random.randint(0, WIDTH - bonus_size[0]), -bonus_size[1], *bonus_size
    )
    bonus_move = [0, random.randint(2, 4)]
    return [bonus, bonus_rect, bonus_move]


def create_score():
    score_image = pygame.image.load(
        os.path.join(IMAGE_PATH, "score2.png")
    ).convert_alpha()
    original_score_size = score_image.get_size()
    original_aspect_ratio = original_score_size[0] / original_score_size[1]
    score_size = (int(WIDTH / 25), int(WIDTH / 25 / original_aspect_ratio))
    score = pygame.image.load(
        os.path.join(IMAGE_PATH, "score2.png")
    ).convert_alpha()  # pygame.Surface(bonus_size)
    score = pygame.transform.scale(score_image, score_size)
    score_rect = pygame.Rect(
        WIDTH - score_size[0] * 2.2, score_size[1] / 2, *score_size
    )
    return [score, score_rect]


enemies = []
CREATE_ENEMY = pygame.USEREVENT + 1
pygame.time.set_timer(CREATE_ENEMY, 3000)

bonuses = []
CREATE_BONUS = pygame.USEREVENT + 2
pygame.time.set_timer(CREATE_BONUS, 3000)

CHANGE_IMAGE = pygame.USEREVENT + 3
pygame.time.set_timer(CHANGE_IMAGE, 200)

score_surface = create_score()[0]
score_rect = create_score()[1]


playing = True
paused = False
space_pressed = False
bg_paused = False


while playing:
    FPS.tick(120)
    for event in pygame.event.get():
        if event.type == QUIT:
            playing = False
        if event.type == CREATE_ENEMY and not paused:
            enemies.append(create_enemy())
        if event.type == CREATE_BONUS and not paused:
            bonuses.append(create_bonus())
        if event.type == CHANGE_IMAGE:
            # image_index += 1
            # if image_index >= len(PLAYER_IMAGES):
            #     image_index = 0
            pass
        elif event.type == pygame.KEYUP and event.key == pygame.K_SPACE:
            space_pressed = False

    if not bg_paused:
        bg_X1 -= bg_move
        bg_X2 -= bg_move

        if bg_X1 < -bg.get_width():
            bg_X1 = bg.get_width()

        if bg_X2 < -bg.get_width():
            bg_X2 = bg.get_width()

        main_display.blit(bg, (bg_X1, 0))
        main_display.blit(bg, (bg_X2, 0))

        for enemy in enemies:
            rotated_enemy = pygame.transform.rotate(enemy[0], enemy[3])
            enemy[1] = enemy[1].move(enemy[2])
            enemy[3] += enemy_rotation_speed
            rotated_enemy = pygame.transform.rotate(enemy[0], enemy[3])
            new_rect = rotated_enemy.get_rect(center=enemy[1].center)
            if enemy[1].right > 0:
                main_display.blit(rotated_enemy, new_rect.topleft)

            if player_rect.colliderect(enemy[1]):
                playing = False

        for bonus in bonuses:
            bonus[1] = bonus[1].move(bonus[2])
            if bonus[1].bottom < HEIGHT:
                main_display.blit(bonus[0], bonus[1])

            if player_rect.colliderect(bonus[1]):
                score += 1
                bonuses.pop(bonuses.index(bonus))


    keys = pygame.key.get_pressed()

    if keys[pygame.K_SPACE] and not space_pressed:
        space_pressed = True
        paused = not paused
        bg_paused = paused

    if not paused:
        if keys[K_DOWN] and player_rect.bottom < HEIGHT:
            player_rect = player_rect.move(player_move_down)

        if keys[K_UP] and player_rect.top > 0:
            player_rect = player_rect.move(player_move_up)

        if keys[K_RIGHT] and player_rect.right < WIDTH:
            player_rect = player_rect.move(player_move_right)

        if keys[K_LEFT] and player_rect.left > 0:
            player_rect = player_rect.move(player_move_left)


    main_display.blit(score_surface, score_rect)
    main_display.blit(FONT.render(str(score), True, COLOR_WHITE), (WIDTH - 50, 20))
    main_display.blit(player, player_rect)

    pygame.display.flip()

    for enemy in enemies:
        if enemy[1].left < 0:
            enemies.pop(enemies.index(enemy))

    pygame.display.flip()
    for bonus in bonuses:
        if bonus[1].bottom > HEIGHT:
            bonuses.pop(bonuses.index(bonus))
