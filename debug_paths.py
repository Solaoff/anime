# debug_paths.py - отладка путей к профилям (ИСПРАВЛЕННАЯ ВЕРСИЯ)
import os
from pathlib import Path

def debug_paths():
    print("=== ОТЛАДКА ПУТЕЙ (ИСПРАВЛЕННАЯ) ===")
    
    # Текущая директория
    current_dir = os.getcwd()
    print(f"Текущая директория: {current_dir}")
    print(f"Заканчивается на 'src': {current_dir.endswith('src')}")
    
    # Правильный путь к папке профилей
    if current_dir.endswith('src'):
        profiles_dir = Path(current_dir) / "data" / "profiles"
    else:
        profiles_dir = Path(current_dir) / "src" / "data" / "profiles"
        
    print(f"Правильный путь к папке профилей: {profiles_dir}")
    print(f"Папка профилей существует: {profiles_dir.exists()}")
    
    # Создаем папку если её нет
    if not profiles_dir.exists():
        print("Создаем папку профилей...")
        os.makedirs(profiles_dir, exist_ok=True)
        print(f"Папка создана: {profiles_dir.exists()}")
    
    # Проверяем права доступа
    try:
        test_file = profiles_dir / "test.txt"
        test_file.write_text("test")
        test_file.unlink()
        print("✓ Права записи есть")
    except Exception as e:
        print(f"✗ Проблема с правами записи: {e}")
    
    # Создаем тестовый профиль
    test_profile_path = profiles_dir / "Test Anime.json"
    test_data = {
        "metadata": {
            "anime_name": "Test Anime",
            "created_date": "2025-01-15T10:00:00",
            "version": "1.0"
        },
        "characters": {
            "Tiwa": {
                "name": "Tiwa",
                "tts_engine": "edge_tts",
                "voice": "pl-PL-ZofiaNeural",
                "gender": "female"
            },
            "Rudo": {
                "name": "Rudo", 
                "tts_engine": "edge_tts",
                "voice": "pl-PL-MarekNeural",
                "gender": "male"
            }
        }
    }
    
    try:
        import json
        with open(test_profile_path, 'w', encoding='utf-8') as f:
            json.dump(test_data, f, indent=2, ensure_ascii=False)
        print(f"✓ Тестовый профиль создан: {test_profile_path}")
    except Exception as e:
        print(f"✗ Ошибка создания тестового профиля: {e}")
    
    # Список файлов в папке
    if profiles_dir.exists():
        files = list(profiles_dir.glob("*.json"))
        print(f"JSON файлы в папке: {[f.name for f in files]}")

if __name__ == "__main__":
    debug_paths()