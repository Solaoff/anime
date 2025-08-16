# tts_engines/base/base_tts.py - базовый класс для всех TTS движков
from abc import ABC, abstractmethod
from pathlib import Path

class BaseTTS(ABC):
    """Базовый класс для всех TTS движков"""
    
    def __init__(self, engine_name: str):
        self.engine_name = engine_name
        self.output_dir = Path("temp_audio")
        self.output_dir.mkdir(exist_ok=True)
    
    @abstractmethod
    def synthesize(self, text: str, voice: str, output_path: str, **kwargs) -> bool:
        """
        Синтез речи из текста
        
        Args:
            text: Текст для озвучки
            voice: Голос для использования
            output_path: Путь к выходному файлу
            **kwargs: Дополнительные параметры (api_key, voice_id и т.д.)
            
        Returns:
            bool: True если успешно, False если ошибка
        """
        pass
    
    @abstractmethod
    def get_available_voices(self, **kwargs) -> list:
        """
        Получить список доступных голосов
        
        Args:
            **kwargs: Дополнительные параметры (api_key и т.д.)
            
        Returns:
            list: Список доступных голосов
        """
        pass
    
    @abstractmethod
    def test_voice(self, text: str, voice: str, **kwargs) -> str:
        """
        Тестирование голоса с текстом
        
        Args:
            text: Текст для тестирования
            voice: Голос для тестирования
            **kwargs: Дополнительные параметры
            
        Returns:
            str: Путь к созданному аудио файлу или пустая строка при ошибке
        """
        pass
    
    def clean_text(self, text: str) -> str:
        """Очистка текста от нежелательных символов"""
        import re
        # Убираем HTML теги
        text = re.sub(r'<[^>]+>', '', text)
        # Убираем лишние пробелы
        text = re.sub(r'\s+', ' ', text).strip()
        return text
    
    def get_temp_filename(self, prefix: str = "test") -> str:
        """Получить временное имя файла"""
        import uuid
        filename = f"{prefix}_{uuid.uuid4().hex[:8]}.wav"
        return str(self.output_dir / filename)
