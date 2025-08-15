# test_api_keys.py - тестирование новых функций API ключей и voice_id
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from profiles.character_profile import CharacterProfile

def test_voice_id_support():
    """Тест поддержки voice_id в профилях"""
    print("=== ТЕСТ ПОДДЕРЖКИ VOICE_ID ===")
    
    # Создаем тестовый профиль
    profile = CharacterProfile("Test Voice ID")
    
    # Добавляем персонажа с voice_id
    profile.add_character(
        name="Agata",
        tts_engine="elevenlabs", 
        voice="agata",
        gender="female",
        api_key="sk-test123456789",
        voice_id="RWZoDXNWfWzwHbPcWFpP"
    )
    
    # Добавляем персонажа без voice_id (для Edge TTS)
    profile.add_character(
        name="Marek",
        tts_engine="edge_tts",
        voice="pl-PL-MarekNeural",
        gender="male"
    )
    
    # Проверяем что данные сохранились правильно
    agata = profile.get_character("Agata")
    marek = profile.get_character("Marek")
    
    print(f"Agata voice_id: {agata.get('voice_id')}")
    print(f"Agata api_key: {agata.get('api_key')}")
    print(f"Marek voice_id: {marek.get('voice_id', 'не задан')}")
    
    # Сохраняем и перезагружаем
    profile.save_profile()
    print(f"Профиль сохранен: {profile.profile_path}")
    
    # Создаем новый объект и загружаем
    profile2 = CharacterProfile("Test Voice ID")
    if profile2.load_profile():
        agata2 = profile2.get_character("Agata")
        print(f"После загрузки - Agata voice_id: {agata2.get('voice_id')}")
        print(f"После загрузки - Agata api_key: {agata2.get('api_key')}")
        print("✓ Тест прошел успешно!")
    else:
        print("✗ Ошибка загрузки профиля")

if __name__ == "__main__":
    test_voice_id_support()
