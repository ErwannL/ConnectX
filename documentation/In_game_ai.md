# In-Game AI Technical Documentation

[← Back to README](../README.md)

## Overview

The ConnectX AI system implements a hybrid approach combining traditional game tree search algorithms with pre-trained models. The AI adapts its behavior based on the selected difficulty level and available computational resources. Recent updates include automatic model selection, improved logging, and enhanced move evaluation.

## AI Difficulty Levels

### Easy Mode
- Makes random valid moves
- No lookahead or strategy
- Suitable for beginners

### Medium Mode
- One-ply lookahead (depth = 4)
- Implements basic strategy:
  - Looks for immediate winning moves
  - Blocks opponent's winning moves
  - Avoids obviously bad moves
- Good balance between challenge and performance

### Hard Mode
- Dynamic depth based on CPU cores (depth = max(6, cpu_cores/4))
- Full minimax algorithm with alpha-beta pruning
- Pre-trained model integration when available
- Multi-threaded evaluation
- Comprehensive move evaluation

### Model Mode (NEW)
- **Automatic Model Selection**: Chooses the best available trained model
- **Selection Logic**:
  1. Highest depth model available
  2. Most recent model if multiple have same depth
- **Fallback**: Uses HARD mode if no models available
- **Performance**: Fast move lookup with pre-calculated optimal moves
- **Logging**: Clear indication of which model is being used

## AI Implementation

### Core Components

1. **Move Generation**
   - Identifies valid moves (non-full columns)
   - Simulates moves to create new board states
   - Handles board state validation

2. **Board Evaluation**
   - Window-based pattern recognition
   - Scoring system for different board patterns
   - Terminal state detection (win/draw)

3. **Search Algorithm**
   - Minimax with alpha-beta pruning
   - Dynamic depth control
   - Move ordering for better pruning
   - Multi-threaded evaluation

### Enhanced Model Integration (UPDATED)

1. **Automatic Model Loading**
   ```python
   def __init__(self, difficulty="HARD", debug_mode=False, is_in_game=True, model_file=None):
       # Load specified model or auto-select best available
       if model_file and os.path.exists(model_file):
           self.model = load_model(model_file)
       else:
           self.model = load_best_available_model()
   ```

2. **Improved Move Selection Process**
   - **Priority 1**: Check for immediate winning moves
   - **Priority 2**: Block opponent's winning moves
   - **Priority 3**: Use pre-trained model (if available)
   - **Priority 4**: Fall back to minimax algorithm

3. **Model Usage**
   - Board state lookup in model
   - Direct move selection for known positions
   - Confidence-based fallback to minimax
   - Enhanced error handling and logging

## Performance Optimization

### Multi-threading
- Uses 75% of available CPU cores
- Parallel move evaluation
- Thread-safe AI instances
- Dynamic thread pool management

### Search Optimization
1. **Alpha-Beta Pruning**
   - Eliminates unnecessary branches
   - Improves search efficiency
   - Maintains optimal move selection

2. **Move Ordering**
   - Prioritizes promising moves
   - Enhances pruning effectiveness
   - Reduces search space

3. **Depth Control**
   - Dynamic depth based on CPU cores
   - Minimum depth of 6 for Hard mode
   - Adaptive to system resources

## Enhanced Logging System (NEW)

### Game Initialization Logs
```
=== GAME INITIALIZED: AI MODEL MODE ===
Model: model_depth_8_date_2025-06-17_22_23_02.pkl
AI MODEL loaded successfully: model_depth_8_date_2025-06-17_22_23_02.pkl (depth: 8)
```

### Move Selection Logs
- **Model Mode**: `AI MODEL chose column 3`
- **Easy Mode**: `AI EASY chose column 3`
- **Medium Mode**: `AI MEDIUM chose column 3`
- **Hard Mode**: `AI HARD chose column 3 (depth: 6)`

### Game State Logs
- Clear indication of which mode is active
- Model selection information
- Game start/end events
- Error handling and fallbacks

## Development Mode Features

When running in development mode (`./launch.sh dev`), the AI provides:

1. **Visualization**
   - AI's current calculation board
   - Move evaluation scores
   - Best move selection process
   - Neural network predictions (with model)

2. **Enhanced Logging**
   - Detailed move evaluations
   - Search depth information
   - Pruning statistics
   - Model usage data
   - Board state visualization

## AI Behavior

### Move Selection (UPDATED)
1. **Immediate Win Detection**
   - Check for winning moves first
   - Highest priority for move selection

2. **Blocking Detection**
   - Check for opponent's winning moves
   - Second priority for move selection

3. **Pre-trained Model Phase**
   - Lookup current board state
   - Use stored best move if available
   - Fall back to minimax if needed

4. **Minimax Phase**
   - Generate valid moves
   - Evaluate each move
   - Apply alpha-beta pruning
   - Select best scoring move

### Evaluation Criteria
1. **Terminal States**
   - Win detection
   - Draw detection
   - Immediate scoring

2. **Non-terminal States**
   - Window pattern scoring
   - Position evaluation
   - Strategic value assessment

## User Interface Integration (NEW)

### Model Selection
- **Automatic Selection**: No manual model selection required
- **Smart Defaults**: Always chooses the best available model
- **Fallback Handling**: Graceful degradation to HARD mode if needed

### Game Launch Options
1. **Standard Launch**: `./launch.sh`
   - Choose from EASY, MEDIUM, HARD, MODEL modes
   - MODEL mode auto-selects best available model

2. **Specific Model Launch**: `./launch.sh model ai/models/model_depth_X_date_...`
   - Forces use of specified model
   - Overrides automatic selection

3. **Development Mode**: `./launch.sh dev`
   - Enhanced logging and debugging
   - Visual AI calculation display

## Future Improvements

1. **Enhanced Model Integration**
   - Incremental model updates
   - Adaptive model selection
   - Performance analytics
   - Model performance comparison

2. **Improved Evaluation**
   - Advanced pattern recognition
   - Position-based scoring
   - Dynamic evaluation weights
   - Machine learning integration

3. **Performance Optimization**
   - Enhanced parallel processing
   - Improved caching
   - Optimized board representation
   - GPU acceleration for model evaluation and training

4. **Learning Capabilities**
   - Online learning
   - Adaptive difficulty
   - Player style recognition
   - Real-time model updates

5. **User Experience**
   - Model strength indicators
   - Performance statistics
   - Custom difficulty settings
   - Tournament mode
