import pygame
import random
import sys
import os

# Initialize Pygame
pygame.init()

# Constants
WIDTH, HEIGHT = 1366,768
PLAYER_SIZE = 50
ENEMY_SIZE = 30
BULLET_SIZE = 5
BOSS_SIZE = 100
FPS = 60

# Colors
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)
PURPLE = (128, 0, 128)

# Screen setup
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("2D Game")

# Clock
clock = pygame.time.Clock()

# Player setup
player = pygame.Rect(WIDTH // 2, HEIGHT - PLAYER_SIZE - 10, PLAYER_SIZE, PLAYER_SIZE)
player_speed = 5

# Bullet setup
player_bullets = []
enemy_bullets = []

# Enemy setup
enemies = []
enemy_timer = 1000
enemy_event = pygame.USEREVENT + 1
pygame.time.set_timer(enemy_event, enemy_timer)

# Boss setup
boss = None
boss_health = 20
boss_stage = False

# Score
score = 0

# Game over flag
is_game_over = False

# Start menu flag
in_start_menu = True

# Fonts
font = pygame.font.SysFont(None, 36)

# Sound directory
sound_dir = r"C:\Users\omar\Downloads\python"

# Load sounds
bullet_sound = pygame.mixer.Sound(os.path.join(sound_dir, "bullet.wav"))
game_over_sound = pygame.mixer.Sound(os.path.join(sound_dir, "game_over.wav"))
enemy_hit_sound = pygame.mixer.Sound(os.path.join(sound_dir, "enemy_hit.wav"))
boss_intro_sound = pygame.mixer.Sound(os.path.join(sound_dir, "boss_intro.wav"))

# Functions
def draw_player():
    pygame.draw.rect(screen, GREEN, player)

def draw_bullets():
    for bullet in player_bullets:
        pygame.draw.rect(screen, YELLOW, bullet[0])
    for bullet in enemy_bullets:
        pygame.draw.rect(screen, RED, bullet)

def draw_enemies():
    for enemy in enemies:
        pygame.draw.rect(screen, RED, enemy)

def draw_boss():
    if boss:
        pygame.draw.rect(screen, PURPLE, boss)
        # Draw boss health bar
        health_bar_width = boss.width * (boss_health / 20)
        pygame.draw.rect(screen, RED, (boss.x, boss.y - 10, health_bar_width, 5))

def move_bullets():
    for bullet in player_bullets[:]:
        rect, dir_x, dir_y = bullet
        rect.x += dir_x
        rect.y += dir_y
        if rect.y < 0 or rect.x < 0 or rect.x > WIDTH:
            player_bullets.remove(bullet)

    for bullet in enemy_bullets[:]:
        bullet.y += 5
        if bullet.y > HEIGHT:
            enemy_bullets.remove(bullet)

def move_enemies():
    for enemy in enemies[:]:
        enemy.y += 2
        if enemy.y > HEIGHT:
            enemies.remove(enemy)

def move_boss():
    if boss:
        boss.y += 1
        if boss.y > HEIGHT:
            reset_boss()

def reset_boss():
    global boss, boss_health, boss_stage
    boss = None
    boss_health = 20
    boss_stage = False

def check_collisions():
    global is_game_over, boss_health, score

    # Check player bullet-enemy collisions
    for bullet in player_bullets[:]:
        rect = bullet[0]
        for enemy in enemies[:]:
            if rect.colliderect(enemy):
                player_bullets.remove(bullet)
                enemies.remove(enemy)
                score += 10
                enemy_hit_sound.play()

        if boss and rect.colliderect(boss):
            player_bullets.remove(bullet)
            boss_health -= 1
            boss_hit_sound.play()
            if boss_health <= 0:
                reset_boss()
                score += 100

    # Check enemy bullet-player collisions
    for bullet in enemy_bullets[:]:
        if bullet.colliderect(player):
            is_game_over = True
            game_over_sound.play()

    # Check player-enemy collisions
    for enemy in enemies:
        if player.colliderect(enemy):
            is_game_over = True
            game_over_sound.play()

    if boss and player.colliderect(boss):
        is_game_over = True
        game_over_sound.play()

def spawn_enemy():
    x_pos = random.randint(0, WIDTH - ENEMY_SIZE)
    enemies.append(pygame.Rect(x_pos, 0, ENEMY_SIZE, ENEMY_SIZE))

def enemy_fire():
    for enemy in enemies:
        bullet = pygame.Rect(enemy.x + ENEMY_SIZE // 2, enemy.y + ENEMY_SIZE, BULLET_SIZE, BULLET_SIZE)
        enemy_bullets.append(bullet)

def spawn_boss():
    global boss, boss_stage
    x_pos = random.randint(0, WIDTH - BOSS_SIZE)
    boss = pygame.Rect(x_pos, -100, BOSS_SIZE, BOSS_SIZE)
    boss_stage = True
    boss_intro_sound.play()

def draw_score():
    score_text = font.render(f"Score: {score}", True, WHITE)
    screen.blit(score_text, (10, 10))

def game_over_screen():
    game_over_text = font.render("Game Over! Press R to restart.", True, WHITE)
    screen.blit(game_over_text, (WIDTH // 2 - 150, HEIGHT // 2))

def start_menu():
    start_text = font.render("Press SPACE to start the game.", True, WHITE)
    screen.blit(start_text, (WIDTH // 2 - 200, HEIGHT // 2))

def restart_game():
    global player, player_bullets, enemy_bullets, enemies, boss, score, is_game_over, in_start_menu
    player.x, player.y = WIDTH // 2, HEIGHT - PLAYER_SIZE - 10
    player_bullets.clear()
    enemy_bullets.clear()
    enemies.clear()
    boss = None
    score = 0
    is_game_over = False
    in_start_menu = False

# Game loop
running = True
while running:
    screen.fill((0, 0, 0))
    
    if in_start_menu:
        start_menu()
    elif is_game_over:
        game_over_screen()
    else:
        draw_player()
        draw_bullets()
        draw_enemies()
        draw_boss()
        draw_score()

        move_bullets()
        move_enemies()
        move_boss()
        check_collisions()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                if in_start_menu:
                    restart_game()
                elif not is_game_over:
                    # Create a bullet going straight up
                    bullet = pygame.Rect(player.x + PLAYER_SIZE // 2 - BULLET_SIZE // 2, player.y, BULLET_SIZE, BULLET_SIZE)
                    player_bullets.append((bullet, 0, -10))
                    bullet_sound.play()
            if event.key == pygame.K_r and is_game_over:
                in_start_menu = True  # Return to start menu

        if event.type == enemy_event and not in_start_menu and not is_game_over:
            if not boss_stage and score < 500:
                spawn_enemy()
                enemy_fire()  # Make enemies fire bullets
            if score >= 500 and not boss:
                spawn_boss()

    keys = pygame.key.get_pressed()
    if not in_start_menu and not is_game_over:
        if keys[pygame.K_RIGHT]:
            player.x += player_speed
        if keys[pygame.K_LEFT]:
            player.x -= player_speed

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
sys.exit()
