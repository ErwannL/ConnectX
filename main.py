import pygame
import sys
import random
import numpy as np
from enum import Enum
import logging
import os
from datetime import datetime
from settings import Settings
from ai import AI
import time

# Set up logging
log_dir = "logs"
if not os.path.exists(log_dir):
    os.makedirs(log_dir)

log_file = os.path.join(log_dir, f"connectx_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler()
    ]
)

# Asset paths
ASSETS_DIR = "assets"
MUSIC_FILE = os.path.join(ASSETS_DIR, "music.mp3")
DROP_SFX_FILE = os.path.join(ASSETS_DIR, "drop.mp3")

# Initialize Pygame
try:
    pygame.init()
    logging.info("Pygame initialized successfully")
except Exception as e:
    logging.error(f"Failed to initialize Pygame: {e}")
    sys.exit(1)

# Try to initialize audio, but continue if it fails
try:
    pygame.mixer.init()
    logging.info("Audio system initialized successfully")
except pygame.error as e:
    logging.warning(f"Audio initialization failed: {e}. Game will run without sound.")
    pygame.mixer.quit()

# Get screen info
try:
    screen_info = pygame.display.Info()
    logging.info(f"Screen info retrieved: {screen_info.current_w}x{screen_info.current_h}")
except Exception as e:
    logging.error(f"Failed to get screen info: {e}")
    sys.exit(1)

WINDOW_WIDTH = 800  # Default window size
WINDOW_HEIGHT = 600
FULLSCREEN_WIDTH = screen_info.current_w
FULLSCREEN_HEIGHT = screen_info.current_h

# Constants
BOARD_ROWS = 6
BOARD_COLS = 7
SQUARE_SIZE = 80
RADIUS = int(SQUARE_SIZE/2 - 5)

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
BLUE = (13, 27, 42)  # Dark blue background
RED = (255, 0, 0)
YELLOW = (255, 255, 0)
GRAY = (128, 128, 128)
COLOR_PALETTE = [
    (255, 0, 0), (255, 255, 0), (0, 255, 0), (0, 0, 255),
    (255, 128, 0), (128, 0, 255), (0, 255, 255), (255, 0, 255),
    (255, 255, 255), (128, 128, 128)
]

class GameState(Enum):
    MENU = 1
    PLAY_MENU = 2
    PLAYING = 3
    SETTINGS = 4

class Button:
    def __init__(self, x, y, width, height, text, font_size=40):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.font = pygame.font.SysFont('Comic Sans MS', font_size)
        self.is_hovered = False

    def draw(self, screen):
        color = (50, 50, 50) if self.is_hovered else BLACK
        pygame.draw.rect(screen, color, self.rect)
        pygame.draw.rect(screen, WHITE, self.rect, 2)
        text_surface = self.font.render(self.text, True, WHITE)
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.is_hovered = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                return True
        return False

class Slider:
    def __init__(self, x, y, width, min_value, max_value, value, label):
        self.rect = pygame.Rect(x, y, width, 20)
        self.min_value = min_value
        self.max_value = max_value
        self.value = value
        self.label = label
        self.dragging = False
        self.font = pygame.font.SysFont('Comic Sans MS', 24)

    def draw(self, screen):
        pygame.draw.rect(screen, WHITE, self.rect, 2)
        fill_width = int((self.value - self.min_value) / (self.max_value - self.min_value) * self.rect.width)
        pygame.draw.rect(screen, WHITE, (self.rect.x, self.rect.y, fill_width, self.rect.height))
        label_surface = self.font.render(f"{self.label}: {int(self.value)}", True, WHITE)
        screen.blit(label_surface, (self.rect.x, self.rect.y - 30))

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and self.rect.collidepoint(event.pos):
            self.dragging = True
        elif event.type == pygame.MOUSEBUTTONUP:
            self.dragging = False
        elif event.type == pygame.MOUSEMOTION and self.dragging:
            rel_x = event.pos[0] - self.rect.x
            rel_x = max(0, min(rel_x, self.rect.width))
            self.value = self.min_value + (rel_x / self.rect.width) * (self.max_value - self.min_value)
            return True
        return False

class ColorPicker:
    def __init__(self, x, y, selected_color, label):
        self.x = x
        self.y = y
        self.selected_color = selected_color
        self.label = label
        self.font = pygame.font.SysFont('Comic Sans MS', 24)
        self.swatch_size = 30
        self.swatch_margin = 10
        self.palette = COLOR_PALETTE

    def draw(self, screen):
        label_surface = self.font.render(self.label, True, WHITE)
        screen.blit(label_surface, (self.x, self.y))
        for i, color in enumerate(self.palette):
            rect = pygame.Rect(self.x + i*(self.swatch_size+self.swatch_margin), self.y+30, self.swatch_size, self.swatch_size)
            pygame.draw.rect(screen, color, rect)
            pygame.draw.rect(screen, WHITE, rect, 2)
            if color == self.selected_color:
                pygame.draw.rect(screen, (0,255,0), rect, 3)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            for i, color in enumerate(self.palette):
                rect = pygame.Rect(self.x + i*(self.swatch_size+self.swatch_margin), self.y+30, self.swatch_size, self.swatch_size)
                if rect.collidepoint(event.pos):
                    self.selected_color = color
                    return color
        return None

class ToggleButton:
    def __init__(self, x, y, width, height, options, selected_index=0, font_size=28):
        self.rect = pygame.Rect(x, y, width, height)
        self.options = options
        self.selected_index = selected_index
        self.font = pygame.font.SysFont('Comic Sans MS', font_size)

    def draw(self, screen):
        for i, option in enumerate(self.options):
            opt_rect = pygame.Rect(self.rect.x + i * (self.rect.width // 2), self.rect.y, self.rect.width // 2, self.rect.height)
            color = (50, 50, 50) if i == self.selected_index else BLACK
            pygame.draw.rect(screen, color, opt_rect)
            pygame.draw.rect(screen, WHITE, opt_rect, 2)
            text_surface = self.font.render(option, True, WHITE)
            text_rect = text_surface.get_rect(center=opt_rect.center)
            screen.blit(text_surface, text_rect)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            for i in range(len(self.options)):
                opt_rect = pygame.Rect(self.rect.x + i * (self.rect.width // 2), self.rect.y, self.rect.width // 2, self.rect.height)
                if opt_rect.collidepoint(event.pos):
                    self.selected_index = i
                    return True
        return False

class AICheckboxList:
    def __init__(self, x, y, options, selected_index=1, font_size=28):
        self.x = x
        self.y = y
        self.options = options
        self.selected_index = selected_index
        self.font = pygame.font.SysFont('Comic Sans MS', font_size)
        self.box_size = 28
        self.spacing = 40

    def draw(self, screen):
        for i, option in enumerate(self.options):
            rect = pygame.Rect(self.x, self.y + i * self.spacing, self.box_size, self.box_size)
            pygame.draw.rect(screen, WHITE, rect, 2)
            if i == self.selected_index:
                pygame.draw.line(screen, WHITE, (rect.left+5, rect.centery), (rect.centerx, rect.bottom-5), 3)
                pygame.draw.line(screen, WHITE, (rect.centerx, rect.bottom-5), (rect.right-5, rect.top+5), 3)
            text_surface = self.font.render(option, True, WHITE)
            screen.blit(text_surface, (rect.right + 10, rect.y))

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            for i in range(len(self.options)):
                rect = pygame.Rect(self.x, self.y + i * self.spacing, self.box_size, self.box_size)
                if rect.collidepoint(event.pos):
                    self.selected_index = i
                    return True
        return False

class FullscreenToggleButton:
    def __init__(self, x, y, width=180, height=40, font_size=28):
        self.rect = pygame.Rect(x, y, width, height)
        self.font = pygame.font.SysFont('Comic Sans MS', font_size)
        self.is_fullscreen = False

    def draw(self, screen, is_fullscreen):
        label = "Windowed Mode" if is_fullscreen else "Fullscreen Mode"
        color = (50, 50, 50) if is_fullscreen else BLACK
        pygame.draw.rect(screen, color, self.rect)
        pygame.draw.rect(screen, WHITE, self.rect, 2)
        text_surface = self.font.render(label, True, WHITE)
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and self.rect.collidepoint(event.pos):
            return True
        return False

class Game:
    def __init__(self):
        self.settings = Settings()
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("ConnectX")
        self.clock = pygame.time.Clock()
        self.game_state = GameState.MENU
        self.board = np.zeros((BOARD_ROWS, BOARD_COLS))
        self.game_over = False
        self.human_piece = 1
        self.ai_piece = 2
        self.current_player = self.human_piece
        self.is_fullscreen = False
        self.ai_difficulty = self.settings.get_ai_difficulty()
        self.player_colors = self.settings.get_player_colors()
        self.music_volume = self.settings.current_settings['music_volume']
        self.sfx_volume = self.settings.current_settings['sfx_volume']
        self.sfx_enabled = self.sfx_volume > 0
        self.ai_player = AI(self.ai_difficulty)
        self.winner = None
        self.draw = False
        self.show_end_popup = False
        self.end_popup_button = Button(self.screen.get_width()//2 - 120, self.screen.get_height()//2 + 100, 240, 60, "MAIN MENU")
        self.winning_coords = []
        self.animating = False
        self.anim_drop_row = None
        self.anim_drop_col = None
        self.anim_drop_piece = None
        self.anim_drop_y = None
        self.anim_speed = 30
        self.init_buttons()
        self.init_settings_controls()
        self.init_play_menu_controls()
        self.load_sounds()
        self.play_music()
        self.board_x = (WINDOW_WIDTH - (BOARD_COLS * SQUARE_SIZE)) // 2
        self.board_y = (WINDOW_HEIGHT - (BOARD_ROWS * SQUARE_SIZE)) // 2 - (SQUARE_SIZE // 2)
        self.vs_ai = False
        self.ai_starts = False
        self.go_back_playmenu = Button(self.screen.get_width()//2 - 100, self.screen.get_height()//2 + 300, 200, 50, "GO BACK")

    def init_buttons(self):
        button_width = 240
        button_height = 60
        center_x = self.screen.get_width() // 2
        spacing = 20
        self.menu_buttons = {
            'play': Button(center_x - button_width//2, self.screen.get_height()//2 - button_height - spacing, button_width, button_height, "PLAY"),
            'settings': Button(center_x - button_width//2, self.screen.get_height()//2, button_width, button_height, "SETTINGS"),
            'exit': Button(center_x - button_width//2, self.screen.get_height()//2 + button_height + spacing, button_width, button_height, "EXIT")
        }
        self.settings_buttons = {
            'back': Button(center_x - button_width//2, self.screen.get_height() - button_height - spacing, button_width, button_height, "BACK")
        }
        self.play_vs_friend_button = Button(center_x - 300 + 30, self.screen.get_height()//2 + 10, button_width, button_height, "PLAY")
        self.play_vs_ai_button = Button(center_x + 60, self.screen.get_height()//2 + 150, button_width, button_height, "PLAY VS AI")
        self.go_back_playmenu = Button(center_x - 120, self.screen.get_height()//2 + 300, button_width, button_height, "GO BACK")

    def init_settings_controls(self):
        self.music_slider = Slider(300, 180, 200, 0, 100, self.music_volume, "Music Volume")
        self.sfx_slider = Slider(300, 240, 200, 0, 100, self.sfx_volume, "SFX Volume")
        self.color_picker1 = ColorPicker(300, 320, self.player_colors[0], "Player 1 Color")
        self.color_picker2 = ColorPicker(300, 380, self.player_colors[1], "Player 2 Color")

    def init_play_menu_controls(self):
        center_x = self.screen.get_width() // 2
        self.ai_checkbox_list = AICheckboxList(center_x + 80, self.screen.get_height()//2 - 40, ["EASY", "MEDIUM", "HARD"], ["EASY", "MEDIUM", "HARD"].index(self.ai_difficulty))
        self.toggle_starter = ToggleButton(center_x + 80, self.screen.get_height()//2 + 60, 220, 60, ["Player", "AI"], 0)

    def load_sounds(self):
        self.music_loaded = False
        self.sfx_loaded = False
        if os.path.exists(MUSIC_FILE):
            try:
                pygame.mixer.music.load(MUSIC_FILE)
                self.music_loaded = True
            except Exception as e:
                logging.warning(f"Could not load music: {e}")
        else:
            logging.warning("Music file not found.")
        if os.path.exists(DROP_SFX_FILE):
            try:
                self.drop_sound = pygame.mixer.Sound(DROP_SFX_FILE)
                self.sfx_loaded = True
            except Exception as e:
                logging.warning(f"Could not load drop SFX: {e}")
        else:
            logging.warning("Drop SFX file not found.")

    def play_music(self):
        if self.music_loaded:
            pygame.mixer.music.set_volume(self.music_slider.value / 100.0)
            pygame.mixer.music.play(-1)

    def stop_music(self):
        if self.music_loaded:
            pygame.mixer.music.stop()

    def play_drop_sfx(self):
        if self.sfx_loaded and self.sfx_enabled:
            self.drop_sound.set_volume(self.sfx_slider.value / 100.0)
            self.drop_sound.play()

    def toggle_fullscreen(self, force_windowed=False):
        if force_windowed or self.is_fullscreen:
            self.is_fullscreen = False
            self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        else:
            self.is_fullscreen = True
            self.screen = pygame.display.set_mode((FULLSCREEN_WIDTH, FULLSCREEN_HEIGHT), pygame.FULLSCREEN)
        self.board_x = (self.screen.get_width() - (BOARD_COLS * SQUARE_SIZE)) // 2
        self.board_y = (self.screen.get_height() - (BOARD_ROWS * SQUARE_SIZE)) // 2 - (SQUARE_SIZE // 2)
        self.init_buttons()
        self.init_settings_controls()
        self.init_play_menu_controls()

    def draw_board(self, anim_drop=None):
        try:
            self.screen.fill(BLUE)
            
            # Show turn info
            font = pygame.font.SysFont('Comic Sans MS', 32)
            if not self.game_over:
                if self.vs_ai:
                    if self.current_player == self.human_piece:
                        turn_text = "Your Turn"
                    else:
                        turn_text = "AI's Turn"
                else:
                    turn_text = f"Player {self.current_player}'s Turn"
            else:
                turn_text = "Game Over"  # Default text

            turn_surface = font.render(turn_text, True, WHITE)
            self.screen.blit(turn_surface, (self.screen.get_width()//2 - turn_surface.get_width()//2, 20))

            # Draw board background
            for c in range(BOARD_COLS):
                for r in range(BOARD_ROWS):
                    pygame.draw.rect(self.screen, BLACK, 
                                   (self.board_x + c*SQUARE_SIZE, 
                                    self.board_y + r*SQUARE_SIZE + SQUARE_SIZE, 
                                    SQUARE_SIZE, SQUARE_SIZE))
                    pygame.draw.circle(self.screen, BLUE, 
                                     (int(self.board_x + c*SQUARE_SIZE + SQUARE_SIZE/2), 
                                      int(self.board_y + r*SQUARE_SIZE + SQUARE_SIZE + SQUARE_SIZE/2)), 
                                     RADIUS)
            
            # Draw pieces
            for c in range(BOARD_COLS):
                for r in range(BOARD_ROWS):
                    if self.board[r][c] != 0:
                        color = self.player_colors[int(self.board[r][c])-1]
                        glow = False
                        if self.game_over and (r, c) in self.winning_coords:
                            t = time.time()
                            if int(t*4)%2 == 0:
                                color = (min(color[0]+120,255), min(color[1]+120,255), min(color[2]+120,255))
                            glow = True
                        pygame.draw.circle(
                            self.screen, color,
                            (int(self.board_x + c*SQUARE_SIZE + SQUARE_SIZE/2),
                             self.screen.get_height() - int(self.board_y + r*SQUARE_SIZE + SQUARE_SIZE/2)),
                            RADIUS+4 if glow else RADIUS)
            
            # Draw animating drop
            if anim_drop:
                col, y, piece = anim_drop
                color = self.player_colors[piece-1]
                pygame.draw.circle(
                    self.screen, color,
                    (int(self.board_x + col*SQUARE_SIZE + SQUARE_SIZE/2), int(y)),
                    RADIUS)
            
            # Draw column indicators
            if not self.animating and not self.game_over:
                mouse_x = pygame.mouse.get_pos()[0]
                for c in range(BOARD_COLS):
                    if self.board[BOARD_ROWS-1][c] == 0:
                        if self.board_x + c*SQUARE_SIZE <= mouse_x <= self.board_x + (c+1)*SQUARE_SIZE:
                            s = pygame.Surface((SQUARE_SIZE, SQUARE_SIZE), pygame.SRCALPHA)
                            indicator_color = self.player_colors[self.current_player-1]
                            pygame.draw.circle(s, (*indicator_color, 128), (int(SQUARE_SIZE/2), int(SQUARE_SIZE/2)), RADIUS)
                            self.screen.blit(s, (self.board_x + c*SQUARE_SIZE, 0))
            
            # Draw instructions
            font2 = pygame.font.SysFont('Comic Sans MS', 20)
            instructions = [
                "Click on a column to drop your piece",
                "Press F to toggle fullscreen",
                "Press S for windowed mode",
                "Press ESC to return to menu"
            ]
            y_pos = 60
            for instruction in instructions:
                text = font2.render(instruction, True, WHITE)
                self.screen.blit(text, (10, y_pos))
                y_pos += 25
            
            # Draw end popup if needed
            if self.show_end_popup:
                self.draw_end_popup()
            
            pygame.display.update()
        except Exception as e:
            logging.error(f"Error drawing board: {e}")

    def draw_end_popup(self):
        popup_width = 400
        popup_height = 200
        popup_x = self.screen.get_width()//2 - popup_width//2
        popup_y = self.screen.get_height()//2 - popup_height//2
        pygame.draw.rect(self.screen, GRAY, (popup_x, popup_y, popup_width, popup_height))
        pygame.draw.rect(self.screen, WHITE, (popup_x, popup_y, popup_width, popup_height), 4)
        font = pygame.font.SysFont('Comic Sans MS', 36)
        if self.draw:
            msg = "It's a draw!"
            color = WHITE
        else:
            if self.vs_ai:
                if self.winner == self.human_piece:
                    msg = "You win!"
                else:
                    msg = "AI wins!"
            else:
                msg = f"Player {self.winner} wins!"
            color = self.player_colors[self.winner-1]
        msg_surface = font.render(msg, True, color)
        msg_rect = msg_surface.get_rect(center=(self.screen.get_width()//2, popup_y + 60))
        self.screen.blit(msg_surface, msg_rect)
        self.end_popup_button.rect.topleft = (self.screen.get_width()//2 - 120, popup_y + 120)
        self.end_popup_button.draw(self.screen)

    def draw_menu(self):
        try:
            self.screen.fill(BLUE)
            title_font = pygame.font.SysFont('Comic Sans MS', 60)
            title_text = title_font.render("ConnectX", True, WHITE)
            title_rect = title_text.get_rect(center=(self.screen.get_width()//2, 100))
            self.screen.blit(title_text, title_rect)
            for button in self.menu_buttons.values():
                button.draw(self.screen)
            pygame.display.update()
        except Exception as e:
            logging.error(f"Error drawing menu: {e}")

    def draw_settings(self):
        self.screen.fill(BLUE)
        title_font = pygame.font.SysFont('Comic Sans MS', 40)
        title_text = title_font.render("Settings", True, WHITE)
        title_rect = title_text.get_rect(center=(self.screen.get_width()//2, 100))
        self.screen.blit(title_text, title_rect)
        self.music_slider.draw(self.screen)
        self.sfx_slider.draw(self.screen)
        self.color_picker1.draw(self.screen)
        self.color_picker2.draw(self.screen)
        for button in self.settings_buttons.values():
            button.draw(self.screen)
        pygame.display.update()

    def draw_play_menu(self):
        self.screen.fill(BLUE)
        center_x = self.screen.get_width() // 2
        title_font = pygame.font.SysFont('Comic Sans MS', 40)
        title_text = title_font.render("Choose Game Mode", True, WHITE)
        title_rect = title_text.get_rect(center=(center_x, 40))
        self.screen.blit(title_text, title_rect)
        
        left_x = center_x - 300
        right_x = center_x + 80
        col_width = 300
        left_box_height = 320
        right_box_height = 500
        section_font = pygame.font.SysFont('Comic Sans MS', 32)
        box_y_offset = -120
        
        # Draw left box
        left_box_top = self.screen.get_height()//2 - 100 + box_y_offset
        pygame.draw.rect(self.screen, WHITE, (left_x-30, left_box_top, col_width, left_box_height), 2)
        left_title = section_font.render("Play vs Friend", True, WHITE)
        self.screen.blit(left_title, (left_x, left_box_top + 20))
        self.play_vs_friend_button.rect.topleft = (left_x - 30 + (col_width - self.play_vs_friend_button.rect.width)//2, left_box_top + left_box_height - self.play_vs_friend_button.rect.height - 30)
        self.play_vs_friend_button.draw(self.screen)
        
        # Draw right box
        right_box_top = self.screen.get_height()//2 - 120 + box_y_offset
        pygame.draw.rect(self.screen, WHITE, (right_x-30, right_box_top, col_width, right_box_height), 2)
        right_title = section_font.render("Play vs AI", True, WHITE)
        self.screen.blit(right_title, (right_x, right_box_top + 20))
        
        # AI level checkboxes
        self.ai_checkbox_list.x = right_x + 20
        self.ai_checkbox_list.y = right_box_top + 70
        self.ai_checkbox_list.spacing = 70
        self.ai_checkbox_list.draw(self.screen)
        
        # Toggle starter
        toggle_label_font = pygame.font.SysFont('Comic Sans MS', 28)
        toggle_label = toggle_label_font.render("Start:", True, WHITE)
        toggle_label_x = right_x + 70 + self.toggle_starter.rect.width//4
        toggle_label_y = right_box_top + 70 + self.ai_checkbox_list.spacing * len(self.ai_checkbox_list.options) + 10
        toggle_label_rect = toggle_label.get_rect(center=(right_x + 70 + self.toggle_starter.rect.width//2, toggle_label_y))
        self.screen.blit(toggle_label, toggle_label_rect)
        
        self.toggle_starter.rect.topleft = (right_x + 40, toggle_label_rect.bottom + 10)
        self.toggle_starter.rect.width = 200
        self.toggle_starter.rect.height = 70
        self.toggle_starter.draw(self.screen)
        
        # Play vs AI button
        self.play_vs_ai_button.rect.topleft = (right_x - 30 + (col_width - self.play_vs_ai_button.rect.width)//2, right_box_top + right_box_height - self.play_vs_ai_button.rect.height - 30)
        self.play_vs_ai_button.rect.width = 260
        self.play_vs_ai_button.rect.height = 60
        self.play_vs_ai_button.draw(self.screen)
        
        # Go Back button
        self.go_back_playmenu.rect.topleft = (center_x - 120, self.screen.get_height()//2 + 240)
        self.go_back_playmenu.rect.width = 240
        self.go_back_playmenu.rect.height = 60
        self.go_back_playmenu.draw(self.screen)
        
        pygame.display.update()

    def handle_settings_events(self, event):
        if event.type == pygame.QUIT:
            return False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.game_state = GameState.MENU
                return True
            elif event.key == pygame.K_f:
                self.toggle_fullscreen()
            elif event.key == pygame.K_s:
                self.toggle_fullscreen(force_windowed=True)
        
        changed = False
        if self.music_slider.handle_event(event):
            self.settings.update_setting('music_volume', int(self.music_slider.value))
            if self.music_loaded:
                pygame.mixer.music.set_volume(self.music_slider.value / 100.0)
            changed = True
        if self.sfx_slider.handle_event(event):
            self.settings.update_setting('sfx_volume', int(self.sfx_slider.value))
            changed = True
        color1 = self.color_picker1.handle_event(event)
        if color1:
            self.settings.current_settings['player_colors'][0] = color1
            self.settings.save_settings()
            self.player_colors[0] = color1
            changed = True
        color2 = self.color_picker2.handle_event(event)
        if color2:
            self.settings.current_settings['player_colors'][1] = color2
            self.settings.save_settings()
            self.player_colors[1] = color2
            changed = True
        for button_name, button in self.settings_buttons.items():
            if button.handle_event(event):
                if button_name == 'back':
                    self.game_state = GameState.MENU
                    return True
        return True

    def handle_play_menu_events(self, event):
        if event.type == pygame.QUIT:
            return False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.game_state = GameState.MENU
                return True
            elif event.key == pygame.K_f:
                self.toggle_fullscreen()
            elif event.key == pygame.K_s:
                self.toggle_fullscreen(force_windowed=True)
        
        if self.play_vs_friend_button.handle_event(event):
            self.vs_ai = False
            self.current_player = 1  # Always start with player 1 in vs friend mode
            self.reset_board()
            self.game_state = GameState.PLAYING
            return True
        
        if self.play_vs_ai_button.handle_event(event):
            self.vs_ai = True
            self.ai_difficulty = self.ai_checkbox_list.options[self.ai_checkbox_list.selected_index]
            self.set_ai_difficulty(self.ai_difficulty)
            self.settings.update_setting('ai_difficulty', self.ai_difficulty)
            self.ai_starts = self.toggle_starter.selected_index == 1
            self.current_player = self.ai_piece if self.ai_starts else self.human_piece
            self.reset_board()
            self.game_state = GameState.PLAYING
            return True
        
        if self.go_back_playmenu.handle_event(event):
            self.game_state = GameState.MENU
            return True
        
        self.ai_checkbox_list.handle_event(event)
        self.toggle_starter.handle_event(event)
        return True

    def handle_menu_events(self, event):
        if event.type == pygame.QUIT:
            return False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                return False
            elif event.key == pygame.K_f:
                self.toggle_fullscreen()
            elif event.key == pygame.K_s:
                self.toggle_fullscreen(force_windowed=True)
        for button_name, button in self.menu_buttons.items():
            if button.handle_event(event):
                if button_name == 'play':
                    self.game_state = GameState.PLAY_MENU
                elif button_name == 'settings':
                    self.game_state = GameState.SETTINGS
                elif button_name == 'exit':
                    return False
        return True

    def update_animation(self):
        if self.animating:
            target_y = self.screen.get_height() - (self.board_y + self.anim_drop_row * SQUARE_SIZE + SQUARE_SIZE/2)
            if self.anim_drop_y < target_y:
                self.anim_drop_y += self.anim_speed
            else:
                self.animating = False
                # # After animation completes, switch turns if needed
                # if self.vs_ai and self.current_player == self.human_piece:
                #     self.current_player = self.ai_piece
                #     logging.debug(f"Animation complete. Switching to AI turn. Current player: {self.current_player}")

    def handle_playing_events(self, event):
        if self.show_end_popup:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if self.end_popup_button.handle_event(event):
                    self.game_state = GameState.MENU
                    return True
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self.game_state = GameState.MENU
                return True
            return True

        if event.type == pygame.QUIT:
            return False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.game_state = GameState.MENU
                return True
            elif event.key == pygame.K_f:
                self.toggle_fullscreen()
            elif event.key == pygame.K_s:
                self.toggle_fullscreen(force_windowed=True)

        # Only process human moves if it's human's turn
        if event.type == pygame.MOUSEBUTTONDOWN and not self.game_over and not self.animating:
            if self.vs_ai and self.current_player != self.human_piece:
                logging.debug(f"Ignoring human click - AI's turn. Current player: {self.current_player}")
                return True

            mouse_x = event.pos[0]
            for c in range(BOARD_COLS):
                if self.board_x + c*SQUARE_SIZE <= mouse_x <= self.board_x + (c+1)*SQUARE_SIZE and self.board[BOARD_ROWS-1][c] == 0:
                    row = self.get_next_open_row(self.board, c)
                    self.animate_drop(c, row, self.current_player)
                    self.board[row][c] = self.current_player
                    self.play_drop_sfx()

                    if self.check_win(self.current_player):
                        self.winner = self.current_player
                        self.game_over = True
                        self.show_end_popup = True
                    elif self.check_draw():
                        self.draw = True
                        self.game_over = True
                        self.show_end_popup = True

                    # FIXED: Proper turn switching logic
                    if not self.game_over:
                        if self.vs_ai:
                            # For AI mode, switch to AI turn immediately
                            self.current_player = self.ai_piece
                        else:
                            # For PvP, switch to other player
                            self.current_player = 3 - self.current_player
                    break
        return True

    def make_ai_move(self):
        if not self.vs_ai or self.current_player != self.ai_piece or self.game_over or self.animating:
            return

        # AI thinking time
        pygame.time.wait(int(self.settings.get_ai_thinking_time() * 1000))
        ai_col = self.ai_player.get_move(self.board.copy(), self.ai_piece)

        if self.is_valid_location(self.board, ai_col):
            row = self.get_next_open_row(self.board, ai_col)
            self.animate_drop(ai_col, row, self.ai_piece)
            self.board[row][ai_col] = self.ai_piece
            self.play_drop_sfx()

            if self.check_win(self.ai_piece):
                self.winner = self.ai_piece
                self.game_over = True
                self.show_end_popup = True
            elif self.check_draw():
                self.draw = True
                self.game_over = True
                self.show_end_popup = True

            # FIX: Switch back to human player after AI move
            if not self.game_over:
                self.current_player = self.human_piece
                logging.debug(f"AI move completed. Switching to human turn. Current player: {self.current_player}")

    def reset_board(self):
        self.board = np.zeros((BOARD_ROWS, BOARD_COLS))
        self.game_over = False
        self.winner = None
        self.draw = False
        self.show_end_popup = False
        self.winning_coords = []
        self.animating = False
        self.anim_drop_row = None
        self.anim_drop_col = None
        self.anim_drop_piece = None
        self.anim_drop_y = None

    def set_ai_difficulty(self, difficulty):
        self.ai_difficulty = difficulty
        self.ai_player = AI(difficulty)

    def check_win(self, piece):
        # Horizontal
        for c in range(BOARD_COLS-3):
            for r in range(BOARD_ROWS):
                if all(self.board[r][c+i] == piece for i in range(4)):
                    self.winning_coords = [(r, c+i) for i in range(4)]
                    return True
        # Vertical
        for c in range(BOARD_COLS):
            for r in range(BOARD_ROWS-3):
                if all(self.board[r+i][c] == piece for i in range(4)):
                    self.winning_coords = [(r+i, c) for i in range(4)]
                    return True
        # Positive diagonal
        for c in range(BOARD_COLS-3):
            for r in range(BOARD_ROWS-3):
                if all(self.board[r+i][c+i] == piece for i in range(4)):
                    self.winning_coords = [(r+i, c+i) for i in range(4)]
                    return True
        # Negative diagonal
        for c in range(BOARD_COLS-3):
            for r in range(3, BOARD_ROWS):
                if all(self.board[r-i][c+i] == piece for i in range(4)):
                    self.winning_coords = [(r-i, c+i) for i in range(4)]
                    return True
        return False

    def check_draw(self):
        return np.all(self.board != 0)

    def animate_drop(self, col, row, piece):
        self.animating = True
        self.anim_drop_col = col
        self.anim_drop_row = row
        self.anim_drop_piece = piece
        start_y = 0
        end_y = self.screen.get_height() - (self.board_y + row*SQUARE_SIZE + SQUARE_SIZE/2)
        self.anim_drop_y = start_y

    def is_valid_location(self, board, col):
        return board[BOARD_ROWS-1][col] == 0

    def get_next_open_row(self, board, col):
        for r in range(BOARD_ROWS):
            if board[r][col] == 0:
                return r

    def run(self):
        try:
            logging.info("Starting game loop")
            running = True
            while running:
                self.update_animation()

                # Handle AI's turn - FIXED: removed redundant player switching
                if self.game_state == GameState.PLAYING:
                    if self.vs_ai and self.current_player == self.ai_piece and not self.game_over and not self.animating:
                        self.make_ai_move()

                for event in pygame.event.get():
                    if self.game_state == GameState.MENU:
                        running = self.handle_menu_events(event)
                    elif self.game_state == GameState.SETTINGS:
                        running = self.handle_settings_events(event)
                    elif self.game_state == GameState.PLAY_MENU:
                        running = self.handle_play_menu_events(event)
                    elif self.game_state == GameState.PLAYING:
                        running = self.handle_playing_events(event)

                # Draw the current state
                if self.game_state == GameState.MENU:
                    self.draw_menu()
                elif self.game_state == GameState.SETTINGS:
                    self.draw_settings()
                elif self.game_state == GameState.PLAY_MENU:
                    self.draw_play_menu()
                elif self.game_state == GameState.PLAYING:
                    self.draw_board()

                self.clock.tick(60)

            logging.info("Game loop ended, cleaning up")
            pygame.quit()
            sys.exit(0)
        except Exception as e:
            logging.error(f"Error in game loop: {e}")
            pygame.quit()
            sys.exit(1)

if __name__ == "__main__":
    try:
        logging.info("Starting ConnectX game")
        game = Game()
        game.run()
    except Exception as e:
        logging.error(f"Fatal error: {e}")
        pygame.quit()
        sys.exit(1)