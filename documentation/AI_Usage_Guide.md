# AI Usage Guide

[← Back to README](../README.md)

## Quick Start

### Playing Against AI

1. **Launch the game**: `./launch.sh`
2. **Select "PLAY"** from the main menu
3. **Choose "PLAY VS AI"** from the play menu
4. **Select AI difficulty**:
   - **EASY**: Random moves, good for beginners
   - **MEDIUM**: Basic strategy, blocks wins
   - **HARD**: Advanced AI with minimax algorithm
   - **MODEL**: Uses the best trained model available
5. **Choose who starts**: Player or AI
6. **Click "PLAY VS AI"** to start the game

### Playing Against a Specific Model

```bash
./launch.sh model ai/models/model_depth_8_date_2025-06-17_22_23_02.pkl
```

This will automatically use the specified model for the AI.

## AI Difficulty Levels Explained

### Easy Mode
- **Behavior**: Makes random valid moves
- **Best for**: Complete beginners, learning the game
- **Strategy**: None - purely random
- **Difficulty**: Very easy to beat

### Medium Mode
- **Behavior**: Basic strategic play
- **Best for**: Casual players, intermediate skill
- **Strategy**: 
  - Looks for immediate winning moves
  - Blocks opponent's winning moves
  - Otherwise makes random moves
- **Difficulty**: Moderate challenge

### Hard Mode
- **Behavior**: Advanced AI with deep search
- **Best for**: Experienced players, serious challenge
- **Strategy**:
  - Full minimax algorithm with alpha-beta pruning
  - Dynamic depth based on your CPU (6+ moves ahead)
  - Multi-threaded evaluation
  - Comprehensive position analysis
- **Difficulty**: Very challenging

### Model Mode (NEW!)
- **Behavior**: Uses pre-trained models for optimal play
- **Best for**: Maximum challenge, expert players
- **Strategy**:
  - Uses pre-calculated optimal moves from training
  - Automatically selects the best available model
  - Falls back to HARD mode if no models available
- **Difficulty**: Expert level (depends on model depth)

## Model Selection Logic

When you choose "MODEL" mode, the system automatically:

1. **Finds all available models** in the `ai/models/` directory
2. **Sorts by depth** (highest first)
3. **Sorts by date** (most recent first) if same depth
4. **Selects the best model** automatically
5. **Logs the selection** so you know which model is being used

### Example Log Output
```
Auto-selected model: model_depth_8_date_2025-06-17_22_23_02.pkl (depth: 8)
AI MODEL loaded successfully: model_depth_8_date_2025-06-17_22_23_02.pkl (depth: 8)
Starting game vs AI MODEL: model_depth_8_date_2025-06-17_22_23_02.pkl (AI does not start)
```

## Understanding Model Strengths

### Model Depth Guide
- **Depth 1-3**: Basic strategic play, easy to beat
- **Depth 4-5**: Intermediate level, moderate challenge
- **Depth 6-7**: Advanced play, very difficult to beat
- **Depth 8+**: Expert level, extremely challenging

### Why Models Are Strong
- **Pre-calculated**: All optimal moves are pre-computed
- **No time pressure**: No need to calculate during the game
- **Perfect memory**: Never forgets optimal strategies
- **Depth advantage**: Can look many moves ahead

## Game Controls

### During Gameplay
- **Mouse**: Click on a column to drop your piece
- **F**: Toggle fullscreen mode
- **ESC**: Return to main menu

### Training Controls (if training models)
- **Ctrl+Space**: Pause/resume training
- **Ctrl+C**: Stop training (only when paused)

## Development Mode

For debugging and AI analysis:

```bash
./launch.sh dev
```

This provides:
- Enhanced logging
- Visual AI calculation display
- Detailed move evaluation information
- Performance metrics

## Troubleshooting

### No Models Available
If you select "MODEL" mode but no models are found:
- The system will automatically fall back to HARD mode
- You'll see a warning in the logs
- The game will continue normally

### Model Loading Errors
If a model fails to load:
- The system will use HARD mode instead
- Check the logs for error details
- Verify the model file exists and isn't corrupted

### Performance Issues
If the game runs slowly:
- Try EASY or MEDIUM mode instead of HARD/MODEL
- Close other applications to free up CPU
- Check if your system meets the requirements

## Advanced Usage

### Training Your Own Models

1. **Train a depth 3 model** (quick test):
   ```bash
   python src/train_ai.py 3
   ```

2. **Train a depth 6 model** (strong AI):
   ```bash
   python src/train_ai.py 6
   ```

3. **Train full game model** (comprehensive):
   ```bash
   python src/train_ai.py
   ```

### Model Management

- **Location**: `ai/models/` directory
- **Naming**: `model_depth_X_date_YYYY-MM-DD_HH_MM_SS.pkl`
- **Backup**: Keep copies of important models
- **Cleanup**: Remove old models to save space

### Log Analysis

Check the logs in `logs/` directory for:
- Which model was selected
- AI move decisions
- Performance metrics
- Error messages

## Tips for Playing Against AI

### Against Easy/Medium
- Play aggressively
- Look for multiple winning threats
- Don't worry about complex strategies

### Against Hard/Model
- Play defensively
- Block obvious threats
- Try to control the center
- Don't leave obvious winning moves for the AI

### General Strategy
- **Center control**: Columns 3 and 4 are most valuable
- **Multiple threats**: Create situations where you can win in multiple ways
- **Defensive play**: Always check if your move allows the opponent to win
- **Pattern recognition**: Learn common winning patterns

## Performance Tips

### For Best AI Performance
- Use a modern CPU with multiple cores
- Close unnecessary applications
- Ensure adequate RAM (4GB+ recommended)
- Use SSD storage for faster model loading

### For Training Models
- Use a powerful CPU (8+ cores recommended)
- Ensure lots of RAM (8GB+ for high depths)
- Be patient - training can take hours for high depths
- Use checkpoints to resume interrupted training

## Future Features

The AI system is continuously improving. Planned features include:
- GPU acceleration for training
- Online learning capabilities
- Adaptive difficulty based on player skill
- Tournament mode with multiple AI opponents
- Performance analytics and statistics 