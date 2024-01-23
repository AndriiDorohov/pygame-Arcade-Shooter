import pygame
import random
import os
import time
from pygame.constants import QUIT, K_DOWN, K_UP, K_LEFT, K_RIGHT, K_SPACE
from screeninfo import get_monitors


pygame.init()

IMAGE_PATH = "img"


def get_screen_resolution():
    monitors = get_monitors()
    resolutions = [(monitor.width, monitor.height) for monitor in monitors]
    return resolutions


resolutions = get_screen_resolution()


def load_resources():
    global PLAYER_IMAGES, ENEMY_IMAGES, BOOM_IMAGES, PAUSE_IMAGES, GAMEOVER_IMAGES, WIDTH, HEIGHT, FONT, COLOR_WHITE, COLOR_BLACK, COLOR_BLUE, COLOR_YELLOW, main_display, FPS
    PLAYER_IMAGES = pygame.image.load(os.path.join(IMAGE_PATH, "player1.png"))
    ENEMY_IMAGES = pygame.image.load(os.path.join(IMAGE_PATH, "enemy3.png"))
    BOOM_IMAGES = pygame.image.load(os.path.join(IMAGE_PATH, "boom1.png"))
    PAUSE_IMAGES = pygame.image.load(os.path.join(IMAGE_PATH, "pause.png"))
    GAMEOVER_IMAGES = pygame.image.load(os.path.join(IMAGE_PATH, "game-over.png"))
    WIDTH, HEIGHT = resolutions[0][0], resolutions[0][1] - 50
    FONT = pygame.font.SysFont("Verdana", 25)
    COLOR_WHITE = (255, 255, 255)
    COLOR_BLACK = (0, 0, 0)
    COLOR_BLUE = (0, 0, 255)
    COLOR_YELLOW = (255, 255, 0)
    FPS = pygame.time.Clock()
    main_display = pygame.display.set_mode((WIDTH, HEIGHT))


load_resources()


def load_images():
    global bg_original, bg_aspect_ratio, bg_height, bg_width, bg, bg_X1, bg_X2, bg_move, original_player_size, original_aspect_ratio, player, player_size, player_rect, player_move_down, player_move_up, player_move_right, player_move_left, original_boom_size, boom_size, boom, original_pause_size, original_aspect_ratio, pause_size, pause, original_gameover_size, original_aspect_ratio, gameover_size, gameover
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
    player_rect = pygame.Rect(0, (HEIGHT / 2.5), *player_size)
    player_move_down = [0, 4]
    player_move_up = [0, -4]
    player_move_right = [4, 0]
    player_move_left = [-4, 0]

    original_boom_size = BOOM_IMAGES.get_size()
    original_aspect_ratio = original_boom_size[0] / original_boom_size[1]
    boom_size = (int(WIDTH / 5), int(WIDTH / 5 / original_aspect_ratio))
    boom = pygame.transform.scale(
        pygame.image.load(os.path.join(IMAGE_PATH, "boom1.png")), boom_size
    )

    original_pause_size = PAUSE_IMAGES.get_size()
    original_aspect_ratio = original_pause_size[0] / original_pause_size[1]
    pause_size = (int(WIDTH / 1), int(WIDTH / 1 / original_aspect_ratio))
    pause = pygame.transform.scale(
        pygame.image.load(os.path.join(IMAGE_PATH, "pause.png")), pause_size
    )

    original_gameover_size = GAMEOVER_IMAGES.get_size()
    original_aspect_ratio = original_gameover_size[0] / original_gameover_size[1]
    gameover_size = (int(WIDTH / 1), int(WIDTH / 1 / original_aspect_ratio))
    gameover = pygame.transform.scale(
        pygame.image.load(os.path.join(IMAGE_PATH, "game-over.png")), gameover_size
    )


load_images()


def load_events():
    global CREATE_ENEMY, CREATE_BONUS, CHANGE_IMAGE
    CREATE_ENEMY = pygame.USEREVENT + 1
    pygame.time.set_timer(CREATE_ENEMY, 3000)

    CREATE_BONUS = pygame.USEREVENT + 2
    pygame.time.set_timer(CREATE_BONUS, 3000)

    CHANGE_IMAGE = pygame.USEREVENT + 3
    pygame.time.set_timer(CHANGE_IMAGE, 200)


load_events()

score = 0
image_index = 0
enemy_rotation_speed = 0.7
enemies = []
bonuses = []
counter = 0


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


def load_score_surface():
    global score_surface, score_rect
    score_surface = create_score()[0]
    score_rect = create_score()[1]


load_score_surface()

playing = True
paused = False
space_pressed = False
bg_paused = False
pause_displayed = False
main_display_drawn = False


def handle_quit_event():
    pass


def handle_enemy_bonus_events():
    global playing, paused, space_pressed, score, player_rect, enemies, bonuses
    for event in pygame.event.get():
        if event.type == QUIT:
            playing = False
        elif event.type == CREATE_ENEMY and not paused:
            enemies.append(create_enemy())
        elif event.type == CREATE_BONUS and not paused:
            bonuses.append(create_bonus())
        elif event.type == CHANGE_IMAGE:
            # image_index += 1
            # if image_index >= len(PLAYER_IMAGES):
            #     image_index = 0
            pass
        elif event.type == pygame.KEYUP and event.key == pygame.K_SPACE:
            space_pressed = False


def handle_background():
    global bg_X1, bg_X2, bg_paused, playing, player_rect, enemies, enemy_rotation_speed, bonuses, pause_displayed, counter

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

    else:
        if not pause_displayed:
            pause_width, pause_height = pause.get_size()
            pause_x = (WIDTH - pause_width) // 2
            pause_y = (HEIGHT - pause_height) // 2
            main_display.blit(pause, (pause_x, pause_y))
            pause_displayed = True


def handle_unpause():
    global paused, space_pressed, player_rect, bg_paused, playing, pause_displayed, main_display_drawn

    keys = pygame.key.get_pressed()

    if keys[pygame.K_SPACE] and not space_pressed:
        space_pressed = True
        paused = not paused
        bg_paused = paused
        pause_displayed = False
        main_display_drawn = False

    if not paused:
        if keys[K_DOWN] and player_rect.bottom < HEIGHT:
            player_rect = player_rect.move(player_move_down)

        if keys[K_UP] and player_rect.top > 0:
            player_rect = player_rect.move(player_move_up)

        if keys[K_RIGHT] and player_rect.right < WIDTH:
            player_rect = player_rect.move(player_move_right)

        if keys[K_LEFT] and player_rect.left > 0:
            player_rect = player_rect.move(player_move_left)


def handle_main_display():
    global main_display_drawn, counter
    if not paused or (paused and not main_display_drawn):
        main_display.blit(score_surface, score_rect)
        counter += 1
        print("SHOW PAUSE", counter)
        main_display.blit(FONT.render(str(score), True, COLOR_WHITE), (WIDTH - 50, 20))
        main_display.blit(player, player_rect)
        pygame.display.flip()
        main_display_drawn = True


def handle_update():
    global playing, player_rect, enemies, bonuses, score, gameover
    for enemy in enemies:
        if enemy[1].left < 0:
            enemies.pop(enemies.index(enemy))

    for bonus in bonuses:
        if bonus[1].bottom > HEIGHT:
            bonuses.pop(bonuses.index(bonus))
        elif player_rect.colliderect(bonus[1]):
            score += 1
            bonuses.pop(bonuses.index(bonus))

    for enemy in enemies:
        if player_rect.colliderect(enemy[1]):
            original_enemy_width, original_enemy_height = enemy[4]
            current_enemy_width, current_enemy_height = enemy[1].width, enemy[1].height

            width_scale = current_enemy_width / original_enemy_width
            height_scale = current_enemy_height / original_enemy_height

            offset_x = int(130 * width_scale)
            offset_y = int(130 * height_scale)

            collision_x = max(enemy[1].left, enemy[1].left) - offset_x
            collision_y = max(enemy[1].top, enemy[1].top) - offset_y

            main_display.blit(boom, (collision_x, collision_y))
            pygame.display.flip()
            pygame.time.delay(1000)

            gameover_width, gameover_height = gameover.get_size()
            gameover_x = (WIDTH - gameover_width) // 2
            gameover_y = (HEIGHT - gameover_height) // 2

            main_display.blit(gameover, (gameover_x, gameover_y))
            pygame.display.flip()
            pygame.time.delay(5000)

    pygame.display.flip()


def main_game_loop():
    global playing, paused, space_pressed, score, player_rect, enemies, bonuses, freeze_timer

    while playing:
        FPS.tick(120)
        handle_quit_event()
        handle_enemy_bonus_events()
        handle_background()
        handle_unpause()
        handle_main_display()
        handle_update()

    pygame.quit()


main_game_loop()
