# profiles/character_profile.py - управление профилями персонажей, сохранение/загрузка настроек голосов
import json
import os
from pathlib import Path
from datetime import datetime

class CharacterProfile:
    def __init__(self, anime_name):
        self.anime_name = anime_name
        # Правильное определение пути
        import os
        current_dir = os.getcwd()
        
        # Проверяем, находимся ли мы уже в папке src
        if current_dir.endswith('src'):
            # Если уже в src, то просто data/profiles
            self.profile_path = Path(current_dir) / "data" / "profiles" / f"{anime_name}.json"
        else:
            # Если не в src, то добавляем src/data/profiles
            self.profile_path = Path(current_dir) / "src" / "data" / "profiles" / f"{anime_name}.json"
        
        print(f"CharacterProfile создан для '{anime_name}'")
        print(f"Текущая директория: {current_dir}")
        print(f"Путь к профилю: {self.profile_path}")
        
        self.characters = {}
        self.metadata = {
            "anime_name": anime_name,
            "created_date": datetime.now().isoformat(),
            "last_modified": datetime.now().isoformat(),
            "version": "1.0"
        }
        
    def add_character(self, name, tts_engine, voice, gender="unknown", api_key="", voice_id="", estimated_tokens=0):
        """Добавить персонажа в профиль"""
        self.characters[name] = {
            "name": name,
            "tts_engine": tts_engine,
            "voice": voice,
            "gender": gender,
            "api_key": api_key,  # API ключ для TTS сервисов
            "voice_id": voice_id,  # ID голоса для ElevenLabs
            "estimated_tokens": estimated_tokens  # Рассчитанные токены
        }
        self.metadata["last_modified"] = datetime.now().isoformat()
        print(f"Персонаж добавлен в профиль: {name} -> {tts_engine} - {voice} (ID: {voice_id}, Токенов: {estimated_tokens})")
    
    def update_character(self, name, **kwargs):
        """Обновить настройки персонажа"""
        if name in self.characters:
            self.characters[name].update(kwargs)
            self.metadata["last_modified"] = datetime.now().isoformat()
    
    def remove_character(self, name):
        """Удалить персонажа"""
        if name in self.characters:
            del self.characters[name]
            self.metadata["last_modified"] = datetime.now().isoformat()
    
    def get_character(self, name):
        """Получить настройки персонажа"""
        return self.characters.get(name, None)
    
    def get_all_characters(self):
        """Получить всех персонажей"""
        return self.characters
    
    def save_profile(self):
        """Сохранить профиль в файл"""
        print(f"Начинаем сохранение профиля: {self.anime_name}")
        print(f"Путь для сохранения: {self.profile_path}")
        
        # Создаем папку если её нет
        os.makedirs(self.profile_path.parent, exist_ok=True)
        print(f"Папка создана: {self.profile_path.parent}")
        
        profile_data = {
            "metadata": self.metadata,
            "characters": self.characters
        }
        
        print(f"Данные для сохранения: {len(self.characters)} персонажей")
        
        try:
            with open(self.profile_path, 'w', encoding='utf-8') as f:
                json.dump(profile_data, f, indent=2, ensure_ascii=False)
            
            print(f"✓ Профиль успешно сохранен: {self.profile_path}")
            
            # Проверяем что файл действительно создался
            if self.profile_path.exists():
                size = self.profile_path.stat().st_size
                print(f"✓ Файл существует, размер: {size} байт")
            else:
                print("✗ ОШИБКА: Файл не создался!")
                
        except Exception as e:
            print(f"✗ ОШИБКА сохранения: {e}")
            raise e
    
    def load_profile(self):
        """Загрузить профиль из файла"""
        print(f"Попытка загрузить профиль из: {self.profile_path}")
        
        if self.profile_path.exists():
            print(f"Файл профиля найден, загружаем...")
            try:
                with open(self.profile_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.metadata = data.get("metadata", self.metadata)
                    self.characters = data.get("characters", {})
                    print(f"✓ Профиль загружен. Персонажей: {len(self.characters)}")
                    for name, char in self.characters.items():
                        print(f"  - {name}: {char.get('tts_engine')} - {char.get('voice')}")
                    return True
            except Exception as e:
                print(f"✗ Ошибка чтения файла: {e}")
                return False
        else:
            print(f"✗ Файл профиля не найден: {self.profile_path}")
        return False
    
    def get_characters_by_engine(self, engine):
        """Получить персонажей по TTS движку"""
        return {name: char for name, char in self.characters.items() 
                if char["tts_engine"] == engine}
    
    def get_character_stats(self):
        """Статистика профиля"""
        engines = {}
        for char in self.characters.values():
            engine = char["tts_engine"]
            engines[engine] = engines.get(engine, 0) + 1
        
        return {
            "total_characters": len(self.characters),
            "engines_used": engines,
            "created": self.metadata["created_date"],
            "modified": self.metadata["last_modified"]
        }

class ProfileManager:
    def __init__(self):
        # Правильное определение пути
        import os
        current_dir = os.getcwd()
        
        # Проверяем, находимся ли мы уже в папке src
        if current_dir.endswith('src'):
            # Если уже в src, то просто data/profiles
            self.profiles_dir = Path(current_dir) / "data" / "profiles"
        else:
            # Если не в src, то добавляем src/data/profiles
            self.profiles_dir = Path(current_dir) / "src" / "data" / "profiles"
        
        print(f"ProfileManager инициализирован")
        print(f"Текущая директория: {current_dir}")
        print(f"Папка профилей: {self.profiles_dir}")
        
        # Создаем папку если её нет
        os.makedirs(self.profiles_dir, exist_ok=True)
        print(f"Папка создана/проверена: {self.profiles_dir.exists()}")
        
    def get_available_profiles(self):
        """Получить список доступных профилей"""
        print(f"Поиск профилей в: {self.profiles_dir}")
        
        if not self.profiles_dir.exists():
            print("Папка профилей не существует")
            return []
        
        profiles = []
        for profile_file in self.profiles_dir.glob("*.json"):
            profiles.append(profile_file.stem)
            print(f"Найден профиль: {profile_file.stem}")
        
        print(f"Всего найдено профилей: {len(profiles)}")
        return profiles
    
    def load_profile(self, anime_name):
        """Загрузить профиль"""
        print(f"ProfileManager: загружаем профиль для '{anime_name}'")
        
        profile = CharacterProfile(anime_name)
        if profile.load_profile():
            print(f"ProfileManager: профиль успешно загружен")
            return profile
        else:
            print(f"ProfileManager: профиль не найден")
        return None
    
    def create_profile(self, anime_name):
        """Создать новый профиль"""
        print(f"ProfileManager: создаем новый профиль для '{anime_name}'")
        return CharacterProfile(anime_name)