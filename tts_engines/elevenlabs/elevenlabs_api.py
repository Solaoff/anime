# tts_engines/elevenlabs/elevenlabs_api.py - работа с ElevenLabs API
import requests
import json

class ElevenLabsAPI:
    """Класс для работы с ElevenLabs API"""
    
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "https://api.elevenlabs.io/v1"
        self.headers = {
            "Accept": "application/json",
            "xi-api-key": self.api_key
        }
    
    def get_credits_info(self):
        """Получить информацию о кредитах"""
        try:
            url = f"{self.base_url}/user/subscription"
            response = requests.get(url, headers=self.headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                # Извлекаем информацию о кредитах
                character_count = data.get('character_count', 0)
                character_limit = data.get('character_limit', 0)
                
                credits_available = character_limit - character_count
                
                return {
                    'credits_available': credits_available,
                    'credits_used': character_count,
                    'credits_total': character_limit,
                    'status': 'active'
                }
            elif response.status_code == 401:
                return {'error': 'Неверный API ключ'}
            else:
                return {'error': f'HTTP {response.status_code}'}
                
        except requests.exceptions.Timeout:
            return {'error': 'Таймаут соединения'}
        except requests.exceptions.ConnectionError:
            return {'error': 'Ошибка соединения'}
        except Exception as e:
            return {'error': f'Ошибка: {str(e)[:30]}'}
    
    def validate_api_key(self):
        """Проверка валидности API ключа"""
        credits_info = self.get_credits_info()
        return 'error' not in credits_info
    
    def estimate_text_cost(self, text):
        """Оценка стоимости озвучки текста"""
        # ElevenLabs считает символы
        char_count = len(text)
        
        # Приблизительная оценка (может отличаться от реальной)
        # Обычно учитываются только текстовые символы
        text_chars = len(''.join(c for c in text if c.isalnum() or c.isspace()))
        
        return {
            'character_count': text_chars,
            'estimated_cost': text_chars,  # 1 символ = 1 кредит
            'original_length': char_count
        }
    
    def get_available_voices(self):
        """Получить список доступных голосов"""
        try:
            url = f"{self.base_url}/voices"
            response = requests.get(url, headers=self.headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                voices = []
                
                for voice in data.get('voices', []):
                    voices.append({
                        'voice_id': voice.get('voice_id'),
                        'name': voice.get('name'),
                        'category': voice.get('category', 'generated'),
                        'labels': voice.get('labels', {}),
                        'preview_url': voice.get('preview_url')
                    })
                
                return voices
            else:
                return []
                
        except Exception as e:
            print(f"Ошибка получения голосов: {e}")
            return []
    
    def test_voice(self, voice_id, text="Hello, this is a test."):
        """Тестовая генерация голоса"""
        try:
            url = f"{self.base_url}/text-to-speech/{voice_id}"
            
            data = {
                "text": text,
                "model_id": "eleven_monolingual_v1",
                "voice_settings": {
                    "stability": 0.5,
                    "similarity_boost": 0.5
                }
            }
            
            response = requests.post(
                url, 
                json=data, 
                headers=self.headers,
                timeout=30
            )
            
            if response.status_code == 200:
                return {
                    'success': True,
                    'audio_data': response.content,
                    'content_type': response.headers.get('content-type', 'audio/mpeg')
                }
            else:
                return {
                    'success': False,
                    'error': f'HTTP {response.status_code}'
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': f'Ошибка: {str(e)[:30]}'
            }