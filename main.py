import pgzrun
from pygame import Rect

WIDTH = 800
HEIGHT = 600
TITLE = "KodZombies"

game_running = False
game_over = False
music_on = True
sound_on = True
enemy_spawn_timer = 0
ENEMY_SPAWN_INTERVAL = 180


class Button:
    def __init__(self, x, y, width, height, text, action, color_normal=(100, 100, 255), color_hover=(150, 150, 255)):
        self.rect = Rect(x, y, width, height)
        self.text = text
        self.action = action
        self.color_normal = color_normal
        self.color_hover = color_hover
        self.is_hovered = False

    def draw(self):
        color = self.color_hover if self.is_hovered else self.color_normal
        screen.draw.filled_rect(self.rect, color)
        screen.draw.text(self.text, center=self.rect.center, fontsize=30, color="white")
        screen.draw.rect(self.rect, (200, 200, 200))

    def check_hover(self, pos):
        self.is_hovered = self.rect.collidepoint(pos)
        return self.is_hovered

    def on_click(self, pos):
        if self.rect.collidepoint(pos):
            return self.action
        return None


menu_buttons = [
    Button(WIDTH // 2 - 150, HEIGHT // 2 - 60, 300, 50, "START GAME", "start"),
    Button(WIDTH // 2 - 150, HEIGHT // 2 + 20, 300, 50, f"AUDIO: {'ON' if music_on else 'OFF'}", "audio"),
    Button(WIDTH // 2 - 150, HEIGHT // 2 + 100, 300, 50, "EXIT", "exit", (200, 50, 50), (220, 70, 70))
]


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
        self.facing_right = True
        self.attack_cooldown = 0
        self.attack_frames = [f"hero/hero_attack{i}" for i in range(1, 6)]
        self.walk_frames = [f"hero/walk{i}" for i in range(1, 7)]
        self.left_walk_frames = [f"hero/left_walk{i}" for i in range(1, 7)]
        self.hit_frames = [f"hero/hero_hit{i}" for i in range(1, 4)]
        self.death_frames = [f"hero/hero_dead{i}" for i in range(1, 5)]
        self.attack_started = False

    def move(self, keys):
        if not self.is_attacking and not self.is_hit and not self.is_dead:
            if keys.left:
                self.rect.x -= self.speed
                self.animation_frames = self.left_walk_frames.copy()
                self.facing_right = False
            elif keys.right:
                self.rect.x += self.speed
                self.animation_frames = self.walk_frames.copy()
                self.facing_right = True
            else:
                self.animation_frames = ["hero/hero_idle"]

            self.animation_timer = (self.animation_timer + 1) % 10
            if self.animation_timer == 0:
                self.frame_index = (self.frame_index + 1) % len(self.animation_frames)

        if self.animation_frames and 0 <= self.frame_index < len(self.animation_frames):
            self.image = self.animation_frames[self.frame_index]
        else:
            self.image = "hero/hero_idle"

    def start_attack(self):
        if not self.is_attacking and not self.is_hit and not self.is_dead and self.attack_cooldown <= 0:
            self.is_attacking = True
            self.attack_started = True
            self.attack_timer = 0
            self.frame_index = 0
            self.animation_frames = self.attack_frames.copy()
            self.image = self.animation_frames[self.frame_index]
            if sound_on:
                sounds.sword.play()

    def update_attack(self, enemies):
        if self.is_attacking:
            self.attack_timer += 1
            if self.attack_timer % 5 == 0:
                self.frame_index += 1
                if self.frame_index >= len(self.animation_frames):
                    self.is_attacking = False
                    self.attack_started = False
                    self.frame_index = 0
                    self.animation_frames = ["hero/hero_idle"]
                    self.image = self.animation_frames[self.frame_index]
                    self.attack_cooldown = 20
                else:
                    self.image = self.animation_frames[self.frame_index]

            if 2 <= self.frame_index <= 3:
                for enemy in enemies:
                    if self.rect.colliderect(enemy.rect):
                        enemy.take_damage()

        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1

    def take_hit(self):
        if not self.is_hit and not self.is_dead:
            self.is_hit = True
            self.hit_timer = 0
            self.health -= 1
            self.frame_index = 0
            self.animation_frames = self.hit_frames.copy()
            if sound_on:
                sounds.punch.play()

            if self.health <= 0:
                self.animation_frames = self.hit_frames.copy()
                self.is_hit = True

    def update_hit(self):
        if self.is_hit:
            self.hit_timer += 1
            if self.hit_timer % 10 == 0:
                self.frame_index += 1

            if self.frame_index >= len(self.animation_frames):
                if self.health <= 0:
                    self.die()
                else:
                    self.is_hit = False
                    self.frame_index = 0
                    self.animation_frames = ["hero/hero_idle"]

            if self.animation_frames and 0 <= self.frame_index < len(self.animation_frames):
                self.image = self.animation_frames[self.frame_index]

    def die(self):
        self.is_dead = True
        self.is_hit = False
        self.death_timer = 0
        self.frame_index = 0
        self.animation_frames = self.death_frames.copy()

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
        self.walk_frames = [f"enemy/enemy_walk_{i}" for i in range(1, 7)]
        self.left_walk_frames = [f"enemy/enemy_left_walk_{i}" for i in range(1, 7)]
        self.right_attack_frames = [f"enemy/enemy_attack{i}" for i in range(1, 6)]
        self.left_attack_frames = [f"enemy/enemy_left_attack{i}" for i in range(1, 6)]
        self.hit_frames = [f"enemy/enemy_hit{i}" for i in range(1, 5)]
        self.death_frames = [f"enemy/enemy_dead{i}" for i in range(1, 6)]

    def move(self, hero):
        if not self.is_dead and not self.is_attacking:
            if self.rect.x < hero.rect.x:
                self.rect.x += self.speed
                self.animation_frames = self.walk_frames.copy()
            elif self.rect.x > hero.rect.x:
                self.rect.x -= self.speed
                self.animation_frames = self.left_walk_frames.copy()

            self.animation_timer = (self.animation_timer + 1) % 15
            if self.animation_timer == 0:
                self.frame_index = (self.frame_index + 1) % len(self.animation_frames)

            if self.animation_frames and 0 <= self.frame_index < len(self.animation_frames):
                self.image = self.animation_frames[self.frame_index]

    def attack(self, hero):
        if self.rect.colliderect(hero.rect) and not self.is_dead:
            if not self.is_attacking and sound_on:
                sounds.zombie.play()

            self.is_attacking = True
            self.attack_timer += 1
            if self.rect.x < hero.rect.x:
                self.animation_frames = self.right_attack_frames.copy()
            else:
                self.animation_frames = self.left_attack_frames.copy()

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
            else:
                self.animation_frames = self.hit_frames.copy()
                self.frame_index = 0

    def die(self):
        self.is_dead = True
        self.death_timer = 0
        self.frame_index = 0
        self.animation_frames = self.death_frames.copy()

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


platform = Rect(-10, HEIGHT - 250, WIDTH, 60)


def show_menu():
    screen.clear()
    screen.blit("background/background_image", (0, 0))
    screen.draw.text("KodZombie", center=(WIDTH // 2, HEIGHT // 4), fontsize=60, color="white", shadow=(1, 1),
                     scolor="black")
    for button in menu_buttons:
        button.draw()


def on_mouse_move(pos):
    for button in menu_buttons:
        button.check_hover(pos)


def on_mouse_down(pos):
    global game_running, music_on, sound_on
    if not game_running:
        for button in menu_buttons:
            result = button.on_click(pos)
            if result == "start":
                if sound_on:
                    sounds.click.play()
                reset_game()
                return
            elif result == "audio":
                music_on = not music_on
                sound_on = not sound_on
                for btn in menu_buttons:
                    if btn.action == "audio":
                        btn.text = f"AUDIO: {'ON' if music_on else 'OFF'}"
                if music_on:
                    try:
                        music.play("theme")
                    except:
                        print("Erro ao carregar música")
                else:
                    music.stop()
                return
            elif result == "exit":
                exit()


def reset_game():
    global game_running, game_over, hero, enemies, enemy_spawn_timer
    game_running = True
    game_over = False
    hero = Hero(150, platform.y - 127, 3)
    enemies = [Enemy(300, platform.y - 127, 1.5)]
    enemy_spawn_timer = 0


def update():
    global game_running, enemy_spawn_timer
    if game_running and not game_over:
        enemy_spawn_timer += 1

        if len(enemies) < 2 and enemy_spawn_timer >= ENEMY_SPAWN_INTERVAL:
            enemies.append(Enemy(600, platform.y - 127, 1.5))
            enemy_spawn_timer = 0

        if hero.is_hit:
            hero.update_hit()
        elif hero.is_dead:
            hero.update_death()
        else:
            if keyboard.space:
                hero.start_attack()
            hero.move(keyboard)
            hero.update_attack(enemies)

        for enemy in enemies:
            enemy.move(hero)
            enemy.attack(hero)
            enemy.update_death()


def on_key_down(key):
    if key == keys.RETURN and game_over:
        reset_game()
    elif key == keys.SPACE and not hero.is_attacking and not hero.is_hit and not hero.is_dead:
        hero.start_attack()


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


pgzrun.go()