# ConnectX AI Technical Documentation

## Overview

The ConnectX AI system implements three distinct difficulty levels using different algorithmic approaches. The AI is implemented in the `AI` class (`ai.py`) and uses a combination of deterministic and probabilistic strategies to provide varying levels of challenge.

## AI Architecture

### Class Structure

```python
class AI:
    def __init__(self, difficulty="MEDIUM"):
        self.difficulty = difficulty
        self.max_depth = 5  # For hard difficulty
```

The AI class maintains a difficulty level and maximum search depth for the minimax algorithm.

## Difficulty Levels

### 1. Easy Mode

- **Strategy**: Pure random selection
- **Implementation**:

  ```python
  def _easy_move(self, board):
      valid_locations = self._get_valid_locations(board)
      return random.choice(valid_locations)
  ```

- **Behavior**: Makes completely random moves from valid columns
- **Use Case**: Suitable for beginners or casual play

### 2. Medium Mode

- **Strategy**: One-ply lookahead with win/block detection
- **Implementation**:

  ```python
  def _medium_move(self, board, player_piece):
      valid_locations = self._get_valid_locations(board)

      # Check for winning move
      for col in valid_locations:
          temp_board = board.copy()
          row = self._get_next_open_row(temp_board, col)
          temp_board[row][col] = player_piece
          if self._check_win(temp_board, player_piece):
              return col

      # Check for blocking move
      opponent_piece = 3 - player_piece
      for col in valid_locations:
          temp_board = board.copy()
          row = self._get_next_open_row(temp_board, col)
          temp_board[row][col] = opponent_piece
          if self._check_win(temp_board, opponent_piece):
              return col

      return random.choice(valid_locations)
  ```

- **Behavior**:
  1. Checks for immediate winning moves
  2. Checks for moves that block opponent's winning moves
  3. Falls back to random selection if neither exists
- **Use Case**: Balanced gameplay with basic strategic awareness

### 3. Hard Mode

- **Strategy**: Minimax algorithm with alpha-beta pruning
- **Implementation**:

  ```python
  def _hard_move(self, board, player_piece):
      valid_locations = self._get_valid_locations(board)
      best_score = -float('inf')
      best_col = random.choice(valid_locations)

      for col in valid_locations:
          row = self._get_next_open_row(board, col)
          temp_board = board.copy()
          temp_board[row][col] = player_piece
          score = self._minimax(temp_board, self.max_depth, -float('inf'), float('inf'), False, player_piece)

          if score > best_score:
              best_score = score
              best_col = col

      return best_col
  ```

- **Behavior**:
  1. Uses minimax algorithm with alpha-beta pruning
  2. Searches up to 5 moves ahead
  3. Evaluates board positions using a sophisticated scoring system
- **Use Case**: Challenging gameplay for experienced players

## Board Evaluation

### Scoring System

The AI uses a window-based evaluation system that scores potential moves based on patterns:

```python
def _evaluate_window_score(self, window, piece, opponent_piece):
    score = 0
    if window.count(piece) == 4:
        score += 100
    elif window.count(piece) == 3 and window.count(0) == 1:
        score += 5
    elif window.count(piece) == 2 and window.count(0) == 2:
        score += 2

    if window.count(opponent_piece) == 3 and window.count(0) == 1:
        score -= 4

    return score
```

### Evaluation Patterns

1. **Four in a row**: +100 points
2. **Three in a row with one empty**: +5 points
3. **Two in a row with two empty**: +2 points
4. **Opponent's three in a row with one empty**: -4 points

## Minimax Algorithm

### Implementation

```python
def _minimax(self, board, depth, alpha, beta, maximizing_player, player_piece):
    valid_locations = self._get_valid_locations(board)
    is_terminal = self._is_terminal_node(board)

    if depth == 0 or is_terminal:
        if is_terminal:
            if self._check_win(board, player_piece):
                return 100000000000000
            elif self._check_win(board, 3 - player_piece):
                return -10000000000000
            else:  # Game is over, no more valid moves
                return 0
        else:  # Depth is zero
            return self._evaluate_window(board, player_piece)

    if maximizing_player:
        value = -float('inf')
        for col in valid_locations:
            row = self._get_next_open_row(board, col)
            temp_board = board.copy()
            temp_board[row][col] = player_piece
            new_score = self._minimax(temp_board, depth-1, alpha, beta, False, player_piece)
            value = max(value, new_score)
            alpha = max(alpha, value)
            if alpha >= beta:
                break
        return value
    else:
        value = float('inf')
        for col in valid_locations:
            row = self._get_next_open_row(board, col)
            temp_board = board.copy()
            temp_board[row][col] = 3 - player_piece
            new_score = self._minimax(temp_board, depth-1, alpha, beta, True, player_piece)
            value = min(value, new_score)
            beta = min(beta, value)
            if alpha >= beta:
                break
        return value
```

### Key Features

1. **Alpha-Beta Pruning**: Optimizes search by eliminating branches that won't affect the final decision
2. **Depth-Limited Search**: Limits lookahead to 5 moves for performance
3. **Terminal State Detection**: Checks for wins and draws
4. **Board Evaluation**: Uses window-based scoring for non-terminal positions

## Performance Considerations

1. **Memory Usage**:
   - Board representation: 6x7 numpy array
   - Temporary boards created during search
   - Alpha-beta pruning reduces memory requirements

2. **Time Complexity**:
   - Easy: O(n) where n is number of valid columns
   - Medium: O(n) with win/block checks
   - Hard: O(b^d) where b is branching factor and d is depth (5)

3. **Optimizations**:
   - Alpha-beta pruning
   - Early termination on win/draw
   - Efficient board copying
   - Valid move filtering

## Integration with Game Engine

The AI is integrated into the game through the `Game` class:

```python

def make_ai_move(self):
    if not self.vs_ai or self.current_player != self.ai_piece or self.game_over or self.animating:
        return

    pygame.time.wait(int(self.settings.get_ai_thinking_time() * 1000))
    ai_col = self.ai_player.get_move(self.board.copy(), self.ai_piece)
    # ... move execution and game state updates
```

## Future Improvements

1. **Adaptive Difficulty**:
   - Adjust AI strength based on player performance
   - Dynamic depth adjustment

2. **Enhanced Evaluation**:
   - More sophisticated pattern recognition
   - Position-based scoring

3. **Machine Learning**:
   - Train AI using reinforcement learning
   - Learn from player strategies

4. **Performance Optimization**:
   - Parallel move evaluation
   - Caching of common positions
   - Optimized board representation
