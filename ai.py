import numpy as np
import random
import sys
import os
import time
from datetime import datetime
import threading
import queue
import logging
import pickle

class AI:
    def __init__(self, difficulty="EASY", model_file=None):
        self.difficulty = difficulty
        self.max_depth = 3  # Default depth
        self.model = None
        self.model_file = model_file
        
        if model_file:
            self.load_model(model_file)
        
        # Setup logging
        self.setup_logging()
        
        # Initialize thinking thread
        self.thinking_thread = None
        self.calculated_move = None
        self.is_thinking = False
        self.thinking_lock = threading.Lock()
        self.thinking_event = threading.Event()
        self.calculation_board = None
        self.board_drawing_params = None
        self.log_file = None
        self.log_queue = queue.Queue()
        self.log_thread = None
        self.move_queue = queue.Queue()
        self.stop_event = threading.Event()
        self.current_move = None  # Store the current move being calculated

    def start_new_game(self):
        """Initialize logging for a new game"""
        if self.difficulty == "HARD":
            self.setup_logging()
            # Start logging thread
            self.stop_event.clear()
            self.log_thread = threading.Thread(target=self._logging_worker, daemon=True)
            self.log_thread.start()

    def stop_game(self):
        """Stop all threads and cleanup"""
        self.stop_event.set()
        if self.log_thread:
            self.log_thread.join()
        if self.thinking_thread:
            self.thinking_thread.join()

    def _logging_worker(self):
        """Worker thread for handling log writes"""
        while not self.stop_event.is_set():
            try:
                log_entry = self.log_queue.get(timeout=0.1)
                with open(self.log_file, 'a') as f:
                    f.write(log_entry)
            except queue.Empty:
                continue

    def setup_logging(self):
        log_dir = "ai_logs"
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.log_file = os.path.join(log_dir, f"ai_thinking_{timestamp}.txt")
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(self.log_file),
                logging.StreamHandler()
            ]
        )

    def load_model(self, model_file):
        """Load a trained model from file"""
        try:
            with open(model_file, 'rb') as f:
                self.model = pickle.load(f)
            logging.info(f"Loaded model from {model_file}")
        except Exception as e:
            logging.error(f"Error loading model: {e}")
            self.model = None

    def get_move(self, board, player):
        """Get the best move for the current board state"""
        if self.model:
            return self._get_model_move(board, player)
        
        if self.difficulty == "EASY":
            return self._easy_move(board)
        elif self.difficulty == "MEDIUM":
            return self._medium_move(board, player)
        else:  # HARD
            return self._hard_move(board, player)

    def _get_model_move(self, board, player):
        """Get move from trained model"""
        board_key = tuple(map(tuple, board))
        if board_key in self.model and player in self.model[board_key]:
            return self.model[board_key][player]
        # Fallback to random move if position not in model
        return self._easy_move(board)

    def _easy_move(self, board):
        """Make a random valid move"""
        valid_moves = [col for col in range(7) if board[0][col] == 0]
        return random.choice(valid_moves) if valid_moves else 0

    def _medium_move(self, board, player):
        """Make a move that either wins or blocks opponent's win"""
        # Check for winning move
        for col in range(7):
            if self._is_valid_move(board, col):
                temp_board = board.copy()
                self._make_move(temp_board, col, player)
                if self._check_win(temp_board, player):
                    return col

        # Check for blocking move
        opponent = 3 - player
        for col in range(7):
            if self._is_valid_move(board, col):
                temp_board = board.copy()
                self._make_move(temp_board, col, opponent)
                if self._check_win(temp_board, opponent):
                    return col

        # If no winning or blocking move, make a random move
        return self._easy_move(board)

    def _hard_move(self, board, player):
        """Make the best move using minimax algorithm"""
        best_score = float('-inf')
        best_move = None
        alpha = float('-inf')
        beta = float('inf')

        for col in range(7):
            if self._is_valid_move(board, col):
                temp_board = board.copy()
                self._make_move(temp_board, col, player)
                score = self._minimax(temp_board, self.max_depth, False, player, alpha, beta)
                
                if score > best_score:
                    best_score = score
                    best_move = col

        return best_move if best_move is not None else self._easy_move(board)

    def _minimax(self, board, depth, is_maximizing, player, alpha, beta):
        """Minimax algorithm with alpha-beta pruning"""
        opponent = 3 - player
        valid_moves = [col for col in range(7) if self._is_valid_move(board, col)]

        if depth == 0 or not valid_moves or self._check_win(board, player) or self._check_win(board, opponent):
            return self._evaluate_board(board, player)

        if is_maximizing:
            max_eval = float('-inf')
            for col in valid_moves:
                temp_board = board.copy()
                self._make_move(temp_board, col, player)
                eval = self._minimax(temp_board, depth - 1, False, player, alpha, beta)
                max_eval = max(max_eval, eval)
                alpha = max(alpha, eval)
                if beta <= alpha:
                    break
            return max_eval
        else:
            min_eval = float('inf')
            for col in valid_moves:
                temp_board = board.copy()
                self._make_move(temp_board, col, opponent)
                eval = self._minimax(temp_board, depth - 1, True, player, alpha, beta)
                min_eval = min(min_eval, eval)
                beta = min(beta, eval)
                if beta <= alpha:
                    break
            return min_eval

    def _evaluate_board(self, board, player):
        """Evaluate the board state for the given player"""
        opponent = 3 - player
        score = 0

        # Check horizontal
        for r in range(6):
            for c in range(4):
                window = board[r, c:c+4]
                score += self._evaluate_window(window, player, opponent)

        # Check vertical
        for r in range(3):
            for c in range(7):
                window = board[r:r+4, c]
                score += self._evaluate_window(window, player, opponent)

        # Check diagonal (positive slope)
        for r in range(3):
            for c in range(4):
                window = [board[r+i][c+i] for i in range(4)]
                score += self._evaluate_window(window, player, opponent)

        # Check diagonal (negative slope)
        for r in range(3):
            for c in range(4):
                window = [board[r+3-i][c+i] for i in range(4)]
                score += self._evaluate_window(window, player, opponent)

        return score

    def _evaluate_window(self, window, player, opponent):
        """Evaluate a window of 4 positions"""
        score = 0
        player_count = np.count_nonzero(window == player)
        opponent_count = np.count_nonzero(window == opponent)
        empty_count = np.count_nonzero(window == 0)

        if player_count == 4:
            score += 100
        elif player_count == 3 and empty_count == 1:
            score += 5
        elif player_count == 2 and empty_count == 2:
            score += 2

        if opponent_count == 3 and empty_count == 1:
            score -= 4

        return score

    def _is_valid_move(self, board, col):
        """Check if a move is valid"""
        return board[0][col] == 0

    def _make_move(self, board, col, player):
        """Make a move on the board"""
        for row in range(5, -1, -1):
            if board[row][col] == 0:
                board[row][col] = player
                break

    def _check_win(self, board, player):
        """Check if the player has won"""
        # Check horizontal
        for r in range(6):
            for c in range(4):
                if all(board[r][c+i] == player for i in range(4)):
                    return True

        # Check vertical
        for r in range(3):
            for c in range(7):
                if all(board[r+i][c] == player for i in range(4)):
                    return True

        # Check diagonal (positive slope)
        for r in range(3):
            for c in range(4):
                if all(board[r+i][c+i] == player for i in range(4)):
                    return True

        # Check diagonal (negative slope)
        for r in range(3):
            for c in range(4):
                if all(board[r+3-i][c+i] == player for i in range(4)):
                    return True

        return False

    def log_board_state(self, board, message=""):
        if not self.log_file:
            return
        log_entry = f"\n{message}\n"
        log_entry += "Current Board State:\n"
        # Print board from top to bottom
        for row in reversed(board):
            # Convert 1.0 to O and 2.0 to X
            row_str = " ".join(['O' if x == 1 else 'X' if x == 2 else '.' for x in row])
            log_entry += row_str + "\n"
        log_entry += "\n"
        self.log_queue.put(log_entry)

    def log_move_evaluation(self, col, depth, score, is_maximizing):
        if not self.log_file:
            return
        log_entry = f"Evaluating move at column {col} (depth {depth}, {'maximizing' if is_maximizing else 'minimizing'}):\n"
        log_entry += f"Score: {score}\n"
        self.log_queue.put(log_entry)

    def set_drawing_params(self, params):
        self.board_drawing_params = params

    def _thinking_worker(self, board, player_piece):
        """Worker thread for AI thinking"""
        try:
            if self.difficulty == "EASY":
                move = self._easy_move(board)
            elif self.difficulty == "MEDIUM":
                move = self._medium_move(board, player_piece)
            else:  # HARD
                move = self._hard_move(board, player_piece)
            
            # Put the result in the queue
            self.move_queue.put(move)
        except Exception as e:
            logging.error(f"Error in AI thinking: {e}")
            # Put a random valid move in case of error
            valid_locations = self._get_valid_locations(board)
            self.move_queue.put(random.choice(valid_locations))

    def _get_valid_locations(self, board):
        valid_locations = []
        for col in range(7):
            if self._is_valid_location(board, col):
                valid_locations.append(col)
        return valid_locations

    def _is_valid_location(self, board, col):
        return board[5][col] == 0

    def _get_next_open_row(self, board, col):
        for r in range(6):
            if board[r][col] == 0:
                return r

    def _is_terminal_node(self, board):
        return self._check_win(board, 1) or self._check_win(board, 2) or len(self._get_valid_locations(board)) == 0 