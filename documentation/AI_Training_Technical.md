# AI Training Technical Documentation

[← Back to README](../README.md)

## Overview

The ConnectX AI training system generates and evaluates board positions to create a comprehensive model of optimal moves. The system uses a combination of minimax algorithm evaluation and multi-threaded processing to efficiently generate training data. Recent updates include corrected evaluation depth and improved model quality.

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
   - **Evaluation**:
     - Fixed depth: Uses specified training depth
     - Full game: Uses depth 6
   - This ensures models are trained with the actual depth they claim

2. **Evaluation Process**
   - For each position:
     - Generates all possible next moves
     - Evaluates each move using minimax at full training depth
     - Stores best move and score
   - Handles terminal states (win/draw)
   - Uses window-based pattern scoring
   - Enhanced error handling and logging

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
   - Location: `ai/models/` directory
   - Naming: `model_depth_[depth]_date_[YYYY-MM-DD_HH_MM_SS].pkl`
   - Format: Python pickle file

2. **Training Logs**
   - Location: `ai/models_log/` directory
   - Naming: `training_depth_[depth]_date_[YYYY-MM-DD_HH_MM_SS].log`
   - Contents: Training progress, errors, statistics

3. **Checkpoints**
   - Location: `ai/models_checkpoints/` directory
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
  - d = evaluation depth (now uses full training depth)

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

### Model Integration (UPDATED)
1. **Automatic Loading**
   - Load best available model at game start
   - Fallback to minimax if load fails
   - Memory-efficient loading

2. **Move Selection**
   - Lookup current position
   - Use stored best move if available
   - Fallback to minimax evaluation
   - Enhanced priority system (win/block/model/minimax)

### Performance Impact
- Minimal memory overhead
- Fast move lookup
- Graceful fallback
- No impact on game performance

## Recent Improvements (NEW)

### 1. Corrected Evaluation Depth
- **Problem**: Models were trained with limited evaluation depth (4 for fixed depth, 3 for full game)
- **Solution**: Now uses full training depth for evaluation
- **Impact**: Models are now truly trained at their claimed depth

### 2. Enhanced Move Selection
- **Priority System**: Win detection → Blocking → Model → Minimax
- **Improved Logging**: Clear indication of which method was used
- **Better Fallbacks**: Graceful degradation when models fail

### 3. Automatic Model Selection
- **Smart Selection**: Chooses highest depth, then most recent
- **No Manual Intervention**: Automatically picks best available model
- **Clear Logging**: Shows which model was selected and why

### 4. Improved User Interface
- **Model Mode**: New difficulty level for trained models
- **Automatic Selection**: No need to manually choose models
- **Enhanced Logs**: Clear indication of AI behavior and decisions

## Training Quality Improvements

### Before vs After
- **Before**: Models trained at depth 7 but evaluated at depth 4
- **After**: Models trained and evaluated at full depth
- **Result**: Much stronger and more accurate models

### Model Strength
- **Depth 1-3**: Basic strategic play
- **Depth 4-5**: Intermediate level
- **Depth 6-7**: Advanced play, near-optimal moves
- **Depth 8+**: Expert level, very difficult to beat

## Best Practices

### Training Recommendations
1. **Start with Lower Depths**: Train depth 1-3 first to validate system
2. **Gradual Increase**: Progress to higher depths (4-6) for stronger models
3. **Resource Planning**: Higher depths require significant time and memory
4. **Validation**: Test models against different difficulty levels

### Model Usage
1. **Automatic Selection**: Let the system choose the best model
2. **Specific Models**: Use `./launch.sh model [path]` for specific models
3. **Performance Monitoring**: Check logs for model performance
4. **Fallback Handling**: System gracefully handles missing or corrupted models
