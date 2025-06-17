# ConnectX: Intelligent Connect Four

## Overview

A Python-based Connect Four game featuring dynamic AI opponents, customizable settings, and multiplayer functionality. Built with Pygame for graphics and sound, and featuring advanced AI capabilities with both traditional algorithms and machine learning approaches.

## Features

### Game Features
- Play against a friend or AI
- Four AI difficulty levels:
  - Easy: Makes random valid moves
  - Medium: Looks for winning moves and blocks opponent's winning moves
  - Hard: Uses minimax algorithm with alpha-beta pruning
  - Model: Uses pre-trained models for optimal play (NEW!)
- Customizable player colors
- Adjustable music and sound effects
- Fullscreen/windowed mode toggle
- Smooth disc drop animations
- Modern UI with hover effects

### AI Features
- Multi-threaded CPU optimization (uses 75% of available cores)
- Dynamic AI depth based on CPU cores (Hard mode)
- Pre-trained model support with automatic selection
- Enhanced move selection with win/block detection
- Development mode with AI visualization
- Comprehensive logging system
- Training data generation and model management

## Installation

The game automatically handles all dependencies. Simply clone the repository and run:

```bash
./launch.sh
```

## Running the Game

### Basic Launch
```bash
./launch.sh
```

### Development Mode
```bash
./launch.sh dev
```
Development mode provides:
- AI's current calculation board visualization
- Move evaluations display
- Best move selection process visualization
- Neural network predictions (when using a trained model)
- Detailed logging of AI decisions

### Using a Trained Model
```bash
./launch.sh model ai/models/[model].pkl
```

### Training a New Model
```bash
./launch.sh train [depth]
```
Where `depth` is an optional parameter specifying the search depth (default: full game).

Training process:
1. Generates all possible board positions up to specified depth
2. Evaluates each position using minimax algorithm at full depth
3. Saves the model to `ai/models/` directory
4. Creates training logs in `ai/models_log/` directory

Training controls:
- Ctrl+Space: Pause/resume training
- To stop training:
  1. First pause with Ctrl+Space
  2. Then use Ctrl+C to stop and save

## Game Controls

### In-Game Controls
- Left-click: Drop a piece
- ESC: Return to main menu
- M: Return to main menu

### Menu Navigation
- Main Menu:
  - PLAY: Opens play menu
  - SETTINGS: Opens settings menu
  - EXIT: Closes game
- Play Menu:
  - PLAY VS AI: Opens AI difficulty selector
  - PLAY VS FRIEND: Starts 2-player game
  - GO BACK: Returns to main menu
- Settings Menu:
  - Music Volume: Adjust background music (0-100%)
  - SFX Volume: Adjust sound effects (0-100%)
  - Player Colors: Choose colors for both players
  - BACK: Returns to main menu

## Project Structure

### Core Files
- `main.py`: Main game logic and UI
- `ai.py`: AI implementation (minimax and model integration)
- `train_ai.py`: AI training system
- `settings.py`: Game settings management
- `logging_config.py`: Logging system configuration
- `game_settings.json`: User preferences

### Directories
- `ai/models/`: Saved AI models
- `ai/models_log/`: Training logs
- `ai/models_checkpoints/`: Training checkpoints (auto-generated)
- `assets/`: Game assets (music, sounds)
- `logs/`: Game and AI logs

### Scripts
- `launch.sh`: Game launcher script
- `push.sh`: Git push helper script

## Technical Details

### Requirements
- Python 3.12+
- Pygame 2.5.2
- NumPy 1.26.4

### Performance Optimization
- Multi-threaded AI evaluation
- Dynamic CPU core utilization
- Efficient board state representation
- Optimized minimax with alpha-beta pruning

### AI Implementation
For detailed technical information about:
- **AI Usage Guide**: See [AI_Usage_Guide.md](documentation/AI_Usage_Guide.md) - User-friendly guide for playing against AI
- **In-game AI**: See [In_game_ai.md](documentation/In_game_ai.md) - Technical details of AI implementation
- **AI Training**: See [AI_Training_Technical.md](documentation/AI_Training_Technical.md) - Technical details of model training

## Recent Updates

### AI Improvements
- **Model Mode**: New difficulty level using pre-trained models
- **Automatic Model Selection**: System automatically chooses the best available model
- **Enhanced Move Selection**: Priority system (win → block → model → minimax)
- **Improved Logging**: Clear indication of AI behavior and decisions
- **Corrected Training**: Models now use full training depth for evaluation

### User Experience
- **Streamlined Interface**: No manual model selection required
- **Better Feedback**: Clear logs showing which AI mode and model are active
- **Fallback Handling**: Graceful degradation when models are unavailable
- **Performance Optimization**: Faster model loading and evaluation

## License

This project is licensed under the MIT License - see the [LICENSE](documentation/LICENSE) file for details.
