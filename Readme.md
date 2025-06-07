# ConnectX: Intelligent Connect Four

## Overview

A Python-based Connect Four game featuring dynamic AI opponents, customizable settings, and multiplayer functionality. Built with Pygame for graphics and sound.

## Quick Start

### Prerequisites

- Python 3.12 or higher
- pip (Python package installer)

### Installation and Running

#### Windows Users

1. Double-click the `launch.bat` file
   - This will automatically install required packages and start the game
   - If you get a security warning, click "Run anyway"

#### Manual Installation (Alternative Method)

1. Open a terminal/command prompt
2. Navigate to the game directory
3. Install required packages:

```bash
pip install -r requirements.txt
```

4. Start the game:

```bash
python main.py
```

### Troubleshooting

If you encounter any issues:

  1. Make sure Python 3.12 or higher is installed
  2. Try running the commands manually in a terminal
  3. If you get a "pygame module not found" error, run:

  ```bash
  pip install pygame numpy
  ```

## 1. Game Structure

### Main Menu

- Background: Subtle animated grid with floating discs
- Buttons (Centered, modern UI):
  - PLAY → Opens Play Submenu
  - SETTINGS → Opens Settings Menu
  - EXIT → Closes game

### Play Submenu

- Options:
  - PLAY VS AI → Opens AI Difficulty Selector
  - PLAY VS FRIEND → Starts 2-player game
  - GO BACK → Returns to Main Menu

### AI Difficulty Selector (Dropdown)

- Options:
  - EASY → Random moves
  - MEDIUM → Blocks wins/seeks immediate wins
  - HARD → Minimax algorithm (depth=5)

- Starter Selector after difficulty choice:
  - HUMAN STARTS / AI STARTS buttons

### Settings Menu

- Sliders:
  - Music Volume (0-100%): Controls background music
  - SFX Volume (0-100%): Controls disc drops/win sounds

- Color Selection:
  - Grid of 10 color swatches (RGB values predefined)
  - Each color square is a checkbox to selected colors
  - Preview: "Player 1" and "Player 2" text in chosen colors

- GO BACK button

## 2. Gameplay Mechanics

### Board

- Grid: 6 rows × 7 columns (standard Connect Four)
- Discs: Rendered as circles with player colors

### Game Flow

- Player Turn:
  - Click column to drop disc (SFX plays)
  - Disc animates falling to lowest empty row

- AI Turn (if applicable):
  - Difficulty-based move calculation
  - 1-second "thinking" delay for realism

- Win Detection:
  - Horizontal/vertical/diagonal 4-in-a-row
  - Winning Animation: Blinking discs (brightness pulse)
  - Win SFX: Triumphant chime

### End Game

- Popup Modal:
  - "Player X Wins!" / "AI Wins!" in winner's color
  - MAIN MENU button

## 3. AI Implementation

Difficulty Logic:

- EASY:

    ```python
    def ai_move_easy(board):
        return random.choice(get_valid_columns(board))
    ```

- MEDIUM:

    ```python
    def ai_move_medium(board, player):
        if can_win_next_move(board, AI_PIECE): return winning_col  # Win if possible
        if can_win_next_move(board, HUMAN_PIECE): return blocking_col  # Block human
        return random.choice(valid_cols)
    ```

- HARD (Minimax):

    ```python
    def minimax(board, depth, alpha, beta, maximizing):
        # Evaluate board at terminal state/depth limit
        if depth == 0 or game_over: return evaluate_board(board)
        # ... (recursive scoring of moves)
        return optimal_column
    ```

## 4. Technical Specifications

Dependencies:

```bash
$ python --version
Python 3.12.10

Required packages:
- pygame==2.5.2
- numpy==1.26.4
```

## 5. Key Features

- Easy Installation: Simple setup with Python
- Responsive UI: Animated menus, hover effects
- SFX/Music: Dynamic volume control
- Color Persistence: Remembers player colors
- AI Transparency: Console logs AI decision steps (toggleable)

## 6. Visual Design

- Color Palette: Dark blue background (#0d1b2a) with neon disc colors
- Font: Comic Sans MS (clean and readable)
- Animations:
  - Disc drop gravity simulation
  - Menu transitions (slide effects)
  - Winning discs: 3x brightness pulse
