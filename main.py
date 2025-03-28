import pgzrun
import random
from pygame import Rect

# Configurações gerais
WIDTH = 800
HEIGHT = 600
TITLE = "Platformer Game"

# Estado do jogo
game_running = False

# Classe para o Herói
class Hero:
    def __init__(self, x, y, speed):
        self.rect = Rect(x, y, 40, 40)
        self.image = "hero_idle"
        self.speed = speed
        self.frame_index = 0
        self.animation_frames = ["hero_idle"]
        self.animation_timer = 0
        self.is_attacking = False
        self.attack_timer = 0
        self.is_hit = False
        self.hit_timer = 0

    def move(self, keys):
        if not self.is_attacking and not self.is_hit:  # Movimento permitido apenas se não estiver atacando ou sendo atingido
            if keys.left:
                self.rect.x -= self.speed
                self.animation_frames = ["left_walk1", "left_walk2", "left_walk3", "left_walk4", "left_walk5", "left_walk6"]
            elif keys.right:
                self.rect.x += self.speed
                self.animation_frames = ["walk1", "walk2", "walk3", "walk4", "walk5", "walk6"]
            else:
                self.animation_frames = ["hero_idle"]

            self.animation_timer = (self.animation_timer + 1) % 10
            if self.animation_timer == 0:
                self.frame_index = (self.frame_index + 1) % len(self.animation_frames)

        if self.animation_frames and 0 <= self.frame_index < len(self.animation_frames):
            self.image = self.animation_frames[self.frame_index]
        else:
            self.image = "hero_idle"

    def attack(self, enemies):
        if not self.is_attacking:
            self.is_attacking = True
            self.attack_timer = 0
            self.frame_index = 0
            self.animation_frames = ["hero_attack1", "hero_attack2", "hero_attack3", "hero_attack4", "hero_attack5"]

        self.attack_timer += 1
        if self.attack_timer % 7 == 0:
            self.frame_index += 1

        if self.frame_index >= len(self.animation_frames):
            self.is_attacking = False
            self.frame_index = 0
            self.animation_frames = ["hero_idle"]

        if self.animation_frames and 0 <= self.frame_index < len(self.animation_frames):
            self.image = self.animation_frames[self.frame_index]

        for enemy in enemies:
            if self.rect.colliderect(enemy.rect):
                enemy.take_damage()

    def take_damage(self):
        if not self.is_hit:  # Evita que o herói entre no estado de "hit" mais de uma vez ao mesmo tempo
            self.is_hit = True
            self.hit_timer = 0
            self.frame_index = 0
            self.animation_frames = ["hero_hit1", "hero_hit2", "hero_hit3"]

    def update_hit(self):
        if self.is_hit:
            self.hit_timer += 1
            if self.hit_timer % 10 == 0:  # Controle da velocidade da animação de "hit"
                self.frame_index += 1

            if self.frame_index >= len(self.animation_frames):  # Finaliza o estado de "hit"
                self.is_hit = False
                self.frame_index = 0
                self.animation_frames = ["hero_idle"]

            if self.animation_frames and 0 <= self.frame_index < len(self.animation_frames):
                self.image = self.animation_frames[self.frame_index]

    def draw(self):
        screen.blit(self.image, (self.rect.x, self.rect.y))


# Classe para os Inimigos
class Enemy:
    def __init__(self, x, y, speed):
        self.rect = Rect(x, y, 40, 40)
        self.image = "enemy_idle"
        self.speed = speed
        self.animation_frames = ["enemy_walk_1", "enemy_walk_2", "enemy_walk_3", "enemy_walk_4",
                                 "enemy_walk_5", "enemy_walk_6"]
        self.frame_index = 0
        self.animation_timer = 0
        self.is_hit = False
        self.is_dead = False
        self.hit_timer = 0
        self.death_timer = 0
        self.hit_count = 0

    def move(self):
        if not self.is_hit and not self.is_dead:
            self.rect.x += self.speed

            if self.speed > 0:
                self.animation_frames = ["enemy_walk_1", "enemy_walk_2", "enemy_walk_3", "enemy_walk_4",
                                         "enemy_walk_5", "enemy_walk_6"]
            else:
                self.animation_frames = ["enemy_left_walk_1", "enemy_left_walk_2", "enemy_left_walk_3", "enemy_left_walk_4",
                                         "enemy_left_walk_5", "enemy_left_walk_6"]

            if self.rect.x < 0 or self.rect.x > WIDTH - self.rect.width:
                self.speed = -self.speed

            self.animation_timer = (self.animation_timer + 1) % 15
            if self.animation_timer == 0:
                self.frame_index = (self.frame_index + 1) % len(self.animation_frames)

            if self.animation_frames and 0 <= self.frame_index < len(self.animation_frames):
                self.image = self.animation_frames[self.frame_index]

    def take_damage(self):
        if not self.is_dead:
            self.hit_count += 1
            if self.hit_count >= 2:
                self.die()
            else:
                self.is_hit = True
                self.hit_timer = 0
                self.animation_frames = ["enemy_hit1", "enemy_hit2", "enemy_hit3", "enemy_hit4"]

    def die(self):
        self.is_dead = True
        self.death_timer = 0
        self.frame_index = 0
        self.animation_frames = ["enemy_dead1", "enemy_dead2", "enemy_dead3", "enemy_dead4", "enemy_dead5"]

    def draw(self):
        screen.blit(self.image, (self.rect.x, self.rect.y))


# Função para exibir o menu principal
def show_menu():
    screen.clear()
    screen.blit("background_image", (0, 0))
    screen.draw.text("Platformer Game", center=(WIDTH // 2, HEIGHT // 2 - 50), fontsize=40, color="white")
    screen.draw.text("Press ENTER to Start", center=(WIDTH // 2, HEIGHT // 2), fontsize=30, color="yellow")
    screen.draw.text("Press Q to Quit", center=(WIDTH // 2, HEIGHT // 2 + 50), fontsize=30, color="red")


# Adicionando a plataforma
platform = Rect(-10, HEIGHT - 250, WIDTH, 60)

# Inicializações
hero = Hero(150, platform.y - 127, 3)
enemies = [
    Enemy(300, platform.y - 127, 1),
    Enemy(600, platform.y - 127, -1)
]


# Lógica de atualização
def update():
    global game_running
    if game_running:
        if keyboard.space or hero.is_attacking:
            hero.attack(enemies)
        else:
            hero.move(keyboard)

        for enemy in enemies:
            enemy.move()

        hero.update_hit()


# Lógica de desenho
def draw():
    global game_running
    if not game_running:
        show_menu()
    else:
        screen.clear()
        screen.blit("background_image", (0, 0))
        for x in range(0, WIDTH, 156):
            screen.blit("platform_image", (x, platform.y))
        hero.draw()
        for enemy in enemies:
            enemy.draw()


# Controle de entrada no teclado
def on_key_down(key):
    global game_running
    if key == keys.RETURN:
        game_running = True
    elif key == keys.Q:
        exit()


pgzrun.go()
