from tkinter import *
import random

# Constants
GAME_WIDTH = 600
GAME_HEIGHT = 600
SPACE_SIZE = 20
BODY_PARTS = 3
SNAKE_COLOR = "green"
FOOD_COLOR = "red"
BG_COLOR = "black"
WALL_COLOR = "#8B4513"  # Dark green for wall

# Globals
score = 0
direction = 'down'
direction_changed = False  # Prevent multiple direction changes in one move
snake = None
food = None
SPEED = 250  # default speed (Easy)
score_text = None  # To hold the canvas text id for score display

window = Tk()
window.title("Snake Game")
window.resizable(False, False)

canvas = Canvas(window, width=GAME_WIDTH, height=GAME_HEIGHT, bg=BG_COLOR)
canvas.pack()

# -------- Rounded Button helper --------
class RoundedButton(Canvas):
    def __init__(self, parent, width, height, cornerradius, padding, bg, fg, font, text, command=None):
        Canvas.__init__(self, parent, borderwidth=0, relief="flat", highlightthickness=0, bg=BG_COLOR)
        self.command = command
        self.width = width
        self.height = height
        self.cornerradius = cornerradius
        self.padding = padding
        self.bg = bg
        self.fg = fg
        self.font = font
        self.text = text
        self.configure(width=width, height=height)

        self.draw_rounded_rect()
        self.text_id = self.create_text(width // 2, height // 2, text=text, fill=fg, font=font)

        self.bind("<ButtonPress-1>", self._on_press)
        self.bind("<ButtonRelease-1>", self._on_release)

    def draw_rounded_rect(self):
        radius = self.cornerradius
        w = self.width
        h = self.height
        p = self.padding
        bg = self.bg
        # Clear previous shapes
        self.delete("round_rect")
        # Draw four arcs for corners
        self.create_arc((p, p, p + 2*radius, p + 2*radius), start=90, extent=90, fill=bg, outline=bg, tags="round_rect")
        self.create_arc((w - p - 2*radius, p, w - p, p + 2*radius), start=0, extent=90, fill=bg, outline=bg, tags="round_rect")
        self.create_arc((p, h - p - 2*radius, p + 2*radius, h - p), start=180, extent=90, fill=bg, outline=bg, tags="round_rect")
        self.create_arc((w - p - 2*radius, h - p - 2*radius, w - p, h - p), start=270, extent=90, fill=bg, outline=bg, tags="round_rect")
        # Draw rectangles to fill edges
        self.create_rectangle(p + radius, p, w - p - radius, h - p, fill=bg, outline=bg, tags="round_rect")
        self.create_rectangle(p, p + radius, w - p, h - p - radius, fill=bg, outline=bg, tags="round_rect")

    def _on_press(self, event):
        self.itemconfig("round_rect", fill=self._darker_color(self.bg))
        self.itemconfig(self.text_id, fill="white")

    def _on_release(self, event):
        self.itemconfig("round_rect", fill=self.bg)
        self.itemconfig(self.text_id, fill=self.fg)
        if self.command:
            self.command()

    def _darker_color(self, color):
        color = color.lstrip("#")
        lv = len(color)
        rgb = tuple(int(color[i:i + lv // 3], 16) for i in range(0, lv, lv // 3))
        dark_rgb = tuple(max(0, int(c * 0.8)) for c in rgb)
        return "#" + "".join(f"{c:02x}" for c in dark_rgb)


class Snake:
    def __init__(self):
        self.body_size = BODY_PARTS
        self.coordinates = []
        self.squares = []
        # Start snake centered and inside the walls
        start_x = GAME_WIDTH // 2 // SPACE_SIZE * SPACE_SIZE
        start_y = GAME_HEIGHT // 2 // SPACE_SIZE * SPACE_SIZE
        for i in range(BODY_PARTS):
            # Position body parts horizontally leftwards
            self.coordinates.append((start_x - i*SPACE_SIZE, start_y))
        for x, y in self.coordinates:
            square = canvas.create_rectangle(
                x, y, x + SPACE_SIZE, y + SPACE_SIZE,
                fill=SNAKE_COLOR, tag="snake"
            )
            self.squares.append(square)


class Food:
    def __init__(self):
        max_x = (GAME_WIDTH // SPACE_SIZE) - 2
        max_y = (GAME_HEIGHT // SPACE_SIZE) - 2
        x = random.randint(1, max_x) * SPACE_SIZE
        y = random.randint(1, max_y) * SPACE_SIZE
        self.coordinates = (x, y)
        canvas.create_oval(
            x, y, x + SPACE_SIZE, y + SPACE_SIZE,
            fill=FOOD_COLOR, tag="food"
        )

# *** Updated draw_walls with brick style ***
def draw_walls():
    # Draw top wall bricks
    for i in range(GAME_WIDTH // SPACE_SIZE):
        x = i * SPACE_SIZE
        y = 0
        canvas.create_rectangle(
            x, y, x + SPACE_SIZE, y + SPACE_SIZE,
            fill=WALL_COLOR, outline="black"
        )

    # Draw bottom wall bricks
    for i in range(GAME_WIDTH // SPACE_SIZE):
        x = i * SPACE_SIZE
        y = GAME_HEIGHT - SPACE_SIZE
        canvas.create_rectangle(
            x, y, x + SPACE_SIZE, y + SPACE_SIZE,
            fill=WALL_COLOR, outline="black"
        )

    # Draw left wall bricks
    for i in range(GAME_HEIGHT // SPACE_SIZE):
        x = 0
        y = i * SPACE_SIZE
        canvas.create_rectangle(
            x, y, x + SPACE_SIZE, y + SPACE_SIZE,
            fill=WALL_COLOR, outline="black"
        )

    # Draw right wall bricks
    for i in range(GAME_HEIGHT // SPACE_SIZE):
        x = GAME_WIDTH - SPACE_SIZE
        y = i * SPACE_SIZE
        canvas.create_rectangle(
            x, y, x + SPACE_SIZE, y + SPACE_SIZE,
            fill=WALL_COLOR, outline="black"
        )

def start_menu():
    canvas.delete("all")

    lime_green = "#32CD32"  # vibrant lime green
    orange_brown = "#D2691E"  # warm orange-brown (terracotta-like)
    button_bg = "#FFA500"
    button_fg = "white"
    button_font = ("Comic Sans MS", 16, "bold")

    canvas.create_text(
        GAME_WIDTH // 2, GAME_HEIGHT // 2 - 80,
        text="Snake",
        fill=lime_green,
        font=("Comic Sans MS", 60, "bold")
    )
    canvas.create_text(
        GAME_WIDTH // 2, GAME_HEIGHT // 2,
        text="Game",
        fill=orange_brown,
        font=("Comic Sans MS", 60, "bold")
    )

    btn_width = 120
    btn_height = 45
    spacing = 20

    total_width = btn_width * 2 + spacing
    start_x = (GAME_WIDTH - total_width) // 2
    y_pos = GAME_HEIGHT // 2 + 70

    start_btn = RoundedButton(window, btn_width, btn_height, cornerradius=15, padding=2,
                              bg=button_bg, fg=button_fg, font=button_font, text="Start Game",
                              command=start_game)
    quit_btn = RoundedButton(window, btn_width, btn_height, cornerradius=15, padding=2,
                             bg=button_bg, fg=button_fg, font=button_font, text="Quit",
                             command=window.destroy)
    settings_btn = RoundedButton(window, 110, 35, cornerradius=15, padding=2,
                                bg=button_bg, fg=button_fg, font=button_font, text="Settings",
                                command=level_menu)

    canvas.create_window(start_x + btn_width // 2, y_pos, window=start_btn)
    canvas.create_window(start_x + btn_width + spacing + btn_width // 2, y_pos, window=quit_btn)
    canvas.create_window(GAME_WIDTH - 70, 40, window=settings_btn)


def level_menu():
    canvas.delete("all")
    canvas.create_text(
        GAME_WIDTH // 2,
        GAME_HEIGHT // 2 - 100,
        text="Select Difficulty Level",
        fill="white",
        font=('Comic Sans MS', 30, 'bold')
    )
    canvas.create_window(
        GAME_WIDTH // 2,
        GAME_HEIGHT // 2 - 30,
        window=RoundedButton(window, 140, 40, 15, 2, "#FFA500", "white", ("Comic Sans MS", 16, "bold"),
                             "Easy", lambda: set_level('easy'))
    )
    canvas.create_window(
        GAME_WIDTH // 2,
        GAME_HEIGHT // 2 + 30,
        window=RoundedButton(window, 140, 40, 15, 2, "#FFA500", "white", ("Comic Sans MS", 16, "bold"),
                             "Medium", lambda: set_level('medium'))
    )
    canvas.create_window(
        GAME_WIDTH // 2,
        GAME_HEIGHT // 2 + 90,
        window=RoundedButton(window, 140, 40, 15, 2, "#FFA500", "white", ("Comic Sans MS", 16, "bold"),
                             "Hard", lambda: set_level('hard'))
    )
    canvas.create_window(
        GAME_WIDTH // 2,
        GAME_HEIGHT // 2 + 150,
        window=RoundedButton(window, 100, 35, 15, 2, "#FFA500", "white", ("Comic Sans MS", 12, "bold"),
                             "Back", start_menu)
    )


def set_level(level):
    global SPEED
    if level == 'easy':
        SPEED = 250
    elif level == 'medium':
        SPEED = 120
    elif level == 'hard':
        SPEED = 70
    start_menu()


def start_game():
    global score, direction, snake, food, score_text, direction_changed
    score = 0
    direction = 'down'
    direction_changed = False
    canvas.delete("all")
    draw_walls()
    snake = Snake()
    food = Food()
    score_text = canvas.create_text(
        GAME_WIDTH // 2, 20,
        text=f"Score: {score}",
        fill="white",
        font=('consolas', 20)
    )
    next_turn(snake)


def next_turn(snake_obj):
    global direction, score, food, score_text, direction_changed

    direction_changed = False

    x, y = snake_obj.coordinates[0]
    if direction == 'up':
        y -= SPACE_SIZE
    elif direction == 'down':
        y += SPACE_SIZE
    elif direction == 'left':
        x -= SPACE_SIZE
    elif direction == 'right':
        x += SPACE_SIZE

    snake_obj.coordinates.insert(0, (x, y))
    square = canvas.create_rectangle(
        x, y, x + SPACE_SIZE, y + SPACE_SIZE,
        fill=SNAKE_COLOR
    )
    snake_obj.squares.insert(0, square)

    if (x, y) == food.coordinates:
        score += 1
        canvas.itemconfigure(score_text, text=f"Score: {score}")
        canvas.delete("food")
        food = Food()
    else:
        del snake_obj.coordinates[-1]
        canvas.delete(snake_obj.squares[-1])
        del snake_obj.squares[-1]

    if check_collisions(snake_obj):
        game_over()
    else:
        window.after(SPEED, next_turn, snake_obj)


def change_direction(new_dir):
    global direction, direction_changed
    opposites = {'up': 'down', 'down': 'up', 'left': 'right', 'right': 'left'}
    if not direction_changed and new_dir != opposites.get(direction):
        direction = new_dir
        direction_changed = True


def check_collisions(snake_obj):
    x, y = snake_obj.coordinates[0]
    # Collision with walls (edges) is already checked by boundary conditions
    if x < SPACE_SIZE or x >= GAME_WIDTH - SPACE_SIZE or y < SPACE_SIZE or y >= GAME_HEIGHT - SPACE_SIZE:
        return True
    for part in snake_obj.coordinates[1:]:
        if (x, y) == part:
            return True
    return False


def game_over():
    canvas.delete("all")
    canvas.create_text(
        GAME_WIDTH // 2,
        GAME_HEIGHT // 2 - 60,
        text="GAME OVER",
        fill="red",
        font=('consolas', 40)
    )
    canvas.create_text(
        GAME_WIDTH // 2,
        GAME_HEIGHT // 2,
        text=f"YOUR SCORE: {score}",
        fill="white",
        font=('consolas', 30)
    )
    canvas.create_window(
        GAME_WIDTH // 2 - 70,
        GAME_HEIGHT // 2 + 60,
        window=RoundedButton(window, 120, 45, 15, 2, "#FFA500", "white", ("Comic Sans MS", 16, "bold"),
                             "Restart", restart_game)
    )
    canvas.create_window(
        GAME_WIDTH // 2 + 70,
        GAME_HEIGHT // 2 + 60,
        window=RoundedButton(window, 120, 45, 15, 2, "#FFA500", "white", ("Comic Sans MS", 16, "bold"),
                             "Menu", back_to_menu)
    )
    window.bind('<Return>', lambda event: restart_game())


def restart_game():
    window.unbind('<Return>')
    global score, direction, snake, food, score_text, direction_changed
    score = 0
    direction = 'down'
    direction_changed = False
    canvas.delete("all")
    draw_walls()
    snake = Snake()
    food = Food()
    score_text = canvas.create_text(
        GAME_WIDTH // 2, 20,
        text=f"Score: {score}",
        fill="white",
        font=('consolas', 20)
    )
    next_turn(snake)


def back_to_menu():
    window.unbind('<Return>')
    start_menu()


# Center window on screen
window.update()
screen_width = window.winfo_screenwidth()
screen_height = window.winfo_screenheight()
x = (screen_width // 2) - (GAME_WIDTH // 2)
y = (screen_height // 2) - (GAME_HEIGHT // 2)
window.geometry(f"{GAME_WIDTH}x{GAME_HEIGHT + 60}+{x}+{y}")

# Key bindings
window.bind('<Left>', lambda event: change_direction('left'))
window.bind('<Right>', lambda event: change_direction('right'))
window.bind('<Up>', lambda event: change_direction('up'))
window.bind('<Down>', lambda event: change_direction('down'))

# Show start menu initially
start_menu()

window.mainloop()
