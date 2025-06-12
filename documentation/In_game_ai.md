# In-Game AI Technical Documentation

[← Back to README](../Readme.md)

## Overview

The ConnectX AI system implements a hybrid approach combining traditional game tree search algorithms with pre-trained models. The AI adapts its behavior based on the selected difficulty level and available computational resources.

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

### Model Integration

1. **Model Loading**
   ```python
   def _load_model(self, model_file):
       try:
           with open(model_file, 'rb') as f:
               return pickle.load(f)
       except Exception as e:
           logging.warning(f"Failed to load model {model_file}: {e}")
           return None
   ```

2. **Move Selection Process**
   - First attempts to use pre-trained model
   - Falls back to minimax if:
     - No model is loaded
     - Current position not in model
     - Model evaluation fails

3. **Model Usage**
   - Board state lookup in model
   - Direct move selection for known positions
   - Confidence-based fallback to minimax

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

## Development Mode Features

When running in development mode (`./launch.sh dev`), the AI provides:

1. **Visualization**
   - AI's current calculation board
   - Move evaluation scores
   - Best move selection process
   - Neural network predictions (with model)

2. **Logging**
   - Detailed move evaluations
   - Search depth information
   - Pruning statistics
   - Model usage data

## AI Behavior

### Move Selection
1. **Pre-trained Model Phase**
   - Lookup current board state
   - Use stored best move if available
   - Fall back to minimax if needed

2. **Minimax Phase**
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

## Future Improvements

1. **Enhanced Model Integration**
   - Incremental model updates
   - Adaptive model selection
   - Performance analytics

2. **Improved Evaluation**
   - Advanced pattern recognition
   - Position-based scoring
   - Dynamic evaluation weights

3. **Performance Optimization**
   - Enhanced parallel processing
   - Improved caching
   - Optimized board representation
   - GPU acceleration for model evaluation and training

4. **Learning Capabilities**
   - Online learning
   - Adaptive difficulty
   - Player style recognition
