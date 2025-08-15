import pygame
import sys
import random
import json
from pathlib import Path
from typing import Tuple, List, Dict

# -----------------------------
# Configuration
# -----------------------------
SCREEN_WIDTH = 500
SCREEN_HEIGHT = 720
GRID_SIZE = 20
GRID_WIDTH = SCREEN_WIDTH // GRID_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // GRID_SIZE

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
DARK_GRAY = (30, 30, 30)
GRAY = (100, 100, 100)
GREEN = (28, 200, 120)
DARK_GREEN = (10, 120, 70)
RED = (230, 60, 60)
YELLOW = (245, 210, 40)
BLUE = (40, 130, 255)
CHARCOAL = (54, 69, 79)
LIGHT_GREEN = (144, 238, 144)
MAGENTA = (255, 0, 200)
CYAN = (0, 220, 220)

# Game settings
INITIAL_SPEED = 8
SPEED_INCREMENT = 0.5
HIGHSCORE_FILE = Path("highscore.json")


# -----------------------------
# Helper classes & functions
# -----------------------------
class Button:
    def __init__(self, rect: pygame.Rect, text: str, font: pygame.font.Font,
                 fg=WHITE, bg=BLUE, hover_bg=YELLOW):
        self.rect = rect
        self.text = text
        self.font = font
        self.fg = fg
        self.bg = bg
        self.hover_bg = hover_bg

    def draw(self, surface: pygame.Surface):
        mouse = pygame.mouse.get_pos()
        is_hover = self.rect.collidepoint(mouse)
        color = self.hover_bg if is_hover else self.bg
        pygame.draw.rect(surface, color, self.rect, border_radius=10)
        pygame.draw.rect(surface, DARK_GRAY, self.rect, 2, border_radius=10)
        txt = self.font.render(self.text, True, BLACK if is_hover else self.fg)
        txt_rect = txt.get_rect(center=self.rect.center)
        surface.blit(txt, txt_rect)

    def is_clicked(self, event: pygame.event.Event) -> bool:
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                return True
        return False


def grid_to_pixels(pos: Tuple[int, int]) -> Tuple[int, int]:
    x, y = pos
    return x * GRID_SIZE, y * GRID_SIZE


def random_empty_cell(exclude: List[Tuple[int, int]]) -> Tuple[int, int]:
    while True:
        pos = (random.randint(0, GRID_WIDTH - 1), random.randint(0, GRID_HEIGHT - 1))
        if pos not in exclude:
            return pos

# -----------------------------
# Core game class
# -----------------------------
class SnakeGame:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Snake Game - Pygame")
        self.fullscreen = False
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.clock = pygame.time.Clock()

        # Fonts (swap title_font to any custom TTF if you like)
        self.title_font = pygame.font.SysFont("arialblack", 72)
        self.large_font = pygame.font.SysFont("segoeui", 32, bold=True)
        self.font = pygame.font.SysFont("segoeui", 22)
        self.small_font = pygame.font.SysFont("segoeui", 16)

        # Themes
        self.themes: Dict[str, Dict[str, Tuple[int, int, int]]] = {
            "Retro": {
                "snake_head": DARK_GREEN,
                "snake_body": GREEN,
                "food": RED,
                "grid": (20, 20, 20),
                "play_bg": (12, 12, 12),
                "title": GREEN,
            },
            "Minimal": {
                "snake_head": (220, 220, 220),
                "snake_body": (180, 180, 180),
                "food": (255, 120, 120),
                "grid": (28, 28, 28),
                "play_bg": (14, 14, 14),
                "title": WHITE,
            },
            "Neon": {
                "snake_head": (180, 255, 200),
                "snake_body": (80, 255, 180),
                "food": MAGENTA,
                "grid": (35, 35, 60),
                "play_bg": (8, 8, 16),
                "title": CYAN,
            },
        }
        self.theme_name = "Retro"

        # Menu buttons
        btn_w, btn_h = 240, 56
        center_x = SCREEN_WIDTH // 2
        y = 300
        self.start_btn = Button(pygame.Rect(center_x - btn_w // 2, y, btn_w, btn_h), "Start Game", self.large_font, fg=BLACK, bg=YELLOW, hover_bg=(200, 200, 200))
        y += 70
        self.mode_btn = Button(pygame.Rect(center_x - btn_w // 2, y, btn_w, btn_h), "Adventure", self.large_font, fg=BLACK, bg=YELLOW, hover_bg=(200, 200, 200))
        y += 70
        self.theme_btn = Button(pygame.Rect(center_x - btn_w // 2, y, btn_w, btn_h), "Retro", self.large_font, fg=BLACK, bg=YELLOW, hover_bg=(200, 200, 200))
        y += 70
        self.quit_btn = Button(pygame.Rect(center_x - btn_w // 2, y, btn_w, btn_h), "Quit", self.large_font, fg=WHITE, bg=RED, hover_bg=(255, 140, 140))

        # Score screen buttons
        self.restart_btn = Button(pygame.Rect(center_x - btn_w // 2, 360, btn_w, btn_h), "Restart", self.large_font, fg=BLACK, bg=YELLOW, hover_bg=(255, 230, 120))
        self.menu_btn = Button(pygame.Rect(center_x - btn_w // 2, 430, btn_w, btn_h), "Main Menu", self.large_font,bg=GRAY, hover_bg=(200, 200, 200))

        # Game state & options
        self.state = 'menu'  # 'menu', 'playing', 'score'
        self.mode = 'Adventure'  # or 'Adventure'

        # High score cache
        self.highscores = self.load_highscores()

        # Game variables
        self.reset_game()

    # ------------------------
    # High scores
    # ------------------------
    def load_highscores(self) -> Dict[str, int]:
        if HIGHSCORE_FILE.exists():
            try:
                return json.loads(HIGHSCORE_FILE.read_text())
            except Exception:
                return {}
        return {}

    def save_highscores(self):
        try:
            HIGHSCORE_FILE.write_text(json.dumps(self.highscores, indent=2))
        except Exception:
            pass

    def get_highscore(self) -> int:
        return int(self.highscores.get(self.mode, 0))

    def maybe_set_highscore(self):
        if self.score > self.get_highscore():
            self.highscores[self.mode] = self.score
            self.save_highscores()
            return True
        return False

    # ------------------------
    # Display mode
    # ------------------------
    def toggle_fullscreen(self):
        self.fullscreen = not self.fullscreen
        flags = pygame.FULLSCREEN if self.fullscreen else 0
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), flags)

    # ------------------------
    # Game lifecycle
    # ------------------------
    def reset_game(self):
        # Snake starts in the center with length 4
        cx = GRID_WIDTH // 2
        cy = GRID_HEIGHT // 2
        self.snake = [(cx, cy), (cx - 1, cy), (cx - 2, cy), (cx - 3, cy)]
        self.direction = (1, 0)  # moving right
        self.next_direction = self.direction
        # Bricks/obstacles
        self.bricks: List[Tuple[int, int]] = []
        # Place initial food
        occupied = set(self.snake)
        self.food = random_empty_cell(list(occupied))
        self.score = 0
        self.speed = INITIAL_SPEED
        self.alive = True
        self.MOVE_EVENT = pygame.USEREVENT + 1
        pygame.time.set_timer(self.MOVE_EVENT, int(1000 / self.speed))

    def set_speed_timer(self):
        pygame.time.set_timer(self.MOVE_EVENT, max(40, int(1000 / self.speed)))

    # ------------------------
    # Event handlers
    # ------------------------
    def handle_menu_events(self, event):
        if self.start_btn.is_clicked(event):
            self.reset_game()
            self.state = 'playing'
        if self.mode_btn.is_clicked(event):
            self.mode = 'Classic' if self.mode == 'Adventure' else 'Adventure'
            self.mode_btn.text = f"{self.mode}"
        if self.theme_btn.is_clicked(event):
            names = list(self.themes.keys())
            idx = names.index(self.theme_name)
            self.theme_name = names[(idx + 1) % len(names)]
            self.theme_btn.text = f"{self.theme_name}"
        if self.quit_btn.is_clicked(event):
            pygame.quit()
            sys.exit()

    def handle_score_events(self, event):
        if self.restart_btn.is_clicked(event):
            self.reset_game()
            self.state = 'playing'
        if self.menu_btn.is_clicked(event):
            self.state = 'menu'
        if self.quit_btn.is_clicked(event):
            pygame.quit()
            sys.exit()

    def handle_playing_events(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_UP, pygame.K_w) and self.direction != (0, 1):
                self.next_direction = (0, -1)
            elif event.key in (pygame.K_DOWN, pygame.K_s) and self.direction != (0, -1):
                self.next_direction = (0, 1)
            elif event.key in (pygame.K_LEFT, pygame.K_a) and self.direction != (1, 0):
                self.next_direction = (-1, 0)
            elif event.key in (pygame.K_RIGHT, pygame.K_d) and self.direction != (-1, 0):
                self.next_direction = (1, 0)
            elif event.key == pygame.K_ESCAPE:
                # quick go to menu
                self.state = 'menu'
            elif event.key == pygame.K_F11:
                self.toggle_fullscreen()
            elif event.key == pygame.K_g:
                # debug: force game over for preview/testing
                pygame.time.set_timer(self.MOVE_EVENT, 0)
                self.alive = False
                self.state = 'score'
        elif event.type == self.MOVE_EVENT and self.alive:
            self.move_snake()

    # ------------------------
    # Game mechanics
    # ------------------------
    def move_snake(self):
        self.direction = self.next_direction
        head_x, head_y = self.snake[0]
        dx, dy = self.direction
        new_head = (head_x + dx, head_y + dy)

        # Fix: The original code had the logic for Classic and Adventure modes swapped.
        if self.mode == 'Classic':
            # Adventure: Wrap-around
            new_head = (new_head[0] % GRID_WIDTH, new_head[1] % GRID_HEIGHT)
        else:  # self.mode == 'Classic'
            # Classic: Wall collision ends game
            if not (0 <= new_head[0] < GRID_WIDTH and 0 <= new_head[1] < GRID_HEIGHT):
                pygame.time.set_timer(self.MOVE_EVENT, 0)
                self.alive = False
                self.state = 'score'
                self.maybe_set_highscore()
                return

        # Check collision with self or bricks
        if new_head in self.snake or new_head in self.bricks:
            pygame.time.set_timer(self.MOVE_EVENT, 0)
            self.alive = False
            self.state = 'score'
            self.maybe_set_highscore()
            return

        # Move
        self.snake.insert(0, new_head)

        # Check food
        if new_head == self.food:
            self.score += 10
            # increase speed slightly every time you eat
            self.speed += SPEED_INCREMENT
            prev_food = self.food
            # new food at empty cell
            occupied = set(self.snake) | set(self.bricks)
            self.food = random_empty_cell(list(occupied))
            self.set_speed_timer()

            # Classic: spawn a new brick where the last food was
            if self.mode == 'Adventure':
                if prev_food not in self.snake and prev_food not in self.bricks:
                    self.bricks.append(prev_food)
        else:
            self.snake.pop()

    # ------------------------
    # Drawing
    # ------------------------
    def draw_grid(self, color):
        for x in range(0, SCREEN_WIDTH, GRID_SIZE):
            pygame.draw.line(self.screen, color, (x, 0), (x, SCREEN_HEIGHT))
        for y in range(0, SCREEN_HEIGHT, GRID_SIZE):
            pygame.draw.line(self.screen, color, (0, y), (SCREEN_WIDTH, y))

    def draw_snake(self, head_color, body_color):
        for i, seg in enumerate(self.snake):
            px, py = grid_to_pixels(seg)
            rect = pygame.Rect(px + 1, py + 1, GRID_SIZE - 2, GRID_SIZE - 2)
            if i == 0:
                pygame.draw.rect(self.screen, head_color, rect, border_radius=6)
            else:
                pygame.draw.rect(self.screen, body_color, rect, border_radius=6)

    def draw_food(self, color):
        px, py = grid_to_pixels(self.food)
        rect = pygame.Rect(px + 4, py + 4, GRID_SIZE - 8, GRID_SIZE - 8)
        pygame.draw.ellipse(self.screen, color, rect)

    def draw_bricks(self):
        for cell in self.bricks:
            px, py = grid_to_pixels(cell)
            rect = pygame.Rect(px + 1, py + 1, GRID_SIZE - 2, GRID_SIZE - 2)
            pygame.draw.rect(self.screen, (90, 90, 110), rect, border_radius=4)

    def draw_score(self):
        score_surf = self.font.render(f"Score: {self.score}", True, WHITE)
        self.screen.blit(score_surf, (10, 10))
        hs = self.get_highscore()
        hs_surf = self.small_font.render(f"High: {hs}", True, WHITE)
        self.screen.blit(hs_surf, (10, 34))

    def draw_speed(self):
        sp_surf = self.small_font.render(f"Speed: {self.speed:.1f}", True, WHITE)
        self.screen.blit(sp_surf, (10, 56))

    # ------------------------
    # Screens
    # ------------------------
    def render_menu(self):
        theme = self.themes[self.theme_name]
        self.screen.fill(CHARCOAL)
        title = self.title_font.render("S N A K E", True, theme["title"])
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, 160))
        self.screen.blit(title, title_rect)

        # draw buttons
        self.start_btn.draw(self.screen)
        self.mode_btn.draw(self.screen)
        self.theme_btn.draw(self.screen)
        self.quit_btn.draw(self.screen)

    def render_playing(self):
        theme = self.themes[self.theme_name]
        # background
        self.screen.fill(theme["play_bg"])

        # grid & elements
        self.draw_grid(theme["grid"])
        self.draw_bricks()
        self.draw_food(theme["food"])
        self.draw_snake(theme["snake_head"], theme["snake_body"])

        # HUD
        self.draw_score()
        self.draw_speed()

    def render_score(self):
        theme = self.themes[self.theme_name]
        self.screen.fill(CHARCOAL)
        title = self.title_font.render("Game Over", True, RED)
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, 140))
        self.screen.blit(title, title_rect)

        score_txt = self.large_font.render(f"Your Score: {self.score}", True, WHITE)
        score_rect = score_txt.get_rect(center=(SCREEN_WIDTH // 2, 230))
        self.screen.blit(score_txt, score_rect)

        new_record = self.maybe_set_highscore()
        high_txt = self.font.render(
            f"High Score ({self.mode}): {self.get_highscore()}" + ("  NEW!" if new_record else ""), True,
            LIGHT_GREEN if new_record else WHITE)
        high_rect = high_txt.get_rect(center=(SCREEN_WIDTH // 2, 270))
        self.screen.blit(high_txt, high_rect)

        # buttons
        self.restart_btn.draw(self.screen)
        self.menu_btn.draw(self.screen)
    # ------------------------
    # Main loop
    # ------------------------
    def run(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                if self.state == 'menu':
                    self.handle_menu_events(event)
                elif self.state == 'playing':
                    self.handle_playing_events(event)
                elif self.state == 'score':
                    self.handle_score_events(event)

            # Render
            if self.state == 'menu':
                self.render_menu()
            elif self.state == 'playing':
                self.render_playing()
            elif self.state == 'score':
                self.render_score()

            pygame.display.flip()
            self.clock.tick(60)


if __name__ == '__main__':
    game = SnakeGame()
    game.run()