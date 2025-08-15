# test_profiles.py - тест загрузки профилей
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

from profiles.character_profile import ProfileManager

def test_profiles():
    print("=== ТЕСТ ЗАГРУЗКИ ПРОФИЛЕЙ ===")
    
    manager = ProfileManager()
    print(f"Папка профилей: {manager.profiles_dir}")
    
    # Список доступных профилей
    available = manager.get_available_profiles()
    print(f"Доступные профили: {available}")
    
    # Пытаемся загрузить тестовый профиль
    if "Test Anime" in available:
        print("\n--- Загружаем Test Anime ---")
        profile = manager.load_profile("Test Anime")
        if profile:
            print("Профиль загружен успешно!")
            characters = profile.get_all_characters()
            print(f"Персонажей в профиле: {len(characters)}")
            for name, data in characters.items():
                print(f"  {name}: {data['tts_engine']} - {data['voice']} ({data['gender']})")
        else:
            print("Ошибка загрузки профиля")
    else:
        print("Тестовый профиль не найден")

if __name__ == "__main__":
    test_profiles()