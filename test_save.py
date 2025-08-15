# test_save.py - тест сохранения профилей
import sys
import os
from pathlib import Path

# Проверим текущую директорию
print(f"Текущая директория: {os.getcwd()}")

# Добавляем src в путь
sys.path.append(str(Path(__file__).parent))

from profiles.character_profile import ProfileManager, CharacterProfile

def test_save():
    print("=== ТЕСТ СОХРАНЕНИЯ ПРОФИЛЕЙ ===")
    
    # Тестируем создание профиля
    profile = CharacterProfile("Тестовое Аниме")
    print(f"Профиль создан: {profile.anime_name}")
    print(f"Путь к файлу: {profile.profile_path}")
    
    # Добавляем персонажей
    profile.add_character("Тестовый Персонаж 1", "edge_tts", "pl-PL-MarekNeural", "male")
    profile.add_character("Тестовый Персонаж 2", "edge_tts", "pl-PL-ZofiaNeural", "female")
    
    print(f"Добавлено персонажей: {len(profile.get_all_characters())}")
    
    # Сохраняем
    try:
        profile.save_profile()
        print("✓ Сохранение прошло успешно")
        
        # Проверяем файл
        if profile.profile_path.exists():
            size = profile.profile_path.stat().st_size
            print(f"✓ Файл создан, размер: {size} байт")
            
            # Читаем содержимое
            with open(profile.profile_path, 'r', encoding='utf-8') as f:
                content = f.read()
                print(f"Содержимое файла (первые 200 символов):")
                print(content[:200])
        else:
            print("✗ Файл не создался!")
            
    except Exception as e:
        print(f"✗ Ошибка сохранения: {e}")
        import traceback
        traceback.print_exc()
    
    # Тестируем загрузку
    print("\n--- Тестируем загрузку ---")
    manager = ProfileManager()
    loaded_profile = manager.load_profile("Тестовое Аниме")
    
    if loaded_profile:
        print("✓ Профиль загружен")
        characters = loaded_profile.get_all_characters()
        print(f"Персонажей в загруженном профиле: {len(characters)}")
        for name, data in characters.items():
            print(f"  - {name}: {data['tts_engine']} - {data['voice']}")
    else:
        print("✗ Не удалось загрузить профиль")

if __name__ == "__main__":
    test_save()