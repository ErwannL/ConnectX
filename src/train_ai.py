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
import signal
import sys
import threading
import keyboard
import argparse

class AITrainer:
    def __init__(self, depth=None):
        self.depth = depth
        self.model = {}  # Will store board states and their best moves
        self.setup_logging()
        self.start_time = None
        self.paused = False
        self.last_save_time = None
        self.save_interval = 300  # Save every 5 minutes
        self.checkpoint_file = None
        self.positions_to_train = None
        self.trained_count = 0
        self.total_combinations = 0
        self.should_stop = False
        self.pause_start_time = None  # Track when pause started
        self.total_pause_time = 0  # Track total time spent paused
        self.executor = None  # Store executor reference
        self._setup_signal_handlers()
        self._setup_keyboard_handlers()

    def _setup_signal_handlers(self):
        """Setup signal handlers for graceful stop"""
        def signal_handler(signum, frame):
            if self.should_stop:
                print("\nForce stopping...")
                if self.executor:
                    self.executor.shutdown(wait=False)
                keyboard.unhook_all()
                os._exit(1)  # Force exit

            print("\nStopping gracefully... (Press Ctrl+C again to force stop)")
            self.should_stop = True
            if self.pause_start_time is not None:
                self.total_pause_time += time.time() - self.pause_start_time
                self.save_checkpoint()
            
            # Shutdown executor if it exists
            if self.executor:
                self.executor.shutdown(wait=False)
            
            # Cleanup keyboard handlers
            keyboard.unhook_all()
            sys.exit(0)

        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)

    def _setup_keyboard_handlers(self):
        """Setup keyboard handlers for pause/resume"""
        def on_ctrl_space():
            self._toggle_pause()

        keyboard.add_hotkey('ctrl+space', on_ctrl_space, suppress=True)

    def _toggle_pause(self):
        """Toggle pause state when Ctrl+Space is pressed"""
        try:
            self.paused = not self.paused
            if self.paused:
                logging.info("Training paused. Press Ctrl+Space to resume or Ctrl+C to stop completely.")
                self.pause_start_time = time.time()  # Record when pause started
                self.save_checkpoint()  # Save checkpoint when pausing
            else:
                if self.pause_start_time is not None:
                    # Add the duration of this pause to total pause time
                    self.total_pause_time += time.time() - self.pause_start_time
                    self.pause_start_time = None
                logging.info("Resuming training...")
        except Exception as e:
            logging.error(f"Error in pause toggle: {e}")
            # Reset state in case of error
            self.paused = False
            self.pause_start_time = None

    def save_checkpoint(self):
        """Save current training state to a checkpoint file"""
        if not self.checkpoint_file:
            timestamp = datetime.now().strftime("%Y-%m-%d_%H_%M_%S")
            depth_str = f"depth_{self.depth}" if self.depth is not None else "full_game"
            self.checkpoint_file = os.path.join("ai", "models_checkpoints", f"checkpoint_{depth_str}_{timestamp}.pkl")
        
        # If we're paused, add the current pause time to total
        current_pause_time = 0
        if self.pause_start_time is not None:
            current_pause_time = time.time() - self.pause_start_time
        
        checkpoint_data = {
            'model': self.model,
            'trained_count': self.trained_count,
            'total_combinations': self.total_combinations,
            'positions_to_train': self.positions_to_train,
            'depth': self.depth,
            'start_time': self.start_time,
            'total_pause_time': self.total_pause_time + current_pause_time  # Include current pause time
        }
        
        os.makedirs(os.path.join("ai", "models_checkpoints"), exist_ok=True)
        with open(self.checkpoint_file, 'wb') as f:
            pickle.dump(checkpoint_data, f)
        logging.info(f"Checkpoint saved to {self.checkpoint_file}")
        self.last_save_time = time.time()

    def load_checkpoint(self, checkpoint_file):
        """Load training state from a checkpoint file"""
        try:
            with open(checkpoint_file, 'rb') as f:
                checkpoint_data = pickle.load(f)
            
            self.model = checkpoint_data['model']
            self.trained_count = checkpoint_data['trained_count']
            self.total_combinations = checkpoint_data['total_combinations']
            self.positions_to_train = checkpoint_data['positions_to_train']
            self.depth = checkpoint_data['depth']
            self.start_time = checkpoint_data['start_time']
            self.checkpoint_file = checkpoint_file
            
            logging.info(f"Loaded checkpoint from {checkpoint_file}")
            logging.info(f"Resuming from {self.trained_count}/{self.total_combinations} positions trained")
            return True
        except Exception as e:
            logging.error(f"Failed to load checkpoint: {e}")
            return False

    def setup_logging(self):
        log_dir = "ai/models_log"
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
        """Train the AI with pause/resume capability"""
        try:
            self.start_time = time.time()
            self.total_pause_time = 0  # Reset pause time for new training
            logging.info(f"Starting new training with depth {self.depth if self.depth is not None else 'full game'}")
            self.positions_to_train = self.generate_all_positions()
            self.total_combinations = len(self.positions_to_train)
            self.trained_count = 0
            logging.info(f"Total combinations/states to evaluate: {self.total_combinations}")

            # Rest of the training setup...
            ai_difficulty = "HARD"
            ai_max_depth_for_eval = min(self.depth, 4) if self.depth is not None else 3
            logging.info(f"AI evaluator initialized with max_depth: {ai_max_depth_for_eval}")

            cpu_count = os.cpu_count() or 4
            max_workers = max(1, int(cpu_count * 0.75))
            logging.info(f"Using {max_workers} worker threads for training (75% of {cpu_count} CPU cores)")

            with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
                future_to_board_player = {
                    executor.submit(self._evaluate_position, board, player_to_move, ai_difficulty, ai_max_depth_for_eval):
                    (board, player_to_move)
                    for board, player_to_move in self.positions_to_train
                }
                
                for future in tqdm(concurrent.futures.as_completed(future_to_board_player), 
                                 total=len(self.positions_to_train), 
                                 desc="Training positions"):
                    
                    # Check for pause state
                    while self.paused:
                        time.sleep(0.1)  # Shorter sleep for better responsiveness
                        continue

                    board, player_to_move = future_to_board_player[future]
                    try:
                        board_result, player_result, best_move = future.result()
                        board_key = self._board_to_key(board_result)
                        if board_key not in self.model:
                            self.model[board_key] = {}
                        self.model[board_key][player_result] = best_move
                        self.trained_count += 1
                        logging.debug(f"Board evaluation for Player {player_result} completed. Best Move: {best_move}")
                    except Exception as exc:
                        logging.error(f"Board {board} (Player {player_to_move}) generated an exception: {exc}")

            # Final save if not stopped
            self.save_model()
            # Only save checkpoint if we're actually paused
            if self.pause_start_time is not None:
                self.save_checkpoint()
            
            end_time = time.time()
            # Calculate actual training time by subtracting pause time
            actual_duration = end_time - self.start_time - self.total_pause_time
            formatted_duration = self._format_duration(actual_duration)
            formatted_pause = self._format_duration(self.total_pause_time)
            if self.total_pause_time > 0:
                logging.info(f"Training completed in {formatted_duration} (+ {formatted_pause} of pause time)")
            else:
                logging.info(f"Training completed in {formatted_duration}")

        except Exception as e:
            logging.error(f"Unexpected error during training: {e}")
            if self.pause_start_time is not None:
                self.total_pause_time += time.time() - self.pause_start_time
                self.save_checkpoint()
        finally:
            # Cleanup
            keyboard.unhook_all()

    def _board_to_key(self, board):
        """Convert board to a hashable key"""
        return tuple(map(tuple, board.astype(int)))

    def save_model(self):
        """Save the trained model"""
        model_dir = "ai/models"
        if not os.path.exists(model_dir):
            os.makedirs(model_dir)
        
        timestamp = datetime.now().strftime("%Y-%m-%d_%H_%M_%S")
        depth_str = f"depth_{self.depth}" if self.depth is not None else "full_game"
        filename = os.path.join(model_dir, f"model_{depth_str}_date_{timestamp}.pkl")
        
        with open(filename, 'wb') as f:
            pickle.dump(self.model, f)
        logging.info(f"Model saved to {filename}")

def main():
    """Main function to run the AI training"""
    print("""
=== ConnectX AI Training Program ===

Controls:
- Press Ctrl+Space to pause/resume training
- To stop the program:
  1. First pause the training using Ctrl+Space
  2. Then press Ctrl+C to stop and save

Note: Ctrl+C is disabled during active training to prevent data loss.
      You must pause the training first before stopping.

Starting training...
""")
    
    parser = argparse.ArgumentParser(description='Train AI for ConnectX')
    parser.add_argument('depth', type=int, nargs='?', help='Maximum depth for training (default: full game)')
    args = parser.parse_args()

    # Block Ctrl+C during execution
    def block_ctrl_c(signum, frame):
        if not trainer.paused:
            print("\nCtrl+C is disabled during active training.")
            print("Please pause the training first using Ctrl+Space, then press Ctrl+C to stop.")
            return
        # Only allow Ctrl+C when paused
        print("\nStopping training...")
        if trainer.pause_start_time is not None:
            trainer.total_pause_time += time.time() - trainer.pause_start_time
            trainer.save_checkpoint()
        keyboard.unhook_all()
        sys.exit(0)

    trainer = AITrainer(depth=args.depth)
    signal.signal(signal.SIGINT, block_ctrl_c)
    trainer.train()

if __name__ == "__main__":
    main() 