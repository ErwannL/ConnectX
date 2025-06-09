# ConnectX: Intelligent Connect Four

## Overview

A Python-based Connect Four game featuring dynamic AI opponents, customizable settings, and multiplayer functionality. Built with Pygame for graphics and sound.

## Features

- Play against a friend or AI
- Three AI difficulty levels (Easy, Medium, Hard)
- Customizable player colors
- Adjustable music and sound effects
- Fullscreen/windowed mode
- AI thinking logs for Hard difficulty
- AI training system
- Pre-trained model support
- Development mode with AI visualization
- Smooth animations
- Modern UI with hover effects

## Installation

1. Clone the repository
2. Install the required packages:

```bash
pip install -r requirements.txt
```

## Running the Game

To start the game:

```bash
./launch.sh
```

### Using a Trained Model

To play against a trained model:

```bash
./launch.sh model models/path/to/model.pkl
```

### Training a New Model

To train a new AI model:

```bash
./launch.sh train [depth]
```

Where `depth` is an optional parameter specifying the search depth (default: 3).

The training process will:

1. Generate all possible board positions
2. Calculate the best moves for each position
3. Save the model to the `models` directory
4. Create training logs in the `training_ai` directory

## Game Controls

- Left-click to drop a piece
- ESC to toggle fullscreen
- D to toggle development mode (shows AI thinking process)
- R to restart the game
- M to return to main menu

## AI Difficulty Levels

- **Easy**: Makes random valid moves
- **Medium**: Looks for winning moves and blocks opponent's winning moves
- **Hard**: Uses minimax algorithm with alpha-beta pruning to find the best move

## Development Mode

Press 'D' to toggle development mode, which shows:

- AI's current calculation board
- Move evaluations
- Best move selection process

## Project Structure

- `main.py`: Main game logic and UI
- `ai.py`: AI implementation with different difficulty levels
- `in_game_ai.md`: Technical documentation for the in-game AI
- `train_ai.py`: AI training system
- `AI_Training_Technical.md`: Technical documentation for AI training and models
- `models/`: Directory for saved AI models
- `training_ai/`: Directory for training logs
- `ai_logs/`: Directory for AI thinking logs during gameplay

## Requirements

- Python 3.6+
- Pygame
- NumPy
- tqdm (for training progress)

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## 1. Game Structure

### Main Menu

- Background: Dark blue theme with modern UI
- Buttons (Centered, modern UI):
  - PLAY → Opens Play Submenu
  - SETTINGS → Opens Settings Menu
  - EXIT → Closes game

### Play Submenu

- Options:
  - PLAY VS AI → Opens AI Difficulty Selector
  - PLAY VS FRIEND → Starts 2-player game
  - GO BACK → Returns to Main Menu

### AI Difficulty Selector

- Options:
  - EASY → Random moves
  - MEDIUM → Blocks wins/seeks immediate wins
  - HARD → Complete minimax algorithm (calculates all possibilities)

- Starter Selector:
  - PLAYER STARTS / AI STARTS toggle buttons

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
- Visual Features:
  - Column indicators showing valid moves
  - Realistic disc drop animation from top to bottom
  - Winning combination highlight

### Game Flow

- Player Turn:
  - Click column to drop disc (SFX plays)
  - Disc animates falling from top to bottom
  - Turn indicator shows current player

- AI Turn (if applicable):
  - Difficulty-based move calculation
  - Instant response (no artificial delay)
  - Visual feedback during AI's turn
  - In dev mode: Shows AI's calculation process with darker colored discs

- Win Detection:
  - Horizontal/vertical/diagonal 4-in-a-row
  - Winning Animation: Pulsing brightness effect
  - Win SFX: Triumphant chime

### End Game

- Popup Modal:
  - "Player X Wins!" / "AI Wins!" in winner's color
  - "It's a draw!" for tied games
  - MAIN MENU button

## 3. AI Implementation

For detailed technical information about the in-game AI, please refer to [in_game_ai.md](in_game_ai.md).
For a technical explanation of the AI training and model structure, please refer to [AI_Training_Technical.md](AI_Training_Technical.md).

### Quick Overview

- **Easy Mode**: Random move selection
- **Medium Mode**: One-ply lookahead with win/block detection
- **Hard Mode**: Complete minimax algorithm calculating all possible moves

## 4. Technical Specifications

### Dependencies

```bash
$ python --version
Python 3.12.10

Required packages:
- pygame==2.5.2
- numpy==1.26.4
```

### File Structure

```bash
ConnectX/
├── main.py             # Main game logic
├── AI_Explanation.md   # AI implementation details
├── settings.py         # Settings management
├── game_settings.json  # User preferences
├── requirements.txt    # Python dependencies
├── launch.sh           # Unix launcher
├── assets/             # Game assets
│   ├── music.mp3       # Background music
│   └── drop.mp3        # Drop sound effect
└── logs/               # Game logs (automatically generated)
```

## 5. Key Features

- **Modern UI**: Clean, responsive interface with animations
- **Customizable**: Adjustable colors, sound, and AI difficulty
- **Sound System**: Dynamic volume control for music and SFX
- **Fullscreen Support**: Toggle between windowed and fullscreen modes
- **Logging System**: Comprehensive game event logging (logs directory is automatically generated)
- **Cross-Platform**: Works on Windows, Linux, and macOS
- **Optional Development Mode**: Visualize AI calculations by running with `dev` parameter

## 6. Controls

- **Mouse**: Click columns to drop pieces
- **F**: Toggle fullscreen mode
- **S**: Switch to windowed mode
- **ESC**: Return to main menu
- **D**: Toggle development mode
- **R**: Restart the game
- **M**: Return to main menu

## 7. Development

### Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

### Building from Source

1. Clone the repository
2. Install dependencies: `pip install -r requirements.txt`
3. Run the game: `python main.py`
   - Optional: Run in development mode: `python main.py dev`

## 8. License

This project is open source and available under the MIT License.

## AI Logs

When playing against the Hard AI, the game automatically generates detailed logs of the AI's thinking process in the `ai_logs` directory. These logs include:

- Current board state
- All possible moves evaluated
- Scores for each move
- Depth of evaluation

The logs are automatically generated and should not be committed to version control.
