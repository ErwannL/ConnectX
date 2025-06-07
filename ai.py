import numpy as np
import random

class AI:
    def __init__(self, difficulty="MEDIUM"):
        self.difficulty = difficulty
        self.max_depth = 5  # For hard difficulty

    def get_move(self, board, player_piece):
        if self.difficulty == "EASY":
            return self._easy_move(board)
        elif self.difficulty == "MEDIUM":
            return self._medium_move(board, player_piece)
        else:  # HARD
            return self._hard_move(board, player_piece)

    def _easy_move(self, board):
        valid_locations = self._get_valid_locations(board)
        return random.choice(valid_locations)

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

        # If no winning or blocking move, choose randomly
        return random.choice(valid_locations)

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

    def _evaluate_window(self, board, piece):
        score = 0
        opponent_piece = 3 - piece

        # Score horizontal
        for r in range(6):
            row_array = [int(i) for i in list(board[r,:])]
            for c in range(4):
                window = row_array[c:c+4]
                score += self._evaluate_window_score(window, piece, opponent_piece)

        # Score vertical
        for c in range(7):
            col_array = [int(i) for i in list(board[:,c])]
            for r in range(3):
                window = col_array[r:r+4]
                score += self._evaluate_window_score(window, piece, opponent_piece)

        # Score positive diagonal
        for r in range(3):
            for c in range(4):
                window = [board[r+i][c+i] for i in range(4)]
                score += self._evaluate_window_score(window, piece, opponent_piece)

        # Score negative diagonal
        for r in range(3):
            for c in range(4):
                window = [board[r+3-i][c+i] for i in range(4)]
                score += self._evaluate_window_score(window, piece, opponent_piece)

        return score

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

    def _check_win(self, board, piece):
        # Check horizontal locations
        for c in range(4):
            for r in range(6):
                if board[r][c] == piece and board[r][c+1] == piece and board[r][c+2] == piece and board[r][c+3] == piece:
                    return True

        # Check vertical locations
        for c in range(7):
            for r in range(3):
                if board[r][c] == piece and board[r+1][c] == piece and board[r+2][c] == piece and board[r+3][c] == piece:
                    return True

        # Check positively sloped diagonals
        for c in range(4):
            for r in range(3):
                if board[r][c] == piece and board[r+1][c+1] == piece and board[r+2][c+2] == piece and board[r+3][c+3] == piece:
                    return True

        # Check negatively sloped diagonals
        for c in range(4):
            for r in range(3, 6):
                if board[r][c] == piece and board[r-1][c+1] == piece and board[r-2][c+2] == piece and board[r-3][c+3] == piece:
                    return True

        return False

    def _is_terminal_node(self, board):
        return self._check_win(board, 1) or self._check_win(board, 2) or len(self._get_valid_locations(board)) == 0 