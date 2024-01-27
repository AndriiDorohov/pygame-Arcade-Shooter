import pygame
from pygame.constants import QUIT, K_DOWN, K_UP, K_LEFT, K_RIGHT
import random
import os
from screeninfo import get_monitors


pygame.init()
IMAGE_PATH = "img"

FPS = pygame.time.Clock()


class Player(pygame.sprite.Sprite):
    def __init__(self, images_path, game):
        super().__init__()
        self.game = game
        self.images_path = images_path
        self.image = pygame.image.load(os.path.join(self.images_path, "player1.png"))
        self.original_size = self.image.get_size()
        self.original_aspect_ratio = self.original_size[0] / self.original_size[1]
        self.size = (
            int(self.game.WIDTH / 10),
            int(self.game.WIDTH / 10 / self.original_aspect_ratio),
        )
        self.image = pygame.transform.scale(self.image, self.size)
        self.rect = pygame.Rect(0, (self.game.HEIGHT / 2.5), *self.size)
        self.move_down = [0, 4]
        self.move_up = [0, -4]
        self.move_right = [4, 0]
        self.move_left = [-4, 0]

    def change_image(self):
        self.image_index = (self.image_index + 1) % len(self.images)
        self.image = pygame.image.load(
            os.path.join(self.images_path, self.images[self.image_index])
        )


class Enemy(pygame.sprite.Sprite):
    def __init__(self, images_path, game):
        super().__init__()
        self.game = game
        self.images_path = images_path
        self.image = pygame.image.load(os.path.join(self.images_path, "enemy3.png"))
        self.original_size = self.image.get_size()
        self.original_aspect_ratio = self.original_size[0] / self.original_size[1]
        self.size = (
            int(self.game.WIDTH / 14),
            int(self.game.WIDTH / 14 / self.original_aspect_ratio),
        )
        self.image_original = pygame.transform.scale(self.image, self.size)
        self.angle = 0
        self.angle_speed = 2
        self.image = pygame.transform.rotate(self.image_original, self.angle)
        self.rect = self.image.get_rect(
            topleft=(
                self.game.WIDTH,
                random.randint(0, self.game.HEIGHT - self.size[1]),
            )
        )
        self.move = [random.randint(-5, -1), 0]
        self.exploded = False

    def update(self):
        if not self.exploded:
            self.rect = self.rect.move(self.move)
            self.angle = (self.angle + self.angle_speed) % 360
            self.image = pygame.transform.rotate(self.image_original, self.angle)
            self.rect = self.image.get_rect(center=self.rect.center)
        return self.rect.right > 0

    def explode(self):
        self.exploded = True


class Bonus(pygame.sprite.Sprite):
    def __init__(self, images_path, game):
        super().__init__()
        self.game = game

        self.images_path = images_path
        self.image = pygame.image.load(os.path.join(self.images_path, "bonus13.png"))

        self.original_size = self.image.get_size()
        self.original_aspect_ratio = self.original_size[0] / self.original_size[1]
        self.size = (
            int(self.game.WIDTH / 30),
            int(self.game.WIDTH / 30 / self.original_aspect_ratio),
        )
        self.image = pygame.transform.scale(self.image, self.size)
        self.rect = self.image.get_rect(
            topleft=(random.randint(0, self.game.WIDTH - self.size[0]), -self.size[1])
        )
        self.move = [0, random.randint(1, 4)]

    def update(self):
        self.rect = self.rect.move(self.move)
        return self.rect.bottom < self.game.HEIGHT


class Game:
    def __init__(self):
        self.FONT = pygame.font.SysFont("Verdana", 25)
        self.COLOR_WHITE = (255, 255, 255)
        self.COLOR_BLACK = (0, 0, 0)
        self.COLOR_BLUE = (0, 0, 255)
        self.COLOR_YELLOW = (255, 255, 0)

        self.resolutions = self.get_screen_resolution()
        self.WIDTH = self.resolutions[0][0]
        self.HEIGHT = self.resolutions[0][1] - 50
        self.main_display = pygame.display.set_mode((self.WIDTH, self.HEIGHT))

        self.bg_original = pygame.image.load(os.path.join(IMAGE_PATH, "background.jpg"))
        self.bg_aspect_ratio = (
            self.bg_original.get_width() / self.bg_original.get_height()
        )
        self.bg_height = int(self.HEIGHT)
        self.bg_width = int(self.bg_height * self.bg_aspect_ratio)
        self.bg = pygame.transform.scale(
            self.bg_original, (self.bg_width, self.bg_height)
        )
        self.bg_X1 = 0
        self.bg_X2 = self.bg.get_width()
        self.bg_move = 1.2

        self.player = Player(IMAGE_PATH, self)
        self.all_sprites = pygame.sprite.Group()
        self.enemies = pygame.sprite.Group()
        self.bonuses = pygame.sprite.Group()
        self.score = 0
        self.enemy_rotation_speed = 0

        self.BOOM_IMAGES = pygame.image.load(os.path.join(IMAGE_PATH, "boom1.png"))
        original_boom_size = self.BOOM_IMAGES.get_size()
        original_aspect_ratio = original_boom_size[0] / original_boom_size[1]
        boom_size = (int(self.WIDTH / 5), int(self.WIDTH / 5 / original_aspect_ratio))
        self.boom = pygame.transform.scale(self.BOOM_IMAGES, boom_size)

        self.game_over = False
        self.game_over_start_time = None
        self.GAME_OVER_DURATION = 50000
        self.game_state = "playing"

        self.CREATE_ENEMY = pygame.USEREVENT + 1
        pygame.time.set_timer(self.CREATE_ENEMY, 3000)

        self.CREATE_BONUS = pygame.USEREVENT + 2
        pygame.time.set_timer(self.CREATE_BONUS, 5000)

        self.CHANGE_IMAGE = pygame.USEREVENT + 3
        pygame.time.set_timer(self.CHANGE_IMAGE, 200)

        self.score_surface, self.score_rect = self.create_score()
        self.load_score_surface()

        self.playing = True

    def get_screen_resolution(self):
        monitors = get_monitors()
        resolutions = [(monitor.width, monitor.height) for monitor in monitors]
        return resolutions

    def create_enemy(self):
        enemy = Enemy(IMAGE_PATH, self)
        self.all_sprites.add(enemy)
        self.enemies.add(enemy)

    def create_bonus(self):
        bonus = Bonus(IMAGE_PATH, self)
        self.all_sprites.add(bonus)
        self.bonuses.add(bonus)

    def create_score(self):
        score_image = pygame.image.load(
            os.path.join(IMAGE_PATH, "score2.png")
        ).convert_alpha()
        original_score_size = score_image.get_size()
        original_aspect_ratio = original_score_size[0] / original_score_size[1]
        score_size = (
            int(self.WIDTH / 20),
            int(self.WIDTH / 20 / original_aspect_ratio),
        )
        score = pygame.transform.scale(score_image, score_size)
        score_rect = pygame.Rect(
            self.WIDTH - score_size[0] * 2.2, score_size[1] / 2, *score_size
        )
        return score, score_rect

    def load_score_surface(self):
        global score_surface, score_rect
        score_surface, score_rect = self.create_score()

    def handle_events(self, event):
        if event.type == QUIT:
            self.playing = False
        elif event.type == self.CREATE_ENEMY:
            self.create_enemy()
        elif event.type == self.CREATE_BONUS:
            self.create_bonus()
        elif event.type == self.CHANGE_IMAGE:
            # self.player.change_image()
            pass
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.playing = False

    def update_game_state(self, keys):
        self.bg_X1 -= self.bg_move
        self.bg_X2 -= self.bg_move

        if self.bg_X1 < -self.bg.get_width():
            self.bg_X1 = self.bg.get_width()

        if self.bg_X2 < -self.bg.get_width():
            self.bg_X2 = self.bg.get_width()

        if keys[K_DOWN] and self.player.rect.bottom < (
            self.HEIGHT - self.player.size[1]
        ):
            self.player.rect = self.player.rect.move(self.player.move_down)
        if keys[K_UP] and self.player.rect.top > 0:
            self.player.rect = self.player.rect.move(self.player.move_up)
        if keys[K_RIGHT] and self.player.rect.right < self.WIDTH:
            self.player.rect = self.player.rect.move(self.player.move_right)
        if keys[K_LEFT] and self.player.rect.left > 0:
            self.player.rect = self.player.rect.move(self.player.move_left)

        collisions_enemies = pygame.sprite.spritecollide(
            self.player, self.enemies, False
        )

        if collisions_enemies:
            for enemy in collisions_enemies:
                collision_x = (enemy.rect.left + self.player.rect.left) // 2
                collision_y = (enemy.rect.top + self.player.rect.top) // 2

                boom_sprite = pygame.sprite.Sprite()
                boom_sprite.image = self.boom
                boom_sprite.rect = pygame.Rect(
                    collision_x,
                    collision_y,
                    boom_sprite.image.get_width(),
                    boom_sprite.image.get_height(),
                )
                self.all_sprites.add(boom_sprite)

                enemy.explode()

                self.draw_elements()
                pygame.display.flip()
                pygame.time.delay(1000)
                self.game_state = "game_over"
                self.game_over_start_time = pygame.time.get_ticks()

        for enemy in self.enemies:
            if not enemy.update():
                self.all_sprites.remove(enemy)

        for bonus in self.bonuses:
            if not bonus.update():
                self.all_sprites.remove(bonus)
                self.bonuses.remove(bonus)
            if self.player.rect.colliderect(bonus.rect):
                self.score += 1

        collisions_bonuses = pygame.sprite.spritecollide(
            self.player, self.bonuses, True
        )

        if collisions_enemies:
            self.playing = False

    def show_game_over_screen(self):
        gameover = pygame.transform.scale(
            pygame.image.load(os.path.join(IMAGE_PATH, "game-over.png")),
            (self.WIDTH, self.HEIGHT),
        )
        gameover_rect = gameover.get_rect()
        gameover_rect.topleft = (0, 0)
        self.main_display.blit(gameover, gameover_rect)

    def draw_elements(self):
        self.main_display.blit(self.bg, (self.bg_X1, 0))
        self.main_display.blit(self.bg, (self.bg_X2, 0))
        self.main_display.blit(self.score_surface, self.score_rect)
        self.main_display.blit(
            self.FONT.render(str(self.score), True, self.COLOR_WHITE),
            (self.WIDTH - 50, 20),
        )
        self.main_display.blit(self.player.image, self.player.rect)
        self.all_sprites.draw(self.main_display)

    def run(self):
        while self.playing:
            FPS.tick(120)
            for event in pygame.event.get():
                self.handle_events(event)

            keys = pygame.key.get_pressed()
            self.update_game_state(keys)
            self.draw_elements()

            if self.game_state == "game_over":
                self.show_game_over_screen()
                pygame.display.flip()
                pygame.time.delay(3000)

            pygame.display.flip()


if __name__ == "__main__":
    game = Game()
    game.run()
    pygame.quit()
