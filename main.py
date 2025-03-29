import pgzrun
from pygame import Rect

# Configurações gerais
WIDTH = 800
HEIGHT = 600
TITLE = "Platformer Game"

# Estado do jogo
game_running = False
game_over = False

# Classe para o Herói
class Hero:
    def __init__(self, x, y, speed):
        self.rect = Rect(x, y, 40, 40)
        self.image = "hero/hero_idle"
        self.speed = speed
        self.frame_index = 0
        self.animation_frames = ["hero/hero_idle"]
        self.animation_timer = 0
        self.is_attacking = False
        self.attack_timer = 0
        self.is_hit = False
        self.hit_timer = 0
        self.health = 3
        self.is_dead = False
        self.death_timer = 0

    def move(self, keys):
        if not self.is_attacking and not self.is_hit and not self.is_dead:
            if keys.left:
                self.rect.x -= self.speed
                self.animation_frames = ["hero/left_walk1", "hero/left_walk2", "hero/left_walk3"]
            elif keys.right:
                self.rect.x += self.speed
                self.animation_frames = ["hero/walk1", "hero/walk2", "hero/walk3"]
            else:
                self.animation_frames = ["hero/hero_idle"]

            self.animation_timer = (self.animation_timer + 1) % 10
            if self.animation_timer == 0:
                self.frame_index = (self.frame_index + 1) % len(self.animation_frames)

        if self.animation_frames and 0 <= self.frame_index < len(self.animation_frames):
            self.image = self.animation_frames[self.frame_index]
        else:
            self.image = "hero/hero_idle"

    def attack(self, enemies):
        if not self.is_attacking:
            self.is_attacking = True
            self.attack_timer = 0
            self.frame_index = 0
            self.animation_frames = ["hero/hero_attack1", "hero/hero_attack2", "hero/hero_attack3"]

        self.attack_timer += 1
        if self.attack_timer % 7 == 0:
            self.frame_index += 1

        if self.frame_index >= len(self.animation_frames):
            self.is_attacking = False
            self.frame_index = 0
            self.animation_frames = ["hero/hero_idle"]

        for enemy in enemies:
            if self.rect.colliderect(enemy.rect):
                enemy.take_damage()

    def take_hit(self):
        if not self.is_hit and not self.is_dead:
            self.is_hit = True
            self.hit_timer = 0
            self.health -= 1
            self.frame_index = 0
            self.animation_frames = ["hero/hero_hit1", "hero/hero_hit2", "hero/hero_hit3"]

            if self.health <= 0:
                self.die()

    def die(self):
        self.is_dead = True
        self.death_timer = 0
        self.frame_index = 0
        self.animation_frames = ["hero/hero_dead1", "hero/hero_dead2", "hero/hero_dead3", "hero/hero_dead4"]

    def update_death(self):
        global game_over
        if self.is_dead:
            self.death_timer += 1
            if self.death_timer % 10 == 0:
                self.frame_index += 1

            if self.frame_index >= len(self.animation_frames):
                game_over = True

            if self.animation_frames and 0 <= self.frame_index < len(self.animation_frames):
                self.image = self.animation_frames[self.frame_index]

    def draw(self):
        screen.blit(self.image, (self.rect.x, self.rect.y))


# Classe para os Inimigos
class Enemy:
    def __init__(self, x, y, speed):
        self.rect = Rect(x, y, 40, 40)
        self.image = "enemy/enemy_idle"
        self.speed = speed
        self.frame_index = 0
        self.animation_timer = 0
        self.is_dead = False
        self.death_timer = 0
        self.hit_count = 0
        self.is_attacking = False
        self.attack_timer = 0

    def move(self, hero):
        if not self.is_dead and not self.is_attacking:
            if self.rect.x < hero.rect.x:
                self.rect.x += self.speed
                self.image = "enemy/enemy_walk_1"
                self.animation_frames = ["enemy/enemy_walk_1", "enemy/enemy_walk_2", "enemy/enemy_walk_3"]
            elif self.rect.x > hero.rect.x:
                self.rect.x -= self.speed
                self.image = "enemy/enemy_left_walk_1"
                self.animation_frames = ["enemy/enemy_left_walk_1", "enemy/enemy_left_walk_2", "enemy/enemy_left_walk_3"]

            self.animation_timer = (self.animation_timer + 1) % 15
            if self.animation_timer == 0:
                self.frame_index = (self.frame_index + 1) % len(self.animation_frames)

            if self.animation_frames and 0 <= self.frame_index < len(self.animation_frames):
                self.image = self.animation_frames[self.frame_index]

    def attack(self, hero):
        if self.rect.colliderect(hero.rect) and not self.is_dead:
            self.is_attacking = True
            self.attack_timer += 1
            if self.rect.x < hero.rect.x:
                self.animation_frames = ["enemy/enemy_attack1", "enemy/enemy_attack2", "enemy/enemy_attack3", "enemy/enemy_attack4", "enemy/enemy_attack5"]
            else:
                self.animation_frames = ["enemy/enemy_left_attack1", "enemy/enemy_left_attack2", "enemy/enemy_left_attack3", "enemy/enemy_left_attack4", "enemy/enemy_left_attack5"]

            if self.attack_timer % 10 == 0:
                self.frame_index += 1

            if self.frame_index >= len(self.animation_frames):
                self.frame_index = 0
                hero.take_hit()

            if self.animation_frames and 0 <= self.frame_index < len(self.animation_frames):
                self.image = self.animation_frames[self.frame_index]

    def take_damage(self):
        if not self.is_dead:
            self.hit_count += 1
            if self.hit_count >= 2:
                self.die()

    def die(self):
        self.is_dead = True
        self.death_timer = 0
        self.frame_index = 0
        self.animation_frames = ["enemy/enemy_dead1", "enemy/enemy_dead2", "enemy/enemy_dead3"]

    def update_death(self):
        if self.is_dead:
            self.death_timer += 1
            if self.death_timer % 10 == 0:
                self.frame_index += 1

            if self.frame_index >= len(self.animation_frames):
                self.rect.x = -1000
                self.rect.y = -1000

            if self.animation_frames and 0 <= self.frame_index < len(self.animation_frames):
                self.image = self.animation_frames[self.frame_index]

    def draw(self):
        screen.blit(self.image, (self.rect.x, self.rect.y))


def show_menu():
    screen.clear()
    screen.blit("background/background_image", (0, 0))
    screen.draw.text("Press ENTER to Start", center=(WIDTH // 2, HEIGHT // 2), fontsize=40, color="white")


def reset_game():
    global game_running, game_over, hero, enemies
    game_running = True
    game_over = False
    hero = Hero(150, platform.y - 127, 3)
    enemies = [
        Enemy(300, platform.y - 127, 1),
        Enemy(600, platform.y - 127, -1)
    ]


platform = Rect(-10, HEIGHT - 250, WIDTH, 60)
hero = Hero(150, platform.y - 127, 3)
enemies = [
    Enemy(300, platform.y - 127, 1),
    Enemy(600, platform.y - 127, -1)
]


def update():
    global game_running
    if game_running and not game_over:
        if keyboard.space or hero.is_attacking:
            hero.attack(enemies)
        else:
            hero.move(keyboard)

        for enemy in enemies:
            enemy.move(hero)
            enemy.attack(hero)
            enemy.update_death()

        hero.update_death()


def draw():
    if not game_running:
        show_menu()
    elif game_over:
        screen.clear()
        screen.blit("background/background_image", (0, 0))
        screen.draw.text("GAME OVER", center=(WIDTH // 2, HEIGHT // 2), fontsize=50, color="red")
        screen.draw.text("Press ENTER to Restart", center=(WIDTH // 2, HEIGHT // 2 + 50), fontsize=30, color="white")
    else:
        screen.clear()
        screen.blit("background/background_image", (0, 0))
        for x in range(0, WIDTH, 156):
            screen.blit("tiles/platform_image", (x, platform.y))
        hero.draw()
        for enemy in enemies:
            enemy.draw()


def on_key_down(key):
    global game_running
    if key == keys.RETURN:
        reset_game()


pgzrun.go()
