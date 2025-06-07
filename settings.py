import json
import os

class Settings:
    def __init__(self):
        self.settings_file = "game_settings.json"
        self.default_settings = {
            "music_volume": 70,
            "sfx_volume": 70,
            "player_colors": [(255, 0, 0), (255, 255, 0)],  # Red and Yellow
            "ai_difficulty": "MEDIUM",
            "ai_thinking_time": 1.0  # seconds
        }
        self.current_settings = self.load_settings()

    def load_settings(self):
        if os.path.exists(self.settings_file):
            try:
                with open(self.settings_file, 'r') as f:
                    settings = json.load(f)
                    # Convert color tuples from lists back to tuples
                    settings['player_colors'] = [tuple(color) for color in settings['player_colors']]
                    return settings
            except:
                return self.default_settings.copy()
        return self.default_settings.copy()

    def save_settings(self):
        with open(self.settings_file, 'w') as f:
            json.dump(self.current_settings, f, indent=4)

    def update_setting(self, key, value):
        if key in self.current_settings:
            self.current_settings[key] = value
            self.save_settings()

    def get_setting(self, key):
        return self.current_settings.get(key)

    def reset_to_default(self):
        self.current_settings = self.default_settings.copy()
        self.save_settings()

    def get_music_volume(self):
        return self.current_settings['music_volume'] / 100.0

    def get_sfx_volume(self):
        return self.current_settings['sfx_volume'] / 100.0

    def get_player_colors(self):
        return self.current_settings['player_colors']

    def get_ai_difficulty(self):
        return self.current_settings['ai_difficulty']

    def get_ai_thinking_time(self):
        return self.current_settings['ai_thinking_time']