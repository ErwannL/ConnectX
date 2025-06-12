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
import torch
import torch.nn as nn
import torch.nn.functional as F
from concurrent.futures import ThreadPoolExecutor
from settings import Settings

class Connect4Net(nn.Module):
    def __init__(self):
        super(Connect4Net, self).__init__()
        self.conv1 = nn.Conv2d(1, 64, kernel_size=3, padding=1)
        self.conv2 = nn.Conv2d(64, 128, kernel_size=3, padding=1)
        self.conv3 = nn.Conv2d(128, 128, kernel_size=3, padding=1)
        self.fc1 = nn.Linear(128 * 6 * 7, 256)
        self.fc2 = nn.Linear(256, 7)  # 7 outputs for each column

    def forward(self, x):
        x = F.relu(self.conv1(x))
        x = F.relu(self.conv2(x))
        x = F.relu(self.conv3(x))
        x = x.view(-1, 128 * 6 * 7)
        x = F.relu(self.fc1(x))
        x = self.fc2(x)
        return x

class AI:
    def __init__(self, difficulty="HARD", debug_mode=False, is_in_game=True):
        self.difficulty = difficulty
        self.debug_mode = debug_mode
        self.depth = 6  # Augmenté de 4 à 6 par défaut
        self.win_score = 1000000
        self.block_score = 500000
        self.center_bonus = 100  # Ajout d'un bonus pour le contrôle du centre
        self.model = None
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.thread_pool = ThreadPoolExecutor(max_workers=os.cpu_count() or 4)
        self.board_drawing_params = None
        self.is_in_game = is_in_game
        
        # Initialize logger
        self.logger = logging.getLogger('ai_reflection')
        
        # Load neural network model if available and if in game mode
        if is_in_game:
            try:
                # Chercher le modèle avec la plus grande profondeur dans le dossier models
                model_dir = "ai/models"
                if os.path.exists(model_dir):
                    model_files = [f for f in os.listdir(model_dir) if f.endswith('.pkl')]
                    if model_files:
                        # Extraire la profondeur de chaque fichier et trier
                        def get_depth_and_time(filename):
                            try:
                                # Extraire la profondeur du nom de fichier (model_depth_X_date_...)
                                depth = int(filename.split('depth_')[1].split('_')[0])
                                # Obtenir la date de modification
                                mtime = os.path.getmtime(os.path.join(model_dir, filename))
                                return (depth, mtime)
                            except:
                                return (0, 0)  # En cas d'erreur, considérer comme profondeur 0
                        
                        # Trier d'abord par profondeur (descendant), puis par date (descendant)
                        model_files.sort(key=get_depth_and_time, reverse=True)
                        model_path = os.path.join(model_dir, model_files[0])
                        
                        # Extraire la profondeur du modèle choisi
                        depth = get_depth_and_time(model_files[0])[0]
                        self.logger.info(f"Loading model with highest depth ({depth}): {model_path}")
                        
                        # Charger le modèle pickle
                        with open(model_path, 'rb') as f:
                            self.model = pickle.load(f)
                        self.logger.info(f"Neural network model loaded successfully (depth: {depth})")
                    else:
                        self.logger.warning("No neural network model found in models directory")
                else:
                    self.logger.warning("Models directory not found")
            except Exception as e:
                self.logger.warning(f"Could not load neural network model: {e}. Using heuristic evaluation only.")
                self.model = None

    def _log_board_state(self, board, player):
        """Log the current board state in a readable format (DEBUG level)"""
        if self.debug_mode:
            board_str = "\n"
            # Print board from bottom to top (row 0 is bottom)
            for row in range(5, -1, -1):
                row_str = "|"
                for col in range(7):
                    if board[row][col] == 0:
                        row_str += " "
                    elif board[row][col] == 1:
                        row_str += "X"
                    else:
                        row_str += "O"
                    row_str += "|"
                board_str += row_str + "\n"
            board_str += "+-+-+-+-+-+-+-+\n"
            board_str += " 0 1 2 3 4 5 6 "
            self.logger.debug(f"Current board state (Player {player}'s turn):{board_str}")

    def _log_move_evaluation(self, col, score, depth):
        """Log AI move evaluation details (DEBUG level)"""
        if self.debug_mode:
            if isinstance(score, (np.ndarray, torch.Tensor)):
                score = float(score.mean())
            self.logger.debug(f"Move evaluation: column {col} with score {score:.2f} at depth {depth}")

    def get_move(self, board, player):
        """Get the best move for the current board state"""
        self._log_board_state(board, player)
        
        try:
            if self.difficulty == "EASY":
                move = self._easy_move(board)
                if self.is_in_game:
                    self.logger.info(f"Easy AI chose column {move}")
            elif self.difficulty == "MEDIUM":
                move = self._medium_move(board, player)
                if self.is_in_game:
                    self.logger.info(f"Medium AI chose column {move}")
            else:  # HARD
                # Use minimax with neural network evaluation for final decision
                move, score = self._hard_move(board, player)
                self._log_move_evaluation(move, score, self.depth)
                if self.is_in_game:
                    self.logger.info(f"Hard AI chose column {move} (depth: {self.depth})")
            
            # Validate move before returning
            if move is None or not self._is_valid_location(board, move):
                self.logger.warning(f"AI generated invalid move: {move}, choosing random valid move instead")
                valid_locations = self._get_valid_locations(board)
                if valid_locations:
                    move = random.choice(valid_locations)
                    if self.debug_mode:
                        self.logger.debug(f"Selected random valid move: {move}")
                else:
                    self.logger.error("No valid moves available!")
                    move = 0
            
            return move
            
        except Exception as e:
            self.logger.error(f"Error in AI move calculation: {e}")
            # En cas d'erreur, retourne un coup valide par défaut
            valid_locations = self._get_valid_locations(board)
            if valid_locations:
                return random.choice(valid_locations)
            return 0

    def _hard_move(self, board, player, depth=None):
        """Stratégie améliorée pour le niveau difficile"""
        if depth is None:
            depth = self.depth
        
        try:
            # 1. Vérifier les coups gagnants immédiats
            for col in range(7):
                if self._is_valid_move(board, col):
                    temp_board = board.copy()
                    if self._make_move(temp_board, col, player):
                        if self._check_win(temp_board, player):
                            self._log_move_evaluation(col, self.win_score, depth)
                            return col, self.win_score
            
            # 2. Bloquer les coups gagnants de l'adversaire
            opponent = 3 - player
            for col in range(7):
                if self._is_valid_move(board, col):
                    temp_board = board.copy()
                    if self._make_move(temp_board, col, opponent):
                        if self._check_win(temp_board, opponent):
                            self._log_move_evaluation(col, self.block_score, depth)
                            return col, self.block_score
            
            # 3. Utiliser minimax avec évaluation parallèle pour les autres coups
            valid_moves = self._get_valid_locations(board)
            if not valid_moves:
                self.logger.warning("No valid moves available!")
                return 0, 0
            
            # Log de la réflexion complète (uniquement en mode dev)
            if self.debug_mode:
                self.logger.debug(f"AI reflection for player {player}:")
                self.logger.debug(f"Valid moves: {valid_moves}")
            
            # Évaluation parallèle des coups
            futures = []
            for col in valid_moves:
                temp_board = board.copy()
                if self._make_move(temp_board, col, player):
                    futures.append(self.thread_pool.submit(
                        self._minimax, temp_board, depth-1, float('-inf'), float('inf'), False, player
                    ))
            
            # Attendre les résultats et trouver le meilleur coup
            best_score = float('-inf')
            best_move = valid_moves[0]
            
            for i, future in enumerate(futures):
                try:
                    score = future.result(timeout=5.0)  # Augmenté à 5 secondes par coup
                    col = valid_moves[i]
                    if score > best_score:
                        best_score = score
                        best_move = col
                    if self.debug_mode:
                        self.logger.debug(f"Column {col} evaluated with score {score:.2f}")
                except Exception as e:
                    self.logger.error(f"Error evaluating move {valid_moves[i]}: {e}")
                    # En cas d'erreur sur un coup, on continue avec les autres
                    continue
            
            if best_score == float('-inf'):
                # Si tous les coups ont échoué, on prend le premier coup valide
                self.logger.warning("All moves failed evaluation, using first valid move")
                return valid_moves[0], 0
            
            if self.is_in_game:
                self.logger.info(f"Best move found: column {best_move} with score {best_score:.2f}")
            return best_move, best_score
            
        except Exception as e:
            self.logger.error(f"Error in hard move calculation: {e}")
            valid_moves = self._get_valid_locations(board)
            if valid_moves:
                return valid_moves[0], 0
            return 0, 0

    def _minimax(self, board, depth, alpha, beta, is_maximizing, player):
        """Minimax algorithm with alpha-beta pruning and neural network evaluation"""
        opponent = 3 - player
        valid_moves = [col for col in range(7) if self._is_valid_move(board, col)]

        if depth == 0 or not valid_moves or self._check_win(board, player) or self._check_win(board, opponent):
            # Use neural network for evaluation at leaf nodes
            return self._evaluate_position_with_nn(board, player)

        if is_maximizing:
            max_eval = float('-inf')
            for col in valid_moves:
                temp_board = board.copy()
                self._make_move(temp_board, col, player)
                eval = self._minimax(temp_board, depth - 1, alpha, beta, False, player)
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
                eval = self._minimax(temp_board, depth - 1, alpha, beta, True, player)
                min_eval = min(min_eval, eval)
                beta = min(beta, eval)
                if beta <= alpha:
                    break
            return min_eval

    def _evaluate_position_with_nn(self, board, player):
        """Evaluate position using neural network and heuristic evaluation"""
        # Score de base du réseau de neurones
        nn_score = 0
        if self.model is not None:
            try:
                # Convertir le board en clé pour le modèle pickle
                board_key = tuple(map(tuple, np.array(board).astype(int)))
                if board_key in self.model and player in self.model[board_key]:
                    # Le modèle pickle contient directement le meilleur coup
                    best_move = self.model[board_key][player]
                    # Calculer un score basé sur la qualité du coup
                    nn_score = self._evaluate_move_quality(board, best_move, player)
            except Exception as e:
                self.logger.warning(f"Neural network evaluation failed: {e}. Falling back to heuristic only.")
                nn_score = 0

        # Score heuristique
        heuristic_score = self._evaluate_heuristic(board, player)
        
        # Si le modèle n'est pas disponible, utiliser uniquement l'heuristique
        if self.model is None:
            return heuristic_score
        
        # Combiner les scores avec plus de poids sur l'heuristique (70% heuristique, 30% NN)
        return 0.7 * heuristic_score + 0.3 * nn_score

    def _evaluate_move_quality(self, board, move, player):
        """Évalue la qualité d'un coup basé sur sa position et son impact"""
        if not self._is_valid_move(board, move):
            return -1000  # Coup invalide = très mauvais score
            
        # Copier le board et faire le coup
        temp_board = board.copy()
        if not self._make_move(temp_board, move, player):
            return -1000
            
        # Vérifier si c'est un coup gagnant
        if self._check_win(temp_board, player):
            return 1000
            
        # Vérifier si ça bloque un coup gagnant de l'adversaire
        opponent = 3 - player
        if self._check_win(temp_board, opponent):
            return 500
            
        # Bonus pour le centre
        if move in [3, 4]:  # Colonnes centrales
            return 100
            
        # Bonus pour les alignements
        score = 0
        # Vérifier les alignements horizontaux
        for r in range(6):
            for c in range(4):
                window = temp_board[r, c:c+4]
                if np.count_nonzero(window == player) == 3 and np.count_nonzero(window == 0) == 1:
                    score += 50
                elif np.count_nonzero(window == player) == 2 and np.count_nonzero(window == 0) == 2:
                    score += 10
                    
        # Vérifier les alignements verticaux
        for c in range(7):
            for r in range(3):
                window = temp_board[r:r+4, c]
                if np.count_nonzero(window == player) == 3 and np.count_nonzero(window == 0) == 1:
                    score += 50
                elif np.count_nonzero(window == player) == 2 and np.count_nonzero(window == 0) == 2:
                    score += 10
                    
        # Vérifier les alignements diagonaux
        for r in range(3):
            for c in range(4):
                window = [temp_board[r+i][c+i] for i in range(4)]
                if np.count_nonzero(window == player) == 3 and np.count_nonzero(window == 0) == 1:
                    score += 50
                elif np.count_nonzero(window == player) == 2 and np.count_nonzero(window == 0) == 2:
                    score += 10
                    
                window = [temp_board[r+3-i][c+i] for i in range(4)]
                if np.count_nonzero(window == player) == 3 and np.count_nonzero(window == 0) == 1:
                    score += 50
                elif np.count_nonzero(window == player) == 2 and np.count_nonzero(window == 0) == 2:
                    score += 10
                    
        return score

    def _evaluate_heuristic(self, board, player):
        """Évaluation heuristique améliorée avec focus sur la victoire et le blocage"""
        score = 0
        opponent = 3 - player
        
        # Vérification des alignements de 2, 3 et 4 pièces avec des scores plus agressifs
        for piece in [player, opponent]:
            # Alignements horizontaux
            for r in range(6):
                for c in range(4):
                    window = [board[r][c+i] for i in range(4)]
                    score += self._evaluate_window(window, piece, player)
            
            # Alignements verticaux
            for c in range(7):
                for r in range(3):
                    window = [board[r+i][c] for i in range(4)]
                    score += self._evaluate_window(window, piece, player)
            
            # Alignements diagonaux positifs
            for r in range(3):
                for c in range(4):
                    window = [board[r+i][c+i] for i in range(4)]
                    score += self._evaluate_window(window, piece, player)
            
            # Alignements diagonaux négatifs
            for r in range(3, 6):
                for c in range(4):
                    window = [board[r-i][c+i] for i in range(4)]
                    score += self._evaluate_window(window, piece, player)
        
        # Bonus pour le contrôle du centre (colonnes 3, 4)
        center_columns = [3, 4]
        for col in center_columns:
            for r in range(6):
                if board[r][col] == player:
                    score += self.center_bonus
                elif board[r][col] == opponent:
                    score -= self.center_bonus
        
        return score

    def _evaluate_window(self, window, piece, player):
        """Évaluation d'une fenêtre de 4 cases avec des scores plus agressifs"""
        score = 0
        opponent = 3 - piece
        
        # Score pour 4 pièces alignées (victoire)
        if window.count(piece) == 4:
            score += self.win_score if piece == player else -self.win_score
        
        # Score pour 3 pièces alignées avec une case vide
        elif window.count(piece) == 3 and window.count(0) == 1:
            score += 1000 if piece == player else -1000
        
        # Score pour 2 pièces alignées avec deux cases vides
        elif window.count(piece) == 2 and window.count(0) == 2:
            score += 100 if piece == player else -100
        
        # Pénalité pour les coups qui permettent à l'adversaire de gagner
        if window.count(opponent) == 3 and window.count(0) == 1:
            score -= self.block_score if piece == player else self.block_score
        
        return score

    def _minimax_move(self, board, player, depth):
        """Algorithme minimax optimisé avec évaluation parallèle"""
        valid_moves = [col for col in range(7) if self._is_valid_move(board, col)]
        if not valid_moves:
            return None, 0
        
        # Évaluation parallèle des coups
        futures = []
        for col in valid_moves:
            temp_board = board.copy()
            if self._make_move(temp_board, col, player):
                futures.append(self.thread_pool.submit(
                    self._minimax, temp_board, depth-1, float('-inf'), float('inf'), False, player
                ))
        
        # Attendre les résultats et trouver le meilleur coup
        best_score = float('-inf')
        best_move = valid_moves[0]
        
        for col, future in zip(valid_moves, futures):
            try:
                score = future.result(timeout=2.0)  # Timeout de 2 secondes par coup
                if score > best_score:
                    best_score = score
                    best_move = col
            except TimeoutError:
                continue
        
        return best_move, best_score

    def _easy_move(self, board):
        """Make a random valid move"""
        valid_moves = [col for col in range(7) if self._is_valid_move(board, col)]
        return random.choice(valid_moves) if valid_moves else 0

    def _medium_move(self, board, player):
        """Make a move that either wins or blocks opponent's win, otherwise random"""
        self.logger.debug(f"Medium AI reflection for player {player}:")
        
        # 1. Check for winning move
        for col in range(7):
            if self._is_valid_move(board, col):
                temp_board = board.copy()
                if self._make_move(temp_board, col, player):
                    if self._check_win(temp_board, player):
                        self.logger.debug(f"Medium AI found winning move in column {col}")
                        return col

        # 2. Check for blocking move
        opponent = 3 - player
        for col in range(7):
            if self._is_valid_move(board, col):
                temp_board = board.copy()
                if self._make_move(temp_board, col, opponent):
                    if self._check_win(temp_board, opponent):
                        self.logger.debug(f"Medium AI found blocking move in column {col}")
                        return col

        # 3. If no winning or blocking move, make a random move
        valid_moves = self._get_valid_locations(board)
        if valid_moves:
            move = random.choice(valid_moves)
            self.logger.debug(f"Medium AI chose random move in column {move}")
            return move
        
        self.logger.warning("No valid moves available for Medium AI")
        return 0

    def _board_to_tensor(self, board, player):
        """Convert board state to neural network input tensor"""
        try:
            # Create a 6x7x1 tensor where 1 represents player's pieces, -1 represents opponent's pieces
            tensor = np.zeros((1, 1, 6, 7), dtype=np.float32)
            for r in range(6):
                for c in range(7):
                    if board[r][c] == player:
                        tensor[0, 0, r, c] = 1
                    elif board[r][c] == 3 - player:
                        tensor[0, 0, r, c] = -1
            return torch.FloatTensor(tensor)
        except Exception as e:
            self.logger.error(f"Error converting board to tensor: {e}")
            # Return a zero tensor as fallback
            return torch.zeros((1, 1, 6, 7), dtype=torch.float32)

    def _is_valid_move(self, board, col):
        """Vérifie si un coup est valide dans la colonne donnée."""
        # Vérifie si la colonne est dans les limites
        if col < 0 or col >= 7:
            return False
        # Vérifie si la colonne n'est pas pleine (la case du bas doit être vide)
        return board[-1][col] == 0  # Utilise la dernière ligne au lieu de la première

    def _get_neural_network_move(self, board, player):
        """Get move prediction from neural network"""
        self.model.eval()
        with torch.no_grad():
            board_tensor = self._board_to_tensor(board, player)
            output = self.model(board_tensor)
            # Mask invalid moves
            valid_moves = [col for col in range(7) if self._is_valid_move(board, col)]
            if not valid_moves:
                return 0
            # Convert output to probabilities and mask invalid moves
            probs = F.softmax(output, dim=1)[0]
            for col in range(7):
                if col not in valid_moves:
                    probs[col] = float('-inf')
            return torch.argmax(probs).item()

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
                move, score = self._hard_move(board, player_piece)
            
            # Put the result in the queue
            self.move_queue.put((move, score))
        except Exception as e:
            logging.error(f"Error in AI thinking: {e}")
            # Put a random valid move in case of error
            valid_locations = self._get_valid_locations(board)
            self.move_queue.put((random.choice(valid_locations), 0))

    def _get_valid_locations(self, board):
        """Retourne la liste des colonnes où un coup est possible"""
        valid_locations = []
        for col in range(7):
            if self._is_valid_move(board, col):
                valid_locations.append(col)
        return valid_locations

    def _is_valid_location(self, board, col):
        """Vérifie si une colonne est valide pour jouer"""
        return self._is_valid_move(board, col)

    def _get_next_open_row(self, board, col):
        """Trouve la première ligne vide en partant du bas"""
        for r in range(len(board)-1, -1, -1):  # Parcourt de bas en haut
            if board[r][col] == 0:
                return r
        return None

    def _is_terminal_node(self, board):
        return self._check_win(board, 1) or self._check_win(board, 2) or len(self._get_valid_locations(board)) == 0

    def _check_win(self, board, piece):
        """Vérifie si le joueur a gagné"""
        # Vérification horizontale
        for c in range(7-3):
            for r in range(6):
                if all(board[r][c+i] == piece for i in range(4)):
                    return True

        # Vérification verticale
        for c in range(7):
            for r in range(6-3):
                if all(board[r+i][c] == piece for i in range(4)):
                    return True

        # Vérification diagonale positive
        for c in range(7-3):
            for r in range(6-3):
                if all(board[r+i][c+i] == piece for i in range(4)):
                    return True

        # Vérification diagonale négative
        for c in range(7-3):
            for r in range(3, 6):
                if all(board[r-i][c+i] == piece for i in range(4)):
                    return True

        return False

    def _make_move(self, board, col, player):
        """Place une pièce dans la colonne spécifiée"""
        row = self._get_next_open_row(board, col)
        if row is not None:
            board[row][col] = player
            return True
        return False

    def _drop_piece(self, board, row, col, player):
        """Drop a piece into the board"""
        board[row][col] = player

    def _is_valid_location(self, board, col):
        return board[5][col] == 0

    def _get_next_open_row(self, board, col):
        for r in range(6):
            if board[r][col] == 0:
                return r

    def _is_terminal_node(self, board):
        return self._check_win(board, 1) or self._check_win(board, 2) or len(self._get_valid_locations(board)) == 0 