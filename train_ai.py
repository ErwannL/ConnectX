import numpy as np
import os
import time
from datetime import datetime
import logging
from tqdm import tqdm
import pickle
from ai import AI
from collections import deque
import concurrent.futures
import math

class AITrainer:
    def __init__(self, depth=None):
        self.depth = depth
        self.model = {}  # Will store board states and their best moves
        self.setup_logging()
        self.start_time = None  # Add start_time attribute

    def setup_logging(self):
        log_dir = "training_ai"
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
        timestamp = datetime.now().strftime("%Y-%m-%d_%H_%M_%S")
        depth_str = f"depth_{self.depth}" if self.depth is not None else "full_game"
        self.log_file = os.path.join(log_dir, f"training_{depth_str}_date_{timestamp}.log")
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(self.log_file),
                logging.StreamHandler()
            ]
        )
        logging.info(f"Training log initialized: {self.log_file}")

    def generate_all_positions(self):
        """Generates all reachable board states.
        If self.depth is specified, it generates states after exactly self.depth moves.
        If self.depth is None, it generates all states until game end (win/draw).
        """
        initial_board = np.zeros((6, 7), dtype=int)

        if self.depth is not None: # Fixed depth generation
            logging.info(f"Generating all board positions for exactly {self.depth} moves (7^{self.depth} potential combinations). This may take a while...")
            positions = []
            visited_states_fixed_depth = set() # To store unique board states for fixed depth

            def _generate_boards_recursive(current_board, num_moves_made, current_player):
                board_key = self._board_to_key(current_board)
                state_key = (board_key, current_player) # Include player to move in state key

                if state_key in visited_states_fixed_depth:
                    return # Already processed this unique board state for this player

                visited_states_fixed_depth.add(state_key)

                if num_moves_made == self.depth:
                    positions.append((current_board.copy(), current_player))
                    return

                # If the game is already over at this state, stop generating further moves
                ai_checker = AI("HARD", is_in_game=False) # Local instance for checking terminal states
                ai_checker.max_depth = 1 # Only need win/draw check, not deep minimax

                if ai_checker._check_win(current_board, current_player) or \
                   ai_checker._check_win(current_board, 3 - current_player) or \
                   len(ai_checker._get_valid_locations(current_board)) == 0:
                    positions.append((current_board.copy(), current_player))
                    return

                for col in range(7):
                    row = self._get_next_open_row(current_board, col)
                    if row is not None:
                        temp_board = current_board.copy()
                        temp_board[row][col] = current_player
                        _generate_boards_recursive(temp_board, num_moves_made + 1, 3 - current_player)

            _generate_boards_recursive(initial_board, 0, 1) # Start with player 1
            logging.info(f"Generated {len(positions)} unique board positions for depth {self.depth}.")
            return positions
        else: # Full game traversal (BFS)
            logging.warning("WARNING: Generating all possible board states until a full board or win is extremely computationally intensive and will likely take an impractical amount of time and memory. Proceed with caution.")
            
            queue = deque([(initial_board, 1)]) # (board, current_player)
            visited_states = set() # Store (board_key, current_player) to avoid re-evaluating
            all_states_to_train = [] # Store (board, current_player) for training

            # Add initial state
            visited_states.add((self._board_to_key(initial_board), 1))
            all_states_to_train.append((initial_board.copy(), 1))

            # Use an AI instance for checking terminal states
            ai_checker = AI("HARD", is_in_game=False)
            ai_checker.max_depth = 1 # Only need win/draw check, not deep minimax

            while queue:
                current_board, current_player = queue.popleft()
                
                # Check if current board is a terminal state
                if ai_checker._check_win(current_board, current_player) or \
                   ai_checker._check_win(current_board, 3 - current_player) or \
                   len(ai_checker._get_valid_locations(current_board)) == 0:
                    continue # Skip generating moves from terminal states
                
                # Generate next possible moves
                for col in range(7):
                    row = self._get_next_open_row(current_board, col)
                    if row is not None:
                        next_board = current_board.copy()
                        next_board[row][col] = current_player
                        next_player = 3 - current_player
                        
                        next_state_key = (self._board_to_key(next_board), next_player)
                        
                        if next_state_key not in visited_states:
                            visited_states.add(next_state_key)
                            all_states_to_train.append((next_board.copy(), next_player))
                            queue.append((next_board, next_player))
            
            logging.info(f"Generated {len(all_states_to_train)} unique board states for full game traversal.")
            return all_states_to_train

    def _get_next_open_row(self, board, col):
        """Helper to find the next open row in a column"""
        for r in range(5, -1, -1):
            if board[r][col] == 0:
                return r
        return None

    def _evaluate_position(self, board, player_to_move, ai_difficulty, ai_max_depth):
        """Helper function to evaluate a single board position in a separate thread"""
        ai = AI(ai_difficulty, is_in_game=False)  # Create a new AI instance for each thread without game mode
        ai.max_depth = ai_max_depth
        
        # Ensure AI's internal state is clean for each evaluation
        ai.calculated_move = None
        ai.is_thinking = False

        best_move = ai.get_move(board.copy(), player_to_move)
        return board, player_to_move, best_move

    def _format_duration(self, seconds):
        """Convert seconds into a human-readable duration string"""
        days = int(seconds // (24 * 3600))
        seconds = seconds % (24 * 3600)
        hours = int(seconds // 3600)
        seconds %= 3600
        minutes = int(seconds // 60)
        seconds = int(seconds % 60)

        parts = []
        if days > 0:
            parts.append(f"{days} day{'s' if days != 1 else ''}")
        if hours > 0:
            parts.append(f"{hours} hour{'s' if hours != 1 else ''}")
        if minutes > 0:
            parts.append(f"{minutes} minute{'s' if minutes != 1 else ''}")
        if seconds > 0 or not parts:  # Include seconds if it's the only unit or if there are seconds
            parts.append(f"{seconds} second{'s' if seconds != 1 else ''}")
        
        return ", ".join(parts)

    def train(self):
        self.start_time = time.time()  # Record start time
        logging.info(f"Starting training with depth {self.depth if self.depth is not None else 'full game'}")
        
        # Generate all positions first
        positions_to_train = self.generate_all_positions()
        total_combinations = len(positions_to_train)
        
        logging.info(f"Total combinations/states to evaluate: {total_combinations}")

        # Estimate time for fixed depth training
        if self.depth is not None and total_combinations > 0:
            # Rough estimation: assume average time per position is 0.01 seconds (can vary greatly)
            # This will be more accurate with actual profiling or a more complex estimation model.
            # For now, this gives a very rough idea.
            estimated_seconds_per_combination = self.depth / 10 # This is a placeholder, tune based on actual performance
            estimated_total_seconds = total_combinations * estimated_seconds_per_combination
            estimated_minutes = math.ceil(estimated_total_seconds / 60)
            logging.info(f"Estimated training time: approximately {estimated_minutes} minutes for {total_combinations} combinations.")
        elif self.depth is None:
            logging.info("Estimated training time for full game traversal will be dynamically updated by the progress bar.")

        # Determine AI difficulty and depth for evaluation during training
        ai_difficulty = "HARD"
        # Set AI evaluation depth during training: use min(self.depth, 4) for fixed depth
        # to balance accuracy and performance, or default to 3 for full game traversal.
        ai_max_depth_for_eval = min(self.depth, 4) if self.depth is not None else 3
        logging.info(f"AI evaluator initialized with max_depth: {ai_max_depth_for_eval}")

        trained_count = 0
        # Use ThreadPoolExecutor for multithreaded training
        cpu_count = os.cpu_count() or 4  # Fallback to 4 if cpu_count() returns None
        max_workers = max(1, int(cpu_count * 0.75))  # Use 75% of available CPU cores
        logging.info(f"Using {max_workers} worker threads for training (75% of {cpu_count} CPU cores)")

        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit all tasks at once for maximum parallelization
            future_to_board_player = {
                executor.submit(self._evaluate_position, board, player_to_move, ai_difficulty, ai_max_depth_for_eval):
                (board, player_to_move)
                for board, player_to_move in positions_to_train
            }
            
            # Process results as they complete
            for future in tqdm(concurrent.futures.as_completed(future_to_board_player), 
                             total=total_combinations, 
                             desc="Training positions"):
                board, player_to_move = future_to_board_player[future]
                try:
                    board_result, player_result, best_move = future.result()
                    board_key = self._board_to_key(board_result)
                    if board_key not in self.model:
                        self.model[board_key] = {}
                    self.model[board_key][player_result] = best_move
                    trained_count += 1
                    logging.debug(f"Board evaluation for Player {player_result} completed. Best Move: {best_move}")
                except Exception as exc:
                    logging.error(f"Board {board} (Player {player_to_move}) generated an exception: {exc}")
                
        logging.info(f"Finished evaluating {trained_count} board-player combinations.")
        logging.info(f"Total unique board states stored in model: {len(self.model)}")
        
        # Save the model
        self.save_model()
        
        # Calculate and log training duration
        end_time = time.time()
        duration_seconds = end_time - self.start_time
        formatted_duration = self._format_duration(duration_seconds)
        logging.info(f"Training completed in {formatted_duration}")

    def _board_to_key(self, board):
        """Convert board to a hashable key"""
        return tuple(map(tuple, board.astype(int)))

    def save_model(self):
        """Save the trained model"""
        model_dir = "models"
        if not os.path.exists(model_dir):
            os.makedirs(model_dir)
        
        timestamp = datetime.now().strftime("%Y-%m-%d_%H_%M_%S")
        depth_str = f"depth_{self.depth}" if self.depth is not None else "full_game"
        filename = os.path.join(model_dir, f"model_{depth_str}_date_{timestamp}.pkl")
        
        with open(filename, 'wb') as f:
            pickle.dump(self.model, f)
        logging.info(f"Model saved to {filename}")

def main():
    import sys
    
    # Setup root logger level for console output (important for tqdm)
    logging.getLogger().setLevel(logging.INFO)

    if len(sys.argv) < 2 or not sys.argv[1].startswith("train"):
        print("Usage: python train_ai.py train [depth]")
        return
    
    # Parse depth from command line
    depth = None  # Default to full game traversal
    if len(sys.argv) > 2:
        try:
            depth = int(sys.argv[2])
            if depth < 1:
                logging.warning("Depth must be at least 1 for fixed-depth training. Defaulting to full game traversal.")
                depth = None
            if depth is not None and depth > 7: 
                logging.warning(f"Training with depth {depth} will generate 7^{depth} = {7**depth} combinations, which will be extremely time-consuming and memory-intensive.")
        except ValueError as e:
            logging.error(f"Invalid depth value: {e}. Defaulting to full game traversal.")
            depth = None
    
    trainer = AITrainer(depth)
    trainer.train()

if __name__ == "__main__":
    main() 