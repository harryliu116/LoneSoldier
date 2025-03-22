import pygame
import math
import random

pygame.init()
clock = pygame.time.Clock()


pygame.mixer.init()


pygame.mixer.music.load("war.MP3")  
pygame.mixer.music.play(-1) 

bullet_sound = pygame.mixer.Sound("bullet.wav")
die_sound = pygame.mixer.Sound("die.wav")
explosion_sound = pygame.mixer.Sound("explosion.wav") 

# Screen dimensions
screen_width = 1280
screen_height = 720
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.mouse.set_visible(False)

# Game settings
clock = pygame.time.Clock()
spam_time = 0
spam_pos = [(0, 0), (0, 720), (1280, 720), (1280, 0)]
running = True

# Player settings
PLAYER_HEALTH = 300
phase = 0

# Colors
WHITE = (255, 255, 255)
BLUE = (50, 200, 255)
RED = (255, 20, 20)
YELLOW = (255, 255, 20)
GREEN = (0, 255, 0)
BLACK = (0, 0, 0)
ORANGE = (255, 150, 0)
DARKGREEN = (10, 100, 30)

# Size
e1_size = 70
e2_size = 300
e3_size = 500
h_size = 30

# Background
bg = pygame.image.load('field.png')
bg = pygame.transform.scale(bg, (screen_width, screen_height))

# Effects
EXPLOSION = [pygame.image.load(f"explosion/ex{i}.gif") for i in range(1, 13)]
# Font
font = pygame.font.Font(None, 36)

class TextCrawl:

    def __init__(self, surface, text, size, color, x, y):
        self.surface = surface
        self.text = text
        self.original_size = size
        self.size = size
        self.color = color
        self.x = x
        self.y = y
        self.font_name = pygame.font.match_font('impact')

    def draw(self):
        font = pygame.font.Font(self.font_name, int(self.size))
        text_surface = font.render(self.text, True, self.color)
        text_rect = text_surface.get_rect()
        text_rect.midtop = (self.x, self.y)
        self.surface.blit(text_surface, text_rect)

    def update(self):
        self.y -= 1.5  # Reduced step to make the movement smoother
        if self.size > self.original_size * 0.3:  # Prevent text from becoming too small
            self.size *= 0.98  # Gradual size reduction for smoother zoom-out effect
        if self.y < -5:
            self.kill()


text_data = [
    "STAR WARS IV.S(4.5)", "AN OLD HOPE", "Han Salad is under the attack of the empire",
    "He needs your help", "Control the Billenium Chicken", "Using W A S D to control the position",
    "Using the mouse to shoot bullets", "MAY THE FORCE BE WITH YOU." 
]

text_list = [
    TextCrawl(screen, text_data[i], 100, (255, 215, 0), screen_width / 2,
              screen_height / 2) for i in range(len(text_data))
]


def intro():
    global text_list
    timer = 0

    while timer < 240:
        screen.fill((0, 0, 0))
        screen.blit(bg, (0, 0))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()

        for i, text in enumerate(text_list):
            if timer > i * 24:
                text.draw()
                text.update()

        timer += 1
        pygame.display.update()
        clock.tick(24)

    text_list = [
        TextCrawl(screen, text_data[i], 100, (255, 215, 0), screen_width / 2,
              screen_height / 2) for i in range(len(text_data))
    ]

# Player class
class Player(pygame.sprite.Sprite):
    def __init__(self, num, color, controls):
        super().__init__()
        self.og_image = pygame.image.load("player.png")
        self.og_image = pygame.transform.scale(self.og_image, (70, 70))
        self.image = self.og_image.copy()
        self.rect = self.image.get_rect(center=(screen_width / 2, screen_height / 2))
        self.num = num
        self.bullets = pygame.sprite.Group()
        self.controls = controls
        self.last_shot = pygame.time.get_ticks()
        self.shoot_delay = 100  # milliseconds
        self.health = PLAYER_HEALTH
        self.total_health = PLAYER_HEALTH
        self.score = 0
        self.mask = pygame.mask.from_surface(self.image)

        self.aim = pygame.image.load("cro.png")
        self.aim = pygame.transform.scale(self.aim, (50, 50))
        self.aim_rect = self.aim.get_rect(center=(screen_width / 2, screen_height / 2))

    def update(self):
        keystate = pygame.key.get_pressed()

        directions = {
            "up": self.controls[0],
            "down": self.controls[1],
            "left": self.controls[2],
            "right": self.controls[3]
        }

        for direction, key in directions.items():
            if keystate[key]:
                if direction == "up" and self.rect.y > 0:
                    self.rect.y -= 6
                elif direction == "down" and self.rect.y < screen_height - 50:
                    self.rect.y += 6
                elif direction == "left" and self.rect.x > 0:
                    self.rect.x -= 6
                elif direction == "right" and self.rect.x < screen_width - 50:
                    self.rect.x += 6

        mouse_x, mouse_y = pygame.mouse.get_pos()
        self.aim_rect.center = (mouse_x, mouse_y)
        self.rotate_towards_mouse()

        if pygame.mouse.get_pressed()[0]:
            now = pygame.time.get_ticks()
            if now - self.last_shot > self.shoot_delay:
                self.last_shot = now
                direction = self.calculate_direction()
                bullet = Bullet(BLUE, self.rect.center, direction)
                self.bullets.add(bullet)
                bullet_sound.play()  # Play bullet sound effect

        self.bullets.update()

    def calculate_direction(self):
        dx = self.aim_rect.centerx - self.rect.centerx
        dy = self.aim_rect.centery - self.rect.centery
        distance = math.sqrt(dx**2 + dy**2)
        direction = (dx / distance * 20, dy / distance * 20)
        return direction

    def rotate_towards_mouse(self):
        dx = self.aim_rect.centerx - self.rect.centerx
        dy = self.aim_rect.centery - self.rect.centery
        angle = math.degrees(math.atan2(-dy, dx))

        if dx < 0:
            self.image = pygame.transform.flip(self.og_image, False, True)
            self.image = pygame.transform.rotate(self.image, angle + 90)
        else:
            self.image = pygame.transform.rotate(self.og_image, angle- 90)

        self.rect = self.image.get_rect(center=self.rect.center)


# Bullet class
class Bullet(pygame.sprite.Sprite):
    def __init__(self, color, pos, direction):
        super().__init__()
        self.image = pygame.Surface((10, 10))
        self.image.fill(color)
        self.rect = self.image.get_rect(center=pos)
        self.direction = direction
        self.mask = pygame.mask.from_surface(self.image)

    def update(self):
        self.rect.x += self.direction[0]
        self.rect.y += self.direction[1]
        if self.rect.x < 0 or self.rect.x > screen_width or self.rect.y < 0 or self.rect.y > screen_height:
            self.kill()


class Explosion(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = EXPLOSION[0]
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.step = 0
        explosion_sound.play()  # Play explosion sound effect when the explosion is created

    def draw(self):
        if self.step == 12:
            self.kill()
        else:
            self.image = EXPLOSION[self.step]
            screen.blit(self.image, self.rect.center)
            self.step += 1


# Enemy class
class Enemy(pygame.sprite.Sprite):

    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.image.load("enemy.png")
        self.image = pygame.transform.scale(self.image, (70, 70))
        self.rect = self.image.get_rect(topleft=(x, y))
        self.health = 80
        self.total_health = 80
        self.shoot_delay = 1000  # milliseconds
        self.last_shot = pygame.time.get_ticks()
        self.mask = pygame.mask.from_surface(self.image)
        self.bullets = pygame.sprite.Group()

    def update(self):
        self.rect.y += 3
        if self.rect.y > screen_height:
            self.kill()

        # Shooting logic
        now = pygame.time.get_ticks()
        if now - self.last_shot > self.shoot_delay:
            self.last_shot = now
            self.shoot()

        self.bullets.update()

    def shoot(self):
        direction = self.calculate_direction()
        bullet = Bullet(RED, self.rect.center, direction)
        self.bullets.add(bullet)
        enemy_bullets.add(bullet)

    def calculate_direction(self):
        dx = player1.rect.centerx - self.rect.centerx
        dy = player1.rect.centery - self.rect.centery
        distance = math.sqrt(dx ** 2 + dy ** 2)
        direction = (dx / distance * 10, dy / distance * 10)  # Adjust speed as needed
        return direction

    def draw(self, screen):
        pygame.draw.rect(screen, RED, (self.rect.x, self.rect.y, 70, 10))
        if self.health >= 0:
            pygame.draw.rect(screen, ORANGE,
                             (self.rect.x, self.rect.y,
                              self.health / self.total_health * 70, 10))
        self.bullets.draw(screen)


# Boss class
class Boss(pygame.sprite.Sprite):

    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.image.load("star_destroyer.png")
        self.image = pygame.transform.scale(self.image, (300, 300))
        self.rect = self.image.get_rect(topleft=(x, y))
        self.health = 200
        self.total_health = 200
        self.shoot_delay = 2000  # milliseconds
        self.last_shot = pygame.time.get_ticks()
        self.mask = pygame.mask.from_surface(self.image)
        self.bullets = pygame.sprite.Group()

    def update(self):
        self.rect.y += 2
        if self.rect.y > screen_height:
            self.kill()

        # Shooting logic
        now = pygame.time.get_ticks()
        if now - self.last_shot > self.shoot_delay:
            self.last_shot = now
            self.shoot()

        self.bullets.update()

    def shoot(self):
        direction = self.calculate_direction()
        bullet = Bullet(RED, self.rect.center, direction)
        self.bullets.add(bullet)
        enemy_bullets.add(bullet)

    def calculate_direction(self):
        dx = player1.rect.centerx - self.rect.centerx
        dy = player1.rect.centery - self.rect.centery
        distance = math.sqrt(dx ** 2 + dy ** 2)
        direction = (dx / distance * 8, dy / distance * 8)  # Adjust speed as needed
        return direction

    def draw(self, screen):
        pygame.draw.rect(screen, RED, (self.rect.x, self.rect.y, 300, 10))
        if self.health >= 0:
            pygame.draw.rect(screen, ORANGE,
                             (self.rect.x, self.rect.y,
                              self.health / self.total_health * 300, 10))
        self.bullets.draw(screen)


# Final Boss class
class Laser(pygame.sprite.Sprite):
    def __init__(self, color, pos, direction, length=500, thickness=10):
        super().__init__()
        self.color = color
        self.length = length
        self.thickness = thickness
        self.start_pos = pos
        self.end_pos = (pos[0] + direction[0] * length, pos[1] + direction[1] * length)
        self.rect = pygame.Rect(self.start_pos, (self.length, self.thickness))
        self.direction = direction

    def update(self):
        # Move the laser in its direction
        self.start_pos = (self.start_pos[0] + self.direction[0], self.start_pos[1] + self.direction[1])
        self.end_pos = (self.start_pos[0] + self.direction[0] * self.length, self.start_pos[1] + self.direction[1] * self.length)
        self.rect = pygame.Rect(self.start_pos, (self.length, self.thickness))
        if self.start_pos[0] < 0 or self.start_pos[0] > screen_width or self.start_pos[1] < 0 or self.start_pos[1] > screen_height:
            self.kill()

    def draw(self, screen):
        pygame.draw.line(screen, self.color, self.start_pos, self.end_pos, self.thickness)



class Final(pygame.sprite.Sprite):

    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.image.load("deathstar.png")
        self.image = pygame.transform.scale(self.image, (500, 500))
        self.rect = self.image.get_rect(topleft=(x, y))
        self.health = 5000
        self.total_health = 5000
        self.shoot_delay = 3000  # milliseconds for regular bullets
        self.laser_delay = 5000  # milliseconds for lasers
        self.last_shot = pygame.time.get_ticks()
        self.last_laser = pygame.time.get_ticks()
        self.mask = pygame.mask.from_surface(self.image)
        self.bullets = pygame.sprite.Group()
        self.lasers = pygame.sprite.Group()

    def update(self):
        self.rect.y += 1
        if self.rect.y >= (screen_height-300)/2:
            self.rect.y = (screen_height-300)/2

        # Shooting logic
        now = pygame.time.get_ticks()
        if now - self.last_shot > self.shoot_delay:
            self.last_shot = now
            self.shoot()

        # Laser shooting logic
        if now - self.last_laser > self.laser_delay:
            self.last_laser = now
            self.shoot_laser()

        self.bullets.update()
        self.lasers.update()

        # Check for collision between laser and player
        for laser in self.lasers:
            if pygame.sprite.collide_rect(laser, player1):  # Assuming `player1` is the player object
                player1.health -= 90  # Reduce player health by 90
                self.bullets.add(Bullet(GREEN, self.rect.center, self.calculate_direction()))  # Add a new bullet to Death Star
                laser.kill()  # Remove the laser after it hits


    def shoot(self):
        direction = self.calculate_direction()
        bullet = Bullet(RED, self.rect.center, direction)
        self.bullets.add(bullet)
        enemy_bullets.add(bullet)

    def shoot_laser(self):
        direction = self.calculate_direction()
        laser = Laser(GREEN, self.rect.center, direction)
        self.lasers.add(laser)

    def calculate_direction(self):
        dx = player1.rect.centerx - self.rect.centerx
        dy = player1.rect.centery - self.rect.centery
        distance = math.sqrt(dx ** 2 + dy ** 2)
        direction = (dx / distance, dy / distance)
        return direction

    def draw(self, screen):
        pygame.draw.rect(screen, RED, (self.rect.x, self.rect.y, 500, 10))
        if self.health >= 0:
            pygame.draw.rect(screen, ORANGE,
                             (self.rect.x, self.rect.y,
                              self.health / self.total_health * 500, 10))
        self.bullets.draw(screen)
        for laser in self.lasers:
            laser.draw(screen)



class Text():

    def __init__(self, surface, text, size, color, x, y):
        font_name = pygame.font.match_font('Impact')
        self.surface = surface
        self.text = text
        self.size = size
        self.font = pygame.font.Font(font_name, self.size)
        self.color = color
        self.x = x
        self.y = y

    def draw(self):
        text_surface = self.font.render(self.text, True, self.color)
        text_rect = text_surface.get_rect()
        text_rect.midtop = (self.x, self.y)
        self.surface.blit(text_surface, text_rect)


class Button:
    def __init__(self, surface, text, size, color1, color2, x, y, w=370, h=80):
        self.surface = surface
        self.text = text
        self.size = size
        self.font = pygame.font.SysFont("Berlin Sans FB", size)
        self.color1 = color1
        self.color2 = color2
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.rect = pygame.Rect(x, y, w, h)
        self.clicked = False

    def draw(self):
        pos = pygame.mouse.get_pos()
        color = self.color2 if self.rect.collidepoint(pos) and self.clicked else self.color1
        pygame.draw.rect(self.surface, color, self.rect)
        text_surface = self.font.render(self.text, True, WHITE)
        text_rect = text_surface.get_rect(center=(self.x + self.w // 2, self.y + self.h // 2))
        self.surface.blit(text_surface, text_rect)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.clicked = True
                return 1
        elif event.type == pygame.MOUSEBUTTONUP:
            if self.rect.collidepoint(event.pos):
                self.clicked = False
                return 2
        return 0


def Player_UI():
    global phase
    LEFT = 140

    health_text = font.render(f"Health:", True, WHITE)
    screen.blit(health_text, (LEFT, 30))

    pygame.draw.rect(screen, RED, (LEFT, 60, 300, 10))

    if player1.health >= 0:
        pygame.draw.rect(
            screen, GREEN,
            (LEFT, 60, player1.health / player1.total_health * 300, 10))

    score_text = font.render(f"Score: {player1.score}", True, WHITE)
    screen.blit(score_text, (LEFT, 80))

    phase_text = font.render(f"Phase {phase}", True, WHITE)
    screen.blit(phase_text, (LEFT, screen_height - 70))


def deathwords():
    font_size = 100
    deathwords = Text(screen, "YOU DIED!!!", font_size, (255, 0, 0), 600, 250)
    button1 = Button(screen, "New Game", 30, GREEN, DARKGREEN, 400, 400)
    button2 = Button(screen, "Exit", 30, ORANGE, RED, 400, 500)
    dead = True
    pygame.mouse.set_visible(True)

    while dead:
        screen.fill((0, 0, 0))
        deathwords.draw()
        button1.draw()
        button2.draw()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            choice1 = button1.handle_event(event)
            choice2 = button2.handle_event(event)
            if choice1 == 2:
                dead = False
            elif choice2 == 2:
                pygame.quit()
                exit()

        pygame.display.update()
        clock.tick(60)
    if not dead:
        print("Not dead")
        main()

def start():
    font_size = 100
    deathwords = Text(screen, "WarZone", font_size, (255, 255, 20), 600, 250)
    button1 = Button(screen, "New Game", 30, GREEN, DARKGREEN, 400, 400)
    button2 = Button(screen, "Exit", 30, ORANGE, RED, 400, 500)
    dead = True
    pygame.mouse.set_visible(True)

    while dead:
        screen.fill((0, 0, 0))
        deathwords.draw()
        button1.draw()
        button2.draw()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            choice1 = button1.handle_event(event)
            choice2 = button2.handle_event(event)
            if choice1 == 2:
                dead = False
            elif choice2 == 2:
                pygame.quit()
                exit()

        pygame.display.update()
        clock.tick(60)
    if not dead:
        print("Not dead")
        main()

def win():
    font_size = 100
    deathwords = Text(screen, "YOU WON!!!", font_size, (255, 255, 20), 600, 250)
    button1 = Button(screen, "New Game", 30, GREEN, DARKGREEN, 400, 400)
    button2 = Button(screen, "Exit", 30, ORANGE, RED, 400, 500)
    dead = True
    pygame.mouse.set_visible(True)

    while dead:
        screen.fill((0, 0, 0))
        deathwords.draw()
        button1.draw()
        button2.draw()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            choice1 = button1.handle_event(event)
            choice2 = button2.handle_event(event)
            if choice1 == 2:
                dead = False
            elif choice2 == 2:
                pygame.quit()
                exit()

        pygame.display.update()
        clock.tick(60)
    if not dead:
        print("Not dead")
        main()


# Initialize player and enemies
player1 = Player(1, GREEN, [pygame.K_w, pygame.K_s, pygame.K_a, pygame.K_d])
player_group = pygame.sprite.Group(player1)
enemy_group = pygame.sprite.Group()
enemy_bullets = pygame.sprite.Group()

explosion_group = pygame.sprite.Group()


# Main game loop
def main():
    global clock, spam_time, spam_pos, running, phase
    pygame.mouse.set_visible(False)
    running = True
    final_boss_spawned = False
    phase = 1
    #intro()


    while running:
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        if player1.score < 150:
            phase = 1  # Phase 1: Tie Fighters only
        elif 150 <= player1.score < 300:
            phase = 2  # Phase 2: Tie Fighters and Star Destroyer
        else:
            phase = 3  # Phase 3: Death Star only

        if phase == 1:
            if spam_time % 35 == 0: 
                x = random.randint(0, screen_width - e1_size)
                y = -e1_size
                enemy = Enemy(x, y)
                enemy_group.add(enemy)

        elif phase == 2:
            if spam_time % 50 == 0: 
                x = random.randint(0, screen_width - e1_size)
                y = -e1_size
                enemy = Enemy(x, y)
                enemy_group.add(enemy)
            if spam_time % 400 == 0: 
                x = random.randint(0, screen_width - e2_size)
                y = -e2_size
                boss = Boss(x, y)
                enemy_group.add(boss)

        elif phase == 3 and not final_boss_spawned:
            x = random.randint(0, screen_width - e3_size)
            y = -e3_size
            final_boss = Final(x, y)
            enemy_group.add(final_boss)
            final_boss_spawned = True

        # Update sprites
        player_group.update()
        enemy_group.update()
        enemy_bullets.update()

        # Collision detection
        for player in player_group:
            for bullet in player.bullets:
                enemies_hit = pygame.sprite.spritecollide(
                    bullet, enemy_group, False, pygame.sprite.collide_mask)
                for e in enemies_hit:
                    bullet.kill()
                    e.health -= 20
                    if e.health == 0:
                        ex = Explosion(e.rect.centerx, e.rect.centery)
                        explosion_group.add(ex)
                        e.kill()
                        # Boom
                        player.score += 10

            player_collide_enemy = pygame.sprite.spritecollide(player, enemy_group, True,
                                                               pygame.sprite.collide_mask)
            for e in player_collide_enemy:
                player1.health -= 80
                ex = Explosion(e.rect.centerx, e.rect.centery)
                explosion_group.add(ex)


            # Check for collision with enemy bullets
            bullet_hit_player = pygame.sprite.spritecollide(player, enemy_bullets, True, pygame.sprite.collide_mask)
            if bullet_hit_player:
                player1.health -= 2

            # Game over and reset
            if player1.health <= 0:
                player1.health = PLAYER_HEALTH
                player1.rect.center = (screen_width / 2, screen_height / 2)
                enemy_group.empty()
                explosion_group.empty()

                enemy_bullets.empty()
                player1.score = 0

                deathwords()

            if final_boss_spawned and len(enemy_group) == len(explosion_group) == 0:
                player1.health = PLAYER_HEALTH
                player1.rect.center = (screen_width / 2, screen_height / 2)
                enemy_group.empty()
                explosion_group.empty()
                enemy_bullets.empty()
                player1.score = 0
                win()
            

        # Draw everything
        screen.fill(BLACK)
        screen.blit(bg, (0, 0))
        player_group.draw(screen)
        enemy_group.draw(screen)
        enemy_bullets.draw(screen)

        for player in player_group:
            player.bullets.draw(screen)
            screen.blit(player.aim, player.aim_rect.topleft)

        for e in enemy_group:
            e.draw(screen)

        for e in explosion_group:
            e.draw()

        # Draw UI (score and health)
        Player_UI()

        # Update display
        pygame.display.update()

        # Cap the frame rate
        clock.tick(50)
        spam_time += 1

    pygame.quit()


start()