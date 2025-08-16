# processors/subtitle_analyzer.py - анализ субтитров, извлечение персонажей, статистика реплик
import re
from collections import defaultdict
from datetime import datetime, timedelta

class SubtitleAnalyzer:
    def __init__(self):
        self.polish_male_endings = ['ski', 'cki', 'dzki', 'owski', 'ewski', 'yk', 'ek', 'osz']
        self.polish_female_endings = ['ska', 'cka', 'dzka', 'owska', 'ewska', 'a']
        
    def parse_srt(self, srt_content):
        """Парсинг .srt файла с правильным форматом"""
        # Разбиваем на блоки по пустым строкам
        blocks = re.split(r'\n\s*\n', srt_content.strip())
        
        subtitles = []
        for block in blocks:
            lines = [line.strip() for line in block.split('\n') if line.strip()]
            
            if len(lines) >= 4:  # Минимум 4 строки: номер, имя, время, текст
                try:
                    # Строка 1: номер
                    subtitle_id = int(lines[0])
                    
                    # Строка 2: имя персонажа
                    character = lines[1]
                    
                    # Строка 3: временной код
                    time_line = lines[2]
                    if '-->' in time_line:
                        time_parts = time_line.split(' --> ')
                        start_time = self._parse_time(time_parts[0])
                        end_time = self._parse_time(time_parts[1])
                    else:
                        continue  # Пропускаем некорректные блоки
                    
                    # Строка 4+: текст реплики (может быть многострочной)
                    text_lines = lines[3:]
                    text = '\n'.join(text_lines)
                    
                    subtitles.append({
                        'id': subtitle_id,
                        'character': character,
                        'start_time': start_time,
                        'end_time': end_time,
                        'text': text,  # Тут теперь хранится только текст реплики
                        'duration': end_time - start_time
                    })
                    
                except (ValueError, IndexError):
                    continue  # Пропускаем некорректные блоки
        
        return subtitles
    
    def analyze_characters(self, subtitles):
        """Анализ персонажей из субтитров"""
        characters = defaultdict(lambda: {
            'name': '',
            'total_lines': 0,
            'total_duration': 0,
            'gender': 'unknown',
            'lines': []
        })
        
        for sub in subtitles:
            char_name = sub['character']
            characters[char_name]['name'] = char_name
            characters[char_name]['total_lines'] += 1
            characters[char_name]['total_duration'] += sub['duration']
            characters[char_name]['gender'] = self._detect_gender(char_name)
            characters[char_name]['lines'].append({
                'text': sub['text'],
                'duration': sub['duration'],
                'start_time': sub['start_time']
            })
        
        return dict(characters)
    
    def _detect_gender(self, name):
        """Определение пола по польскому имени"""
        name_lower = name.lower()
        
        # Проверка мужских окончаний
        for ending in self.polish_male_endings:
            if name_lower.endswith(ending):
                return 'male'
        
        # Проверка женских окончаний
        for ending in self.polish_female_endings:
            if name_lower.endswith(ending):
                return 'female'
        
        return 'unknown'
    
    def _parse_time(self, time_str):
        """Конвертация времени в секунды"""
        time_parts = time_str.replace(',', '.').split(':')
        hours = int(time_parts[0])
        minutes = int(time_parts[1])
        seconds = float(time_parts[2])
        return hours * 3600 + minutes * 60 + seconds
    
    def get_character_stats(self, characters):
        """Статистика по персонажам"""
        stats = []
        for char_data in characters.values():
            stats.append({
                'name': char_data['name'],
                'lines': char_data['total_lines'],
                'duration': round(char_data['total_duration'], 2),
                'gender': char_data['gender']
            })
        return sorted(stats, key=lambda x: x['lines'], reverse=True)