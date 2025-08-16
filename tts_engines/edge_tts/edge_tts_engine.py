# tts_engines/edge_tts/edge_tts_engine.py - TTS движок для Microsoft Edge-TTS
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent))

from tts_engines.base.base_tts import BaseTTS
import asyncio
import os

class EdgeTTSEngine(BaseTTS):
    """TTS движок для Microsoft Edge-TTS"""
    
    def __init__(self):
        super().__init__("edge_tts")
        self.available_voices = [
            "pl-PL-MarekNeural",    # Мужской польский
            "pl-PL-ZofiaNeural",   # Женский польский
            "en-US-AriaNeural",    # Женский английский
            "en-US-GuyNeural",     # Мужской английский
        ]
    
    def synthesize(self, text: str, voice: str, output_path: str, **kwargs) -> bool:
        """Синтез речи через Edge-TTS"""
        try:
            # Импортируем edge-tts
            import edge_tts
            
            # Очищаем текст
            clean_text = self.clean_text(text)
            if not clean_text:
                print("❌ Пустой текст после очистки")
                return False
            
            # Запускаем синтез
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            try:
                loop.run_until_complete(self._synthesize_async(clean_text, voice, output_path))
                print(f"✅ Edge-TTS аудио сохранено: {output_path}")
                return True
            finally:
                loop.close()
                
        except ImportError:
            print("❌ edge-tts не установлен. Установите: pip install edge-tts")
            return False
        except Exception as e:
            print(f"❌ Ошибка Edge-TTS синтеза: {e}")
            return False
    
    async def _synthesize_async(self, text: str, voice: str, output_path: str):
        """Асинхронный синтез речи"""
        import edge_tts
        
        communicate = edge_tts.Communicate(text, voice)
        await communicate.save(output_path)
    
    def get_available_voices(self, **kwargs) -> list:
        """Получить список доступных голосов Edge-TTS"""
        try:
            import edge_tts
            
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            try:
                voices = loop.run_until_complete(edge_tts.list_voices())
                # Фильтруем польские и английские голоса
                filtered_voices = []
                for voice in voices:
                    locale = voice.get('Locale', '')
                    if locale.startswith('pl-') or locale.startswith('en-'):
                        filtered_voices.append({
                            'name': voice.get('ShortName', ''),
                            'display_name': voice.get('FriendlyName', ''),
                            'gender': voice.get('Gender', ''),
                            'locale': locale
                        })
                return filtered_voices
            finally:
                loop.close()
                
        except ImportError:
            print("❌ edge-tts не установлен")
            return [{'name': voice, 'display_name': voice} for voice in self.available_voices]
        except Exception as e:
            print(f"❌ Ошибка получения голосов Edge-TTS: {e}")
            return [{'name': voice, 'display_name': voice} for voice in self.available_voices]
    
    def test_voice(self, text: str, voice: str, **kwargs) -> str:
        """Тестирование голоса Edge-TTS"""
        # Создаем временный файл
        temp_file = self.get_temp_filename("edge_test")
        
        # Синтезируем речь
        if self.synthesize(text, voice, temp_file, **kwargs):
            return temp_file
        else:
            return ""
    
    def clean_text(self, text: str) -> str:
        """Специальная очистка текста для Edge-TTS"""
        # Базовая очистка
        clean_text = super().clean_text(text)
        
        # Убираем SSML теги если есть
        import re
        clean_text = re.sub(r'<[^>]*>', '', clean_text)
        
        # Ограничиваем длину (Edge-TTS имеет лимиты)
        if len(clean_text) > 500:
            clean_text = clean_text[:497] + "..."
            
        return clean_text
