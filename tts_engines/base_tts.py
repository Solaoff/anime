# tts_engines/base_tts.py - базовый класс для всех TTS движков, общий интерфейс
from abc import ABC, abstractmethod
from pathlib import Path

class BaseTTS(ABC):
    def __init__(self, name, settings):
        self.name = name
        self.settings = settings
        self.available_voices = []
        self.is_available = False
        
    @abstractmethod
    def get_voices(self):
        """Получить список доступных голосов"""
        pass
    
    @abstractmethod
    def synthesize(self, text, voice, output_path):
        """Синтез речи"""
        pass
    
    @abstractmethod
    def test_voice(self, voice, test_text="Test voice"):
        """Тест голоса"""
        pass
    
    def check_availability(self):
        """Проверка доступности движка"""
        try:
            self.get_voices()
            self.is_available = True
            return True
        except:
            self.is_available = False
            return False
    
    def get_daily_usage(self):
        """Получить использование за день"""
        return self.settings.get(f"tts_limits.{self.name}.used_today", 0)
    
    def get_daily_limit(self):
        """Получить дневной лимит"""
        return self.settings.get(f"tts_limits.{self.name}.daily_limit", -1)
    
    def can_synthesize(self, text_length):
        """Проверка возможности синтеза"""
        if not self.is_available:
            return False
            
        daily_limit = self.get_daily_limit()
        if daily_limit == -1:  # Безлимитный
            return True
            
        daily_usage = self.get_daily_usage()
        return (daily_usage + text_length) <= daily_limit
    
    def update_usage(self, text_length):
        """Обновление статистики использования"""
        self.settings.update_tts_usage(self.name, text_length)
    
    def clean_text(self, text):
        """Очистка текста от проблемных символов"""
        # Удаляем инструкции, коды, паузы для Edge-TTS
        cleaned = text.replace('<break', '').replace('SSML', '')
        cleaned = cleaned.replace('time=', '').replace('strength=', '')
        return cleaned.strip()