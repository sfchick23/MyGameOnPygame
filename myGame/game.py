import sys
import pygame
from pygame import *
import random
import math

WIN_WIDTH = 800
WIN_HEIGHT = 640
DISPLAY = (WIN_WIDTH, WIN_HEIGHT)
BACKGROUND_COLOR = "#004400"

PLATFORM_WIDTH = 32
PLATFORM_HEIGHT = 32
PLATFORM_COLOR = "#FF6262"

MOVE_SPEED = 5
WIDTH = 22
HEIGHT = 32
COLOR = "#888888"

JUMP_POWER = 10
GRAVITY = 0.35


class Player(sprite.Sprite):
    def __init__(self, x, y):
        sprite.Sprite.__init__(self)
        self.yvel = 0
        self.onGround = False
        self.xvel = 0
        self.startX = x
        self.startY = y
        self.image = pygame.image.load("Idle 01.png")
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)

    def update(self, left, right, up, platforms):
        if up:
            if self.onGround:
                self.yvel = -JUMP_POWER

        if left:
            self.xvel = -MOVE_SPEED

        if right:
            self.xvel = MOVE_SPEED
        if not (left or right):
            self.xvel = 0

        if not self.onGround:
            self.yvel += GRAVITY
        self.onGround = False
        self.rect.y += self.yvel
        self.collide(0, self.yvel, platforms)

        self.rect.x += self.xvel
        self.collide(self.xvel, 0, platforms)

    def collide(self, xvel, yvel, platforms):
        for p in platforms:
            if sprite.collide_rect(self, p):
                if xvel > 0:
                    self.rect.right = p.rect.left
                if xvel < 0:
                    self.rect.left = p.rect.right
                if yvel > 0:
                    self.rect.bottom = p.rect.top
                    self.onGround = True
                    self.yvel = 0
                if yvel < 0:
                    self.rect.top = p.rect.bottom
                    self.yvel = 0


class Platform(sprite.Sprite):
    def __init__(self, x, y, platform_type):
        sprite.Sprite.__init__(self)
        self.platform_type = platform_type

        if self.platform_type == 'terrain':
            self.image = pygame.image.load("Terrain (32x32).png")
        elif self.platform_type == 'terrain_fly':
            self.image = pygame.image.load("Terrain_fly.png")

        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)


class Cloud(sprite.Sprite):
    def __init__(self, x, y, cloud_type):
        sprite.Sprite.__init__(self)
        self.cloud_type = cloud_type
        cloud_images = {
            'cloud1': "Cloud1.png",
            'cloud2': "Cloud2.png",
            'cloud3': "Cloud3.png"
        }
        self.image = pygame.image.load(cloud_images[self.cloud_type])
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)


def spawn_clouds(background, num_clouds):
    cloud_types = ['cloud1', 'cloud2', 'cloud3']
    cloud_list = []

    for _ in range(num_clouds):
        x = random.randint(0, background.get_width())
        y = random.randint(0, background.get_height())
        cloud_type = random.choice(cloud_types)
        cloud = Cloud(x, y, cloud_type)
        cloud_list.append(cloud)

    return cloud_list


class Item(sprite.Sprite):
    def __init__(self, x, y, item_type, frame_duration):
        sprite.Sprite.__init__(self)
        self.item_type = item_type
        self.animation_frames = []
        self.frame_index = 0
        self.frame_duration = frame_duration
        self.frame_counter = 0

        if self.item_type == 'coin':
            for i in range(1, frame_duration):
                image = pygame.image.load(f"Coin/coin{i}.png")
                self.animation_frames.append(image)


        elif self.item_type == 'health_posion':
            for i in range(1, frame_duration):
                image = pygame.image.load(f'0{i}.png')
                self.animation_frames.append(image)

        self.image = self.animation_frames[self.frame_index]
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

    def update(self):
        self.frame_counter += 1
        if self.frame_counter >= self.frame_duration:
            self.frame_counter = 0
            self.frame_index = (self.frame_index + 1) % len(self.animation_frames)
            self.image = self.animation_frames[self.frame_index]


class Spike(sprite.Sprite):
    def __init__(self, x, y):
        sprite.Sprite.__init__(self)
        self.image = pygame.image.load("Spikes.png")
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y


def camera_configure(camera, target_rect, level_width, level_height):
    l, t, _, _ = target_rect
    _, _, w, h = camera

    player_centerx, player_centery = target_rect.centerx, target_rect.centery
    camera_centerx, camera_centery = l + w / 2, t + h / 2

    dx, dy = player_centerx - camera_centerx, player_centery - camera_centery

    l = max(0, min(l + dx, level_width - w))
    t = max(0, min(t + dy, level_height - h))

    return pygame.Rect(l, t, w, h)


def main_logic():
    pygame.init()

    hero = Player(55, 55)
    left = right = False
    up = False
    entities = pygame.sprite.Group()
    platforms = []
    entities.add(hero)
    game_reset = False
    game_win = False
    game_state = "gameplay"

    collected_items = 0
    total_items_to_collect = 20

    scroll_x = 0

    score = 0
    health = 3

    font = pygame.font.SysFont("Comic Sans", 20)

    remaining_minutes = 3
    remaining_seconds = 0
    total_seconds = remaining_minutes * 60

    pygame.init()
    background_music_channel = pygame.mixer.Channel(0)
    sound_coin_channel = pygame.mixer.Channel(1)

    sound_coin = pygame.mixer.Sound("sound_item_up.mp3")
    sound_coin.set_volume(0.5)

    sound_damage = pygame.mixer.Sound("Hit_sound.mp3")
    sound_damage.set_volume(1)

    sound_drink_posion = pygame.mixer.Sound('sound_drink_posion_life.mp3')
    sound_drink_posion.set_volume(1)

    game_over_sound = pygame.mixer.Sound("Game_over_sound.mp3")
    game_over_sound.set_volume(1)
    particles_list = []

    gui_font = pygame.font.Font(None, 30)

    class Particle:
        def __init__(self, x, y, color):
            self.x = x
            self.y = y
            self.radius = 2
            self.max_radius = random.randint(2, 10)
            self.color = color
            self.speed = random.uniform(1, 3)
            self.alpha = 255
            self.direction = random.uniform(0, 2 * math.pi)
            self.max_lifetime = random.randint(30, 60)

        def update(self):
            if self.radius < self.max_radius:
                self.radius += 0.5
            self.alpha -= 5
            self.x += math.cos(self.direction) * self.speed
            self.y += math.sin(self.direction) * self.speed
            self.max_lifetime -= 1

        def is_faded(self):
            return self.alpha <= 0 or self.max_lifetime <= 0

        def draw(self, surface):
            color = self.color
            draw_x, draw_y = int(self.x), int(self.y)
            pygame.draw.circle(surface, color, (draw_x, draw_y), int(self.radius))

    class Button:
        def __init__(self, text, width, height, pos, elevation):
            self.pressed = False
            self.elevation = elevation
            self.dynamic_elevation = elevation
            self.original_y_pos = pos[1]
            self.top_rect = pygame.Rect(pos, (width, height))
            self.top_color = '#475F77'
            self.text_surf = gui_font.render(text, True, '#FFFFFF')
            self.text_rect = self.text_surf.get_rect(center=self.top_rect.center)

            self.buttom_rect = pygame.Rect(pos, (width, elevation))
            self.buttom_color = "#354B5E"

        def draw(self):
            self.top_rect.y = self.original_y_pos - self.dynamic_elevation
            self.text_rect.center = self.top_rect.center
            self.buttom_rect.midtop = self.top_rect.midtop
            self.buttom_rect.height = self.top_rect.height + self.dynamic_elevation

            pygame.draw.rect(screen, self.buttom_color, self.buttom_rect, border_radius=16)
            pygame.draw.rect(screen, self.top_color, self.top_rect, border_radius=16)
            screen.blit(self.text_surf, self.text_rect)

            self.check_click()

        def check_click(self):
            mouse_pos = pygame.mouse.get_pos()
            if self.top_rect.collidepoint(mouse_pos):
                self.top_color = "#D73B4B"
                if pygame.mouse.get_pressed()[0]:
                    self.dynamic_elevation = 0
                    self.pressed = True
                else:
                    if self.pressed:
                        self.dynamic_elevation = self.elevation
                        self.pressed = False
            else:
                self.dynamic_elevation = self.elevation
                self.top_color = "#475F77"

    button_resume = Button('resume', 200, 40, (WIN_WIDTH / 2 - 110, WIN_HEIGHT / 2 - 100), 6)
    button_setting = Button('setting', 200, 40, (WIN_WIDTH / 2 - 110, WIN_HEIGHT / 2 - 50), 6)
    button_quit = Button('exit from game', 200, 40, (WIN_WIDTH / 2 - 110, WIN_HEIGHT / 2), 6)
    button_change_layout = Button('WASD', 200, 40, (WIN_WIDTH / 2 - 110, WIN_HEIGHT / 2 - 50), 6)
    button_back = Button('back', 200, 40, (WIN_WIDTH / 2 - 110, WIN_HEIGHT / 2), 6)

    level = [
        "-----------------------------------------",
        "-                                       -",
        "-                 ^                     -",
        "-      $          =       $             -",
        "-      =                   =            -",
        "-                                 $  *  -",
        "-                              -     -  -",
        "-                                       -",
        "-             =       =                 -",
        "-      $                  $             -",
        "-      =                   =            -",
        "-                                 $     -",
        "-                                --     -",
        "-           - =              $          -",
        "-                            =          -",
        "-         $                             -",
        "-         =           ^                 -",
        "-    ^                =                 -",
        "-    ====        $$                     -",
        "-                =                      -",
        "-          $               $            -",
        "-        ====             ^-$           -",
        "-                         ----          -",
        "-                                       -",
        "-                   ^^^                 -",
        "-----------------------------------------"]
    level1 = ["-----------------------------------------",
              "-                                       -",
              "-      $         ^        $             -",
              "-      =         =         =            -",
              "-           -                 ^    $    -",
              "-                     =       -    -    -",
              "-       -                               -",
              "-            ^                          -",
              "-            =                          -",
              "-                 -                     -",
              "-      $^                               -",
              "-      =                                -",
              "-                      ^$$              -",
              "-           ^  *       =           $$   -",
              "-           - ---                =      -",
              "-                                       -",
              "-          $                $           -",
              "-         ----        $    =            -",
              "-                     -                 -",
              "-    =              ^                   -",
              "-                   =                   -",
              "-          $                            -",
              "-        ----             ^ $           -",
              "-                         ----          -",
              "-              ^^                  ^^ * -",
              "-----------------------------------------"]

    current_level = level

    items = pygame.sprite.Group()

    thorns = pygame.sprite.Group()

    healths = pygame.sprite.Group()

    timer = pygame.time.Clock()
    x = y = 0
    for row in current_level:
        for col in row:
            if col == '-':
                pf = Platform(x, y, "terrain")
                entities.add(pf)
                platforms.append(pf)
            if col == "=":
                pf = Platform(x, y, "terrain_fly")
                entities.add(pf)
                platforms.append(pf)
            if col == "$":
                item = Item(x, y, "coin", 5)
                entities.add(item)
                items.add(item)
            if col == '^':
                thorn = Spike(x, y)
                entities.add(thorn)
                thorns.add(thorn)
            if col == '*':
                hp = Item(x, y, 'health_posion', 8)
                entities.add(hp)
                healths.add(hp)

            x += PLATFORM_WIDTH
        y += PLATFORM_HEIGHT
        x = 0

    level_width = 41 * PLATFORM_WIDTH
    level_height = len(level) * PLATFORM_HEIGHT

    particles = pygame.sprite.Group()

    def collect_item(item, hero, items, collected_items):
        if item.rect.colliderect(hero):
            collected_items += 1
            sound_coin_channel.play(sound_coin)
            items.remove(item)
            item.kill()

            create_particles(hero.rect.centerx, hero.rect.centery)

            return 1
        return 0

    def create_particles(x, y):
        num_particles = 20
        for _ in range(num_particles):
            particle = Particle(x - camera.x, y - camera.y, color=(255, 215, 0))
            particles_list.append(particle)

    def create_red_particles(x, y):
        num_particles = 20
        for _ in range(num_particles):
            particle = Particle(x - camera.x, y - camera.y, (255, 0, 0))
            particles_list.append(particle)

    def check_win_condition():
        return collected_items == total_items_to_collect

    if check_win_condition():
        game_win = True

    camera = pygame.Rect(0, 0, WIN_WIDTH, WIN_HEIGHT)
    screen = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))

    clock = pygame.time.Clock()
    start_time = pygame.time.get_ticks()

    background_image = pygame.image.load("background_1.png")
    background_image = pygame.transform.scale(background_image, (WIN_WIDTH, WIN_HEIGHT))

    clouds = spawn_clouds(background_image, 10)

    layout = "ARROWS"
    layout_WASD = False

    game_play = True

    while not health == 0 and game_play:
        for e in pygame.event.get():
            if e.type == QUIT:
                raise SystemExit
            if game_state == "gameplay":
                if layout == 'ARROWS':
                    if e.type == KEYDOWN and e.key == K_LEFT:
                        left = True
                    if e.type == KEYDOWN and e.key == K_RIGHT:
                        right = True
                    if e.type == KEYUP and e.key == K_RIGHT:
                        right = False
                    if e.type == KEYUP and e.key == K_LEFT:
                        left = False
                    if e.type == KEYDOWN and e.key == K_UP:
                        up = True
                    if e.type == KEYUP and e.key == K_UP:
                        up = False
                elif layout == 'WASD':
                    if e.type == KEYDOWN and e.key == K_a:
                        left = True
                    if e.type == KEYDOWN and e.key == K_d:
                        right = True
                    if e.type == KEYUP and e.key == K_d:
                        right = False
                    if e.type == KEYUP and e.key == K_a:
                        left = False
                    if e.type == KEYDOWN and e.key == K_w:
                        up = True
                    if e.type == KEYUP and e.key == K_w:
                        up = False

                if e.type == KEYDOWN and e.key == K_ESCAPE:
                    game_state = 'pause'

            elif game_state == 'pause':
                button_resume.draw()
                button_quit.draw()
                button_setting.draw()
                if e.type == pygame.MOUSEBUTTONDOWN:
                    if button_resume.top_rect.collidepoint(pygame.mouse.get_pos()):
                        game_state = 'gameplay'
                    if button_setting.top_rect.collidepoint(pygame.mouse.get_pos()):
                        game_state = 'setting'
                    if button_quit.top_rect.collidepoint(pygame.mouse.get_pos()):
                        game_play = False

                if e.type == KEYDOWN and e.key == K_ESCAPE:
                    game_state = "gameplay"

            elif game_state == 'setting':
                button_resume.draw()
                button_change_layout.draw()
                button_back.draw()
                if e.type == pygame.MOUSEBUTTONDOWN:
                    if button_change_layout.top_rect.collidepoint(pygame.mouse.get_pos()):
                        if not layout_WASD:
                            layout = 'WASD'
                            layout_WASD = True
                            button_change_layout.text_surf = gui_font.render("ARROWS", True, "#FFFFFF")
                        else:
                            layout = 'ARROWS'
                            layout_WASD = False
                            button_change_layout.text_surf = gui_font.render('WASD', True, "#FFFFFF")
                    if button_back.top_rect.collidepoint(pygame.mouse.get_pos()):
                        game_state = "pause"

                    if button_resume.top_rect.collidepoint(pygame.mouse.get_pos()):
                        game_state = 'gameplay'

                if e.type == KEYDOWN and e.key == K_ESCAPE:
                    game_state = "pause"

        if game_state == "gameplay":
            if not game_reset:
                if len(items) == 0:
                    reset_level(level1, hero, entities, platforms, items, thorns, healths, particles_list)
                    game_reset = True

            screen.blit(background_image, (0, 0))

            current_time = pygame.time.get_ticks()
            elapsed_time = (current_time - start_time) // 1000

            remaining_seconds = max(0, total_seconds - elapsed_time)
            remaining_minutes = remaining_seconds // 60
            remaining_seconds %= 60

            if remaining_seconds == 0 and remaining_minutes == 0:
                print("Game Over (Time is up)")
                game_over_sound.play()
                pygame.quit()
                sys.exit()

            if remaining_seconds == 0 and remaining_minutes == 0:
                print("Game Over (Time is up)")
                game_over_sound.play()
                pygame.quit()
                sys.exit()

            for cloud in clouds:
                screen.blit(cloud.image, (cloud.rect.x, cloud.rect.y))

            hero.update(left, right, up, platforms)

            camera = camera_configure(camera, hero.rect, level_width, level_height)

            for e in entities:
                if e != hero:
                    screen.blit(e.image, (e.rect.x - camera.x, e.rect.y - camera.y))

            screen.blit(hero.image, (hero.rect.x - camera.x, hero.rect.y - camera.y))

            for item in items:
                score += collect_item(item, hero, items, collected_items)

            for particle in particles_list:
                particle.update()
                if particle.is_faded():
                    particles_list.remove(particle)
                else:
                    particle.draw(screen)

            for spike in thorns:
                if spike.rect.colliderect(hero):
                    sound_damage.play()
                    create_red_particles(spike.rect.centerx, spike.rect.centery)
                    thorns.remove(spike)
                    spike.kill()
                    health -= 1
                    if score > 2:
                        score -= 2

            for health_posion in healths:
                if health_posion.rect.colliderect(hero):
                    sound_drink_posion.play()
                    create_red_particles(health_posion.rect.centerx, health_posion.rect.centery)
                    healths.remove(health_posion)
                    health_posion.kill()
                    health += 1

            if health == 0:
                game_play = False
                game_over_sound.play()
                print("hero dead")

            items.update()
            healths.update()

            score_text = font.render("Score: " + str(score), True, (255, 255, 0))
            screen.blit(score_text, (30, 20))

            health_text = font.render("Health: " + str(health), True, (255, 0, 0))
            screen.blit(health_text, (30, 40))

            time_text = font.render(f"Time: {remaining_minutes:02d}:{remaining_seconds:02d}", True, (255, 255, 255))
            screen.blit(time_text, (30, 60))

        pygame.display.flip()
        clock.tick(60)

    return game_play


def reset_level(level_data, hero, entities, platforms, items, thorns, healths, particles_list):
    global current_level, game_state
    current_level = level_data
    game_state = "gameplay"

    hero.rect.x = hero.startX
    hero.rect.y = hero.startY

    entities.empty()
    platforms.clear()
    items.empty()
    thorns.empty()
    healths.empty()
    particles_list.clear()

    x = y = 0
    for row in current_level:
        for col in row:
            if col == '-':
                pf = Platform(x, y, "terrain")
                entities.add(pf)
                platforms.append(pf)
            if col == "=":
                pf = Platform(x, y, "terrain_fly")
                entities.add(pf)
                platforms.append(pf)
            if col == "$":
                item = Item(x, y, "coin", 5)
                entities.add(item)
                items.add(item)
            if col == '^':
                thorn = Spike(x, y)
                entities.add(thorn)
                thorns.add(thorn)
            if col == '*':
                hp = Item(x, y, 'health_posion', 8)
                entities.add(hp)
                healths.add(hp)

            x += PLATFORM_WIDTH
        y += PLATFORM_HEIGHT
        x = 0

