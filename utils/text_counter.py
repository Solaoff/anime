# utils/text_counter.py - подсчет токенов текста для персонажей
import re
from collections import defaultdict

class TextCounter:
    """Класс для подсчета количества токенов текста персонажей"""
    
    def __init__(self):
        self.character_texts = defaultdict(list)
        self.character_stats = defaultdict(dict)
    
    def analyze_subtitles(self, subtitle_data, characters_map):
        """Анализ субтитров и подсчет текста по персонажам"""
        self.character_texts.clear()
        self.character_stats.clear()
        
        for subtitle in subtitle_data:
            text = subtitle.get('text', '')
            
            # Определяем персонажа по тексту
            character = self.identify_character(text, characters_map)
            if character:
                clean_text = self.clean_text(text)
                self.character_texts[character].append(clean_text)
        
        # Вычисляем статистику
        for character, texts in self.character_texts.items():
            self.character_stats[character] = self.calculate_stats(texts)
        
        return self.character_stats
    
    def identify_character(self, text, characters_map):
        """Определение персонажа по тексту субтитров"""
        # Проверяем есть ли имя персонажа в начале строки
        for character_name in characters_map:
            # Ищем имя в начале строки (с двоеточием или без)
            patterns = [
                f"^{character_name}:",
                f"^{character_name} -",
                f"^{character_name.upper()}:",
                f"^{character_name.lower()}:"
            ]
            
            for pattern in patterns:
                if re.search(pattern, text, re.IGNORECASE):
                    return character_name
        
        # Если не найден точный персонаж, возвращаем "Unknown"
        return "Unknown"
    
    def clean_text(self, text):
        """Очистка текста от служебных символов"""
        # Убираем имя персонажа в начале
        text = re.sub(r'^[^:]+:\s*', '', text)
        text = re.sub(r'^[^-]+-\s*', '', text)
        
        # Убираем HTML теги
        text = re.sub(r'<[^>]+>', '', text)
        
        # Убираем лишние пробелы
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text
    
    def calculate_stats(self, texts):
        """Вычисление статистики для текстов персонажа"""
        if not texts:
            return {
                'total_lines': 0,
                'total_chars': 0,
                'total_words': 0,
                'avg_line_length': 0,
                'elevenlabs_tokens': 0
            }
        
        total_chars = sum(len(text) for text in texts)
        total_words = sum(len(text.split()) for text in texts)
        total_lines = len(texts)
        
        # Для ElevenLabs считаем только буквенно-цифровые символы и пробелы
        elevenlabs_chars = 0
        for text in texts:
            elevenlabs_chars += len(''.join(c for c in text if c.isalnum() or c.isspace()))
        
        return {
            'total_lines': total_lines,
            'total_chars': total_chars,
            'total_words': total_words,
            'avg_line_length': total_chars / total_lines if total_lines > 0 else 0,
            'elevenlabs_tokens': elevenlabs_chars
        }
    
    def get_character_tokens(self, character_name):
        """Получить количество токенов для конкретного персонажа"""
        stats = self.character_stats.get(character_name, {})
        return stats.get('elevenlabs_tokens', 0)
    
    def get_all_character_stats(self):
        """Получить статистику по всем персонажам"""
        return dict(self.character_stats)
    
    def get_total_tokens(self):
        """Получить общее количество токенов"""
        return sum(stats.get('elevenlabs_tokens', 0) 
                  for stats in self.character_stats.values())
    
    def estimate_cost_by_engine(self, character_name, tts_engine):
        """Оценка стоимости озвучки персонажа по TTS движку"""
        stats = self.character_stats.get(character_name, {})
        
        if tts_engine == 'elevenlabs':
            return stats.get('elevenlabs_tokens', 0)
        elif tts_engine in ['google_tts', 'edge_tts']:
            # Бесплатные движки
            return 0
        elif tts_engine == 'gtts':
            # Бесплатный
            return 0
        else:
            # Неизвестный движок
            return stats.get('total_chars', 0)
    
    def print_summary(self):
        """Вывод сводки по всем персонажам"""
        print("\n=== СТАТИСТИКА ТЕКСТА ПЕРСОНАЖЕЙ ===")
        
        total_tokens = 0
        for character, stats in self.character_stats.items():
            tokens = stats.get('elevenlabs_tokens', 0)
            lines = stats.get('total_lines', 0)
            words = stats.get('total_words', 0)
            
            print(f"{character:20} | {lines:3} строк | {words:4} слов | {tokens:4} токенов")
            total_tokens += tokens
        
        print(f"{'':20} | {'':8} | {'':9} | {total_tokens:4} ВСЕГО")
        print("=" * 55)