import pgzrun
import random
import math

# Configurações gerais
WIDTH = 800
HEIGHT = 600
TITLE = "Platformer Game"

# Classe para o Herói
class Hero:
    def __init__(self, x, y, speed):
        self.rect = Rect(x, y, 40, 40)
        self.image = "hero_idle"
        self.speed = speed
        self.jump_speed = -10
        self.is_jumping = False
        self.gravity = 0.5
        self.frame_index = 0
        self.animation_frames = ["hero_idle"]  # Substituir por sprites reais

    def move(self, keys):
        if keys.left:
            self.rect.x -= self.speed
            self.animation_frames = ["left_walk1", "left_walk2", "left_walk3"]
        elif keys.right:
            self.rect.x += self.speed
            self.animation_frames = ["walk1", "walk2", "walk3"]
        else:
            self.animation_frames = ["hero_idle"]

        self.frame_index = (self.frame_index + 0) % len(self.animation_frames)
        self.image = self.animation_frames[self.frame_index]

        if keys.up and not self.is_jumping:
            self.is_jumping = True
            self.rect.y += self.jump_speed

        if self.is_jumping:
            self.rect.y += self.jump_speed
            self.jump_speed += self.gravity

        if self.rect.y >= HEIGHT - 90:  # Alinhado à plataforma
            self.rect.y = HEIGHT - 90
            self.is_jumping = False
            self.jump_speed = -10

    def draw(self):
        screen.blit(self.image, (self.rect.x, self.rect.y))

# Classe para os Inimigos
class Enemy:
    def __init__(self, x, y, speed):
        self.rect = Rect(x, y, 40, 40)
        self.image = "enemy_idle"
        self.speed = speed

    def move(self):
        self.rect.x += self.speed
        if self.rect.x < 0 or self.rect.x > WIDTH - 40:
            self.speed = -self.speed

    def draw(self):
        screen.blit(self.image, (self.rect.x, self.rect.y))

# Menu principal
def show_menu():
    screen.clear()
    screen.blit("background_image", (0, 0))  # Mostra o fundo do menu
    screen.draw.text("Platformer Game", center=(WIDTH//2, HEIGHT//2 - 50), fontsize=40)
    screen.draw.text("Press SPACE to Start", center=(WIDTH//2, HEIGHT//2), fontsize=30)

# Adicionando a plataforma
platform = Rect(0, HEIGHT - 50, WIDTH, 50)

# Inicializações
hero = Hero(100, HEIGHT - 90, 5)  # Herói posicionado na plataforma
enemy = Enemy(300, HEIGHT - 90, 2)  # Inimigo posicionado na plataforma

game_running = False

# Lógica de atualização
def update():
    global game_running
    if game_running:
        hero.move(keyboard)
        enemy.move()

# Lógica de desenho
def draw():
    global game_running
    if not game_running:
        show_menu()
    else:
        screen.clear()
        screen.blit("background_image", (0, 0))  # Fundo do jogo
        screen.draw.filled_rect(platform, "green")  # Desenha a plataforma
        hero.draw()
        enemy.draw()

# Controla o início do jogo
def on_key_down(key):
    global game_running
    if not game_running and key == keys.SPACE:
        game_running = True

pgzrun.go()
