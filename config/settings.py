# config/settings.py - управление настройками приложения, API ключи, пути, конфигурация TTS
import json
import os
from pathlib import Path

class Settings:
    def __init__(self):
        # Правильное определение пути
        import os
        current_dir = os.getcwd()
        
        # Проверяем, находимся ли мы уже в папке src
        if current_dir.endswith('src'):
            # Если уже в src, то просто data/config.json
            self.config_file = Path(current_dir) / "data" / "config.json"
        else:
            # Если не в src, то добавляем src/data/config.json
            self.config_file = Path(current_dir) / "src" / "data" / "config.json"
            
        self.default_config = {
            "api_keys": {
                "google_credentials_path": "google_credentials.json",
                "elevenlabs_keys": []
            },
            "tts_limits": {
                "google_tts": {"daily_limit": 1000000, "used_today": 0},
                "edge_tts": {"daily_limit": -1, "used_today": 0},
                "gtts": {"daily_limit": 100, "used_today": 0},
                "coqui_tts": {"daily_limit": -1, "used_today": 0},
                "elevenlabs": {"daily_limit": 10000, "used_today": 0}
            },
            "ffmpeg": {
                "use_nvenc": True,
                "fallback_x264": True
            },
            "audio": {
                "temp_format": "wav",
                "output_format": "mp3",
                "original_volume_reduction": -6
            }
        }
        self.config = self.load_config()
    
    def load_config(self):
        if self.config_file.exists():
            with open(self.config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return self.default_config.copy()
    
    def save_config(self):
        os.makedirs(self.config_file.parent, exist_ok=True)
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(self.config, f, indent=2, ensure_ascii=False)
    
    def get(self, key, default=None):
        keys = key.split('.')
        value = self.config
        for k in keys:
            value = value.get(k, {})
        return value if value != {} else default
    
    def set(self, key, value):
        keys = key.split('.')
        config = self.config
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        config[keys[-1]] = value
        self.save_config()
    
    def update_tts_usage(self, engine, amount):
        current = self.get(f"tts_limits.{engine}.used_today", 0)
        self.set(f"tts_limits.{engine}.used_today", current + amount)