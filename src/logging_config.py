import logging
import os
from datetime import datetime
from pathlib import Path
from settings import Settings
import sys

def setup_logging(dev_mode=False):
    """Configure le système de logging avec différents niveaux selon le mode dev"""
    
    # Utiliser le répertoire courant comme workspace
    workspace_path = os.getcwd()
    print(f"Current working directory: {workspace_path}")
    
    # Créer les dossiers de logs s'ils n'existent pas
    log_dir = os.path.join(workspace_path, 'logs')
    ai_log_dir = os.path.join(log_dir, 'ai_reflection')
    game_log_dir = os.path.join(log_dir, 'game')
    
    # Créer les dossiers avec leurs parents si nécessaire
    for directory in [log_dir, ai_log_dir, game_log_dir]:
        try:
            os.makedirs(directory, exist_ok=True)
            print(f"Created/verified directory: {directory}")
        except Exception as e:
            print(f"Error creating directory {directory}: {e}")
            raise

    # Timestamp pour les noms de fichiers
    timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    
    # Configuration de base pour la console (toujours en mode dev pour la console)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.DEBUG if dev_mode else logging.INFO)
    console_formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    console_handler.setFormatter(console_formatter)
    
    # Configuration du logger root
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG if dev_mode else logging.INFO)
    # Supprimer tous les handlers existants
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    root_logger.addHandler(console_handler)

    # Logger pour l'IA
    ai_logger = logging.getLogger('ai_reflection')
    ai_logger.setLevel(logging.DEBUG if dev_mode else logging.INFO)
    ai_logger.propagate = False  # Empêche la propagation vers le logger root
    # Supprimer tous les handlers existants
    for handler in ai_logger.handlers[:]:
        ai_logger.removeHandler(handler)
    
    # Fichier de log pour l'IA
    ai_log_path = os.path.join(ai_log_dir, f'game_{timestamp}.log')
    try:
        ai_file_handler = logging.FileHandler(ai_log_path, mode='w', encoding='utf-8')
        # En mode normal, on ne garde que les messages INFO (best move et colonne)
        # En mode dev, on garde aussi les messages DEBUG (réflexion)
        ai_file_handler.setLevel(logging.DEBUG if dev_mode else logging.INFO)
        ai_file_handler.setFormatter(logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        ))
        ai_logger.addHandler(ai_file_handler)
        print(f"Created AI log file: {ai_log_path}")
    except Exception as e:
        print(f"Error creating AI log file {ai_log_path}: {e}")
        raise
    
    # Logger pour le jeu
    game_logger = logging.getLogger('game')
    game_logger.setLevel(logging.DEBUG if dev_mode else logging.INFO)
    game_logger.propagate = False  # Empêche la propagation vers le logger root
    # Supprimer tous les handlers existants
    for handler in game_logger.handlers[:]:
        game_logger.removeHandler(handler)
    
    # Fichier de log pour le jeu
    game_log_path = os.path.join(game_log_dir, f'connectX_{timestamp}.log')
    try:
        game_file_handler = logging.FileHandler(game_log_path, mode='w', encoding='utf-8')
        # En mode normal, on ne garde que les messages INFO (état du jeu)
        # En mode dev, on garde aussi les messages DEBUG (menus, etc.)
        game_file_handler.setLevel(logging.DEBUG if dev_mode else logging.INFO)
        game_file_handler.setFormatter(logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        ))
        game_logger.addHandler(game_file_handler)
        print(f"Created game log file: {game_log_path}")
    except Exception as e:
        print(f"Error creating game log file {game_log_path}: {e}")
        raise

    # Message de confirmation
    if dev_mode:
        print("Logging system initialized in DEV mode")
        ai_logger.debug("AI reflection logging initialized in DEV mode (DEBUG level enabled)")
        game_logger.debug("Game logging initialized in DEV mode (DEBUG level enabled)")
    else:
        print("Logging system initialized successfully")
        ai_logger.info("AI reflection logging initialized (INFO level only)")
        game_logger.info("Game logging initialized (INFO level only)")

    return ai_logger, game_logger

class GameLogger:
    def __init__(self, dev_mode=False):
        self.dev_mode = dev_mode
        self.settings = Settings()
        
        # Create logs/game directory if it doesn't exist
        log_dir = os.path.join("logs", "game")
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
            
        # Create logs/ai_reflection directory if it doesn't exist
        ai_log_dir = os.path.join("logs", "ai_reflection")
        if not os.path.exists(ai_log_dir):
            os.makedirs(ai_log_dir)
            
        # Generate timestamp for both log files
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        
        # Setup game logger
        self.logger = logging.getLogger('game')
        self.logger.setLevel(logging.DEBUG if dev_mode else logging.INFO)
        
        # Game log file
        log_file = os.path.join(log_dir, f"connectX_{timestamp}.log")
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.DEBUG if dev_mode else logging.INFO)
        file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
        self.logger.addHandler(file_handler)
        
        # Console handler (only in dev mode)
        if dev_mode:
            console_handler = logging.StreamHandler()
            console_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
            self.logger.addHandler(console_handler)
        
        # Setup AI reflection logger
        self.ai_logger = logging.getLogger('ai_reflection')
        self.ai_logger.setLevel(logging.DEBUG if dev_mode else logging.INFO)
        
        # AI reflection log file
        ai_log_file = os.path.join(ai_log_dir, f"game_{timestamp}.log")
        ai_file_handler = logging.FileHandler(ai_log_file)
        ai_file_handler.setLevel(logging.DEBUG if dev_mode else logging.INFO)
        ai_file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
        self.ai_logger.addHandler(ai_file_handler)
        
        # AI console handler (only in dev mode)
        if dev_mode:
            ai_console_handler = logging.StreamHandler()
            ai_console_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
            self.ai_logger.addHandler(ai_console_handler)

    def log_board_state(self, board, player):
        """Log l'état du plateau (niveau INFO)"""
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
        self.logger.info(f"Current board state (Player {player}'s turn):{board_str}")

    def log_player_move(self, column, player):
        """Log le coup du joueur (niveau INFO)"""
        self.logger.info(f"Player {player} chose column {column}")

    def log_ai_move(self, column, difficulty, depth=None):
        """Log le coup de l'IA (niveau INFO)"""
        if depth:
            self.logger.info(f"{difficulty} AI chose column {column} (depth: {depth})")
        else:
            self.logger.info(f"{difficulty} AI chose column {column}")

    def log_menu_event(self, menu_name, button_name):
        """Log les événements de menu (niveau DEBUG)"""
        if self.dev_mode:
            self.logger.debug(f"Menu: {menu_name} - Button pressed: {button_name}")

    def log_ai_thinking(self, message):
        """Log la réflexion de l'IA"""
        if self.dev_mode:
            # En mode dev, on log tout en DEBUG
            self.ai_logger.debug(message)
        else:
            # En mode normal, on ne garde que les messages de type "Best move found" et "AI chose column"
            if "Best move found" in message or "AI chose column" in message:
                self.ai_logger.info(message)

class TrainingLogger:
    def __init__(self, depth):
        self.logger = logging.getLogger('ConnectX_Training')
        self.logger.setLevel(logging.INFO)
        
        # Créer le dossier training_ai s'il n'existe pas
        self.log_dir = Path('ai/models_log')
        self.log_dir.mkdir(exist_ok=True)
        
        # Format du nom de fichier
        timestamp = datetime.now().strftime('%Y-%m-%d_%H_%M_%S')
        self.log_file = self.log_dir / f'training_depth_{depth}_date_{timestamp}.log'
        
        # Formatter pour les logs
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        
        # Handler pour le fichier
        file_handler = logging.FileHandler(self.log_file)
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)
        
        # Handler pour le terminal
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)
    
    def info(self, message):
        """Log un message de niveau INFO."""
        self.logger.info(message) 