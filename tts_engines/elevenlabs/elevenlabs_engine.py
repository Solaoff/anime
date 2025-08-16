# tts_engines/elevenlabs/elevenlabs_engine.py - ElevenLabs TTS движок
import os
import tempfile
from pathlib import Path
import pygame
from ..base_tts import BaseTTS
from .elevenlabs_api import ElevenLabsAPI

class ElevenLabsEngine(BaseTTS):
    """ElevenLabs TTS движок"""
    
    def __init__(self, settings):
        super().__init__("ElevenLabs", settings)
        
        # Инициализация pygame для воспроизведения
        try:
            pygame.mixer.init()
            self._pygame_available = True
        except:
            self._pygame_available = False
    
    def get_voices(self, api_key=None):
        """Получить список голосов (требует API ключ)"""
        if not api_key:
            return []
        
        try:
            api = ElevenLabsAPI(api_key)
            voices = api.get_available_voices()
            
            # Форматируем голоса для GUI
            formatted_voices = []
            for voice in voices:
                formatted_voices.append({
                    'id': voice['voice_id'],
                    'name': voice['name'],
                    'category': voice.get('category', 'generated'),
                    'language': 'en',  # ElevenLabs в основном английский
                    'gender': self._guess_gender(voice.get('labels', {}))
                })
            
            self.available_voices = formatted_voices
            return formatted_voices
            
        except Exception as e:
            print(f"Ошибка получения голосов ElevenLabs: {e}")
            return []
    
    def _guess_gender(self, labels):
        """Попытка определить пол по меткам"""
        if not isinstance(labels, dict):
            return 'unknown'
        
        # Ищем указания на пол в метках
        for key, value in labels.items():
            if 'gender' in key.lower():
                return value.lower()
            if 'male' in str(value).lower():
                return 'male'
            if 'female' in str(value).lower():
                return 'female'
        
        return 'unknown'
    
    def synthesize(self, text, character_data, output_path):
        """Синтез речи для персонажа"""
        api_key = character_data.get('api_key')
        voice_id = character_data.get('voice_id')
        
        if not api_key or not voice_id:
            raise ValueError("Требуются API ключ и Voice ID персонажа")
        
        try:
            api = ElevenLabsAPI(api_key)
            
            # Очищаем текст
            clean_text = self.clean_text(text)
            
            # Генерируем речь
            result = api.test_voice(voice_id, clean_text)
            
            if result['success']:
                # Сохраняем аудио
                output_path = Path(output_path)
                output_path.parent.mkdir(parents=True, exist_ok=True)
                
                with open(output_path, 'wb') as f:
                    f.write(result['audio_data'])
                
                # Обновляем статистику использования
                self.update_usage(len(clean_text))
                
                return str(output_path)
            else:
                raise Exception(f"Ошибка синтеза: {result['error']}")
                
        except Exception as e:
            raise Exception(f"ElevenLabs синтез ошибка: {str(e)}")
    
    def test_voice(self, character_data, test_text="Hello, this is a test voice."):
        """Тест голоса персонажа"""
        api_key = character_data.get('api_key')
        voice_id = character_data.get('voice_id')
        
        if not api_key or not voice_id:
            return {
                'success': False,
                'error': 'Требуются API ключ и Voice ID'
            }
        
        try:
            api = ElevenLabsAPI(api_key)
            
            # Очищаем текст
            clean_text = self.clean_text(test_text)
            
            # Генерируем тестовый звук
            result = api.test_voice(voice_id, clean_text)
            
            if result['success']:
                # Воспроизводим через pygame
                if self._pygame_available:
                    success = self._play_audio_data(result['audio_data'])
                    return {
                        'success': success,
                        'message': 'Голос воспроизведен' if success else 'Ошибка воспроизведения'
                    }
                else:
                    return {
                        'success': False,
                        'error': 'pygame недоступен для воспроизведения'
                    }
            else:
                return {
                    'success': False,
                    'error': result['error']
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': f'Ошибка теста: {str(e)}'
            }
    
    def _play_audio_data(self, audio_data):
        """Воспроизведение аудио данных через pygame"""
        try:
            # Создаем временный файл
            with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as temp_file:
                temp_file.write(audio_data)
                temp_path = temp_file.name
            
            # Воспроизводим
            pygame.mixer.music.load(temp_path)
            pygame.mixer.music.play()
            
            # Ждем завершения воспроизведения
            while pygame.mixer.music.get_busy():
                pygame.time.wait(100)
            
            # Удаляем временный файл
            os.unlink(temp_path)
            
            return True
            
        except Exception as e:
            print(f"Ошибка воспроизведения: {e}")
            return False
    
    def check_availability(self):
        """Проверка доступности движка"""
        # ElevenLabs доступен если есть интернет
        # Конкретная проверка будет при вводе API ключа
        self.is_available = True
        return True
    
    def get_credits_info(self, api_key):
        """Получить информацию о кредитах API"""
        if not api_key:
            return {'error': 'API ключ не указан'}
        
        try:
            api = ElevenLabsAPI(api_key)
            return api.get_credits_info()
        except Exception as e:
            return {'error': f'Ошибка: {str(e)}'}
    
    def estimate_cost(self, text):
        """Оценка стоимости озвучки"""
        # ElevenLabs считает символы
        return len(self.clean_text(text))
