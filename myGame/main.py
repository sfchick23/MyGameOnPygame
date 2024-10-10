import pygame
from pygame import *
import sys
from game import main_logic, Player, Platform



pygame.init()
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 640

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Game')

clock = pygame.time.Clock()
gui_font = pygame.font.Font(None, 30)

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


def draw_text(text, font, text_col, x, y) -> None:
    img = font.render(text, True, text_col)
    screen.blit(img, (x, y))

font = pygame.font.SysFont("arialblack",40)
TEXT_COL = (255, 255, 255)

user_text = ''
base_font = pygame.font.Font(None, 40)
input_rect = pygame.Rect(SCREEN_WIDTH / 2 - 110, SCREEN_HEIGHT / 2 - 50, 140, 32)
color_active = pygame.Color("gray14")
color_passive = pygame.Color("gray15")
color = color_passive

pygame.mixer.init()
background_music_channel = pygame.mixer.Channel(0)
coin_sound_channel = pygame.mixer.Channel(1)

backgrounds_music = pygame.mixer.Sound("music_in_lobby.mp3")
backgrounds_music.set_volume(0.01)
background_music_channel.play(backgrounds_music, loops=-1)

button_start_game = Button('click for game', 200, 40, (SCREEN_WIDTH / 2 - 110, SCREEN_HEIGHT / 2 - 100), 6)
button_quit = Button('quit', 200, 40, (SCREEN_WIDTH / 2 - 110, SCREEN_HEIGHT / 2), 6)
button_switch_music = Button("OFF", 50, 25, (50, 550), 6)
button_setting = Button('setting', 200, 40, (SCREEN_WIDTH / 2 - 110, SCREEN_HEIGHT / 2 - 50), 6)
button_back = Button('back', 200, 40, (SCREEN_WIDTH / 2 - 110, SCREEN_HEIGHT / 2), 6)


main_menu = 'start_scene'


sound_play = True
active = False
name_user = False
game_start = False
screen_fill = 'start_scene'
run = True

while run:
    if screen_fill == 'main_scene' and name_user:
        screen.fill("skyblue")
    elif screen_fill == 'start_scene':
        screen.fill((30, 30,30))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                game_start = True
                main_menu = 'main'
                screen_fill = "main_scene"
        if event.type == pygame.KEYDOWN:
            if active == True:
                if event.key == pygame.K_BACKSPACE:
                    user_text = user_text[0:-1]
                else:
                    user_text += event.unicode
        if event.type == pygame.MOUSEBUTTONDOWN:
            if input_rect.collidepoint(event.pos):
                active = True
            if main_menu == "main":
                if button_start_game.top_rect.collidepoint(pygame.mouse.get_pos()):
                    main_menu = 'play_scene'
                if button_quit.top_rect.collidepoint(pygame.mouse.get_pos()):
                    print("Goodbye")
                    run = False
                if button_setting.top_rect.collidepoint(pygame.mouse.get_pos()):
                    main_menu = 'setting'

                if button_switch_music.top_rect.collidepoint(pygame.mouse.get_pos()):
                    if sound_play:
                        backgrounds_music.stop()
                        sound_play = False
                        button_switch_music.text_surf = gui_font.render("ON", True, '#FFFFFF')
                    else:
                        backgrounds_music.play()
                        sound_play = True
                        button_switch_music.text_surf = gui_font.render("OFF", True, '#FFFFFF')

            elif main_menu == 'setting':
                if button_back.top_rect.collidepoint(pygame.mouse.get_pos()):
                    main_menu = 'main'

    if active:
        color = color_active
    else:
        color = color_passive

    if game_start:
        if len(user_text) > 0:
            name_user = True
            if main_menu == 'main':
                active = False
                draw_text(f"Hello {user_text[:-1]}", font, TEXT_COL, SCREEN_WIDTH / 2 - 140, SCREEN_HEIGHT / 2 - 170)
                if sound_play:
                    backgrounds_music.play(-1)
                button_start_game.draw()
                button_quit.draw()
                button_switch_music.draw()
                button_setting.draw()
            elif main_menu == 'play_scene':
                if main_logic():
                    main_logic()
                else:
                    main_menu = "main"
            elif main_menu == 'setting':
                button_back.draw()

        else:
            game_start = False
            draw_text("Enter a name to start the game", font, (255,0,0), SCREEN_WIDTH / 2 - 350, SCREEN_HEIGHT / 2 + 100)

    else:
        draw_text("What will your name be", font, TEXT_COL, SCREEN_WIDTH / 2 - 250, SCREEN_HEIGHT / 2 - 120)
        draw_text("Click Enter for start game", font, TEXT_COL, SCREEN_WIDTH / 2 - 250, SCREEN_HEIGHT / 2 + 20)
        pygame.draw.rect(screen, color, input_rect)
        text_surface = base_font.render(user_text, True, (255, 0,0))
        screen.blit(text_surface, (input_rect.x+5, input_rect.y+5))
        input_rect.w = max(100, text_surface.get_width()+10)
        pygame.display.flip()

    pygame.display.update()
    clock.tick(60)

pygame.quit()