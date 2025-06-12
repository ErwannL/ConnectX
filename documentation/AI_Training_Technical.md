# AI Training Technical Documentation

[← Back to README](../Readme.md)

## Overview

The ConnectX AI training system generates and evaluates board positions to create a comprehensive model of optimal moves. The system uses a combination of minimax algorithm evaluation and multi-threaded processing to efficiently generate training data.

## Training Process

### 1. Position Generation

The system generates board positions in two modes:

1. **Fixed Depth Mode**
   - Generates all possible board positions up to specified depth
   - Example: Depth 3 generates all positions after 3 moves
   - Format: `./launch.sh train [depth]`

2. **Full Game Mode**
   - Generates all possible board positions for complete games
   - No depth limit, explores all valid game states
   - Format: `./launch.sh train`

### 2. Position Evaluation

Each generated position is evaluated using:

1. **AI Evaluator**
   - Uses AI instance with "HARD" difficulty
   - Minimax algorithm with alpha-beta pruning
   - Dynamic depth based on training mode:
     - Fixed depth: Uses specified training depth
     - Full game: Uses depth 3 (optimized for performance)

2. **Evaluation Process**
   - For each position:
     - Generates all possible next moves
     - Evaluates each move using minimax
     - Stores best move and score
   - Handles terminal states (win/draw)
   - Uses window-based pattern scoring

### 3. Multi-threading

The training process uses parallel processing:

1. **Thread Management**
   - Uses 75% of available CPU cores
   - Minimum of 1 thread
   - Thread pool for position evaluation
   - Each thread gets independent AI instance

2. **Thread Safety**
   - Thread-safe board state handling
   - Independent AI instances per thread
   - Synchronized model updates
   - Progress tracking with tqdm

## Training Controls

### Keyboard Controls
- **Ctrl+Space**: Pause/resume training
- **Ctrl+C**: Stop training (only works when paused)

Important notes:
- Ctrl+C is disabled during active training
- To stop training:
  1. First pause with Ctrl+Space
  2. Then use Ctrl+C to stop and save

### Checkpoint System

Checkpoints are saved in two situations:
1. When training is paused (Ctrl+Space)
2. When training is stopped properly (after pause + Ctrl+C)

Checkpoint contents:
- Current model state
- Training progress
- Board positions to train
- Training parameters
- Timing information

## Model Management

### Model Structure

The trained model is a dictionary where:
- Keys: Board states (as tuples)
- Values: Dictionaries containing:
  - Player piece (1 or 2)
  - Best move for that position
  - Evaluation score

### File Management

1. **Model Files**
   - Location: `models/` directory
   - Naming: `model_depth_[depth]_date_[YYYY-MM-DD_HH_MM_SS].pkl`
   - Format: Python pickle file

2. **Training Logs**
   - Location: `training_ai/` directory
   - Naming: `training_depth_[depth]_date_[YYYY-MM-DD_HH_MM_SS].log`
   - Contents: Training progress, errors, statistics

3. **Checkpoints**
   - Location: `checkpoints/` directory
   - Naming: `checkpoint_depth_[depth]_date_[YYYY-MM-DD_HH_MM_SS].pkl`
   - Auto-generated when pausing/stopping

## Performance Considerations

### Memory Usage
- Board state: 6x7 numpy array
- Model storage: Dictionary of positions
- Temporary storage during evaluation
- Checkpoint files

### Time Complexity
- Position generation: O(7^depth)
- Position evaluation: O(b^d) where:
  - b = branching factor (7)
  - d = evaluation depth

### Optimization Techniques
1. **Multi-threading**
   - Parallel position evaluation
   - Efficient CPU core utilization
   - Thread pool management

2. **Alpha-Beta Pruning**
   - Reduces search space
   - Improves evaluation speed
   - Maintains optimal move selection

3. **Early Termination**
   - Stops on win/draw detection
   - Skips evaluated positions
   - Optimizes full game traversal

## Error Handling

### Exception Management
1. **Position Evaluation**
   - Catches and logs individual position errors
   - Continues training despite isolated failures
   - Reports errors in training log

2. **Model Operations**
   - Handles file I/O errors
   - Manages memory constraints
   - Provides fallback mechanisms

### Logging System
- Detailed error reporting
- Training progress tracking
- Performance metrics
- System resource usage

## Usage in Game

### Model Integration
1. **Loading**
   - Load model at game start
   - Fallback to minimax if load fails
   - Memory-efficient loading

2. **Move Selection**
   - Lookup current position
   - Use stored best move if available
   - Fallback to minimax evaluation

### Performance Impact
- Minimal memory overhead
- Fast move lookup
- Graceful fallback
- No impact on game performance
