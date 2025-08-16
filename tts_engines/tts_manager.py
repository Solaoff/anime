# tts_engines/tts_manager.py - менеджер всех TTS движков
from .elevenlabs.elevenlabs_engine import ElevenLabsEngine

class TTSManager:
    """Менеджер всех TTS движков"""
    
    def __init__(self, settings):
        self.settings = settings
        self.engines = {}
        
        # Инициализируем движки
        self._init_engines()
    
    def _init_engines(self):
        """Инициализация всех движков"""
        try:
            # ElevenLabs движок
            self.engines['ElevenLabs'] = ElevenLabsEngine(self.settings)
            
            # TODO: Добавить другие движки
            # self.engines['Edge-TTS'] = EdgeTTSEngine(self.settings)
            # self.engines['Google'] = GoogleTTSEngine(self.settings)
            
        except Exception as e:
            print(f"Ошибка инициализации TTS движков: {e}")
    
    def get_engine(self, engine_name):
        """Получить движок по имени"""
        return self.engines.get(engine_name)
    
    def get_available_engines(self):
        """Получить список доступных движков"""
        available = []
        for name, engine in self.engines.items():
            if engine.check_availability():
                available.append(name)
        return available
    
    def test_voice(self, engine_name, character_data, test_text="Hello, this is a test voice."):
        """Тест голоса через указанный движок"""
        engine = self.get_engine(engine_name)
        if not engine:
            return {
                'success': False,
                'error': f'Движок {engine_name} не найден'
            }
        
        return engine.test_voice(character_data, test_text)
    
    def synthesize_speech(self, engine_name, text, character_data, output_path):
        """Синтез речи через указанный движок"""
        engine = self.get_engine(engine_name)
        if not engine:
            raise Exception(f'Движок {engine_name} не найден')
        
        return engine.synthesize(text, character_data, output_path)
    
    def get_voices_for_engine(self, engine_name, api_key=None):
        """Получить голоса для движка"""
        engine = self.get_engine(engine_name)
        if not engine:
            return []
        
        if engine_name == 'ElevenLabs':
            return engine.get_voices(api_key)
        else:
            return engine.get_voices()
    
    def get_credits_info(self, engine_name, api_key):
        """Получить информацию о кредитах для движка"""
        engine = self.get_engine(engine_name)
        if not engine:
            return {'error': 'Движок не найден'}
        
        if hasattr(engine, 'get_credits_info'):
            return engine.get_credits_info(api_key)
        else:
            return {'error': 'Движок не поддерживает проверку кредитов'}
