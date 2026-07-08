"""
Configuration constants for Hand Gesture Controlled Tic-Tac-Toe.
"""

# Window settings
WINDOW_NAME = "Hand Gesture Controlled Tic-Tac-Toe"
WIDTH = 1280
HEIGHT = 720

# Colors (BGR format for OpenCV)
COLOR_BG = (18, 18, 18)          # Deep dark grey/black
COLOR_GRID = (80, 80, 80)        # Mid grey
COLOR_TEXT = (240, 240, 240)      # Near white
COLOR_X = (80, 80, 255)          # Soft red/coral (B, G, R)
COLOR_O = (255, 180, 80)         # Soft sky blue (B, G, R)
COLOR_HOVER = (200, 200, 200)    # Soft white for hover indicators
COLOR_CURSOR = (0, 255, 0)       # Vibrant green for hand tracking pointer
COLOR_SELECTION = (0, 255, 255)  # Cyan for active choice feedback

# Game Layout (3x3 grid dimensions)
BOARD_SIZE = 450                 # Size of the square board
BOARD_X_START = (WIDTH - BOARD_SIZE) // 2
BOARD_Y_START = (HEIGHT - BOARD_SIZE) // 2
CELL_SIZE = BOARD_SIZE // 3

# Gesture & Interaction Settings
PINCH_THRESHOLD = 30             # Pixel distance between index and thumb to trigger a click
CLICK_COOLDOWN = 1.0             # Minimum seconds between successive selections
SMOOTHING_FACTOR = 0.3           # Exponential Moving Average weight (lower = smoother, higher = faster)


# Game States
STATE_MENU = "MENU"
STATE_GAME = "GAME"

# Game Over Delay
GAME_OVER_DELAY = 2.5            # Delay in seconds before showing game over overlay

# Welcome Screen Buttons
# Format: [x_min, y_min, x_max, y_max]
BTN_PLAY_AI_RECT = [150, 240, 550, 310]
BTN_PLAY_FRIEND_RECT = [150, 340, 550, 410]
BTN_DIFFICULTY_RECT = [150, 440, 550, 510]

BTN_P1_NAME_RECT = [730, 240, 1130, 310]
BTN_P2_NAME_RECT = [730, 340, 1130, 410]

BTN_EXIT_RECT = [440, 560, 840, 630]

# UI Colors (BGR format)
COLOR_BTN_BG = (30, 30, 30)
COLOR_BTN_HOVER = (50, 150, 50)     # Vibrant green highlight for Start Game hover
COLOR_BTN_EXIT_HOVER = (50, 50, 180) # Vibrant red highlight for Exit hover
COLOR_BTN_BORDER = (80, 80, 80)
COLOR_BTN_TEXT = (240, 240, 240)

# Game Over Screen Buttons
# Format: [x_min, y_min, x_max, y_max]
BTN_PLAY_RECT = [420, 400, 620, 460]
BTN_MENU_RECT = [660, 400, 860, 460]

# Win Line Color (Gold)
COLOR_WIN_LINE = (0, 215, 255)


