import tkinter as tk
from tkinter import ttk, messagebox
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from profiles.character_profile import CharacterProfile
from tts_engines.tts_manager import TTSManager
import pygame

class CharacterSetupWindow:
    def __init__(self, parent, characters, profile=None):
        self.parent = parent
        self.characters = characters
        self.profile = profile
        self.tts_manager = TTSManager()
        
        # Доступные TTS движки
        self.tts_engines = ["elevenlabs", "edge_tts", "google_tts", "gtts"]
        
        # Словарь для хранения всех переменных
        self.character_vars = {}
        
        # Создаем окно
        self.window = tk.Toplevel(parent)
        self.window.title("Настройка персонажей")
        self.window.geometry("1200x600")
        self.window.transient(parent)
        self.window.grab_set()
        
        # Инициализация pygame для воспроизведения
        try:
            pygame.mixer.init()
        except Exception as e:
            print(f"Ошибка инициализации pygame: {e}")
        
        self.create_widgets()
        self.load_character_data()
    
    def create_widgets(self):
        # Основной фрейм с прокруткой
        main_frame = ttk.Frame(self.window)
        main_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        
        # Настройка растяжения
        self.window.grid_rowconfigure(0, weight=1)
        self.window.grid_columnconfigure(0, weight=1)
        main_frame.grid_rowconfigure(1, weight=1)
        main_frame.grid_columnconfigure(0, weight=1)
        
        # Заголовок
        title_label = ttk.Label(main_frame, text="Настройка голосов персонажей", 
                               font=("Arial", 14, "bold"))
        title_label.grid(row=0, column=0, pady=(0, 10), sticky="w")
        
        # Создаем Canvas и Scrollbar для прокрутки
        canvas = tk.Canvas(main_frame)
        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Размещаем canvas и scrollbar
        canvas.grid(row=1, column=0, sticky="nsew")
        scrollbar.grid(row=1, column=1, sticky="ns")
        
        # Заголовки колонок
        headers = ["Персонаж", "Пол", "TTS", "Голос", "ID Голоса", "API Ключ", "Действия", "Статус"]
        for col, header in enumerate(headers):
            header_label = ttk.Label(scrollable_frame, text=header, font=("Arial", 10, "bold"))
            header_label.grid(row=0, column=col, padx=4, pady=5, sticky="w")
        
        # Создаем элементы для каждого персонажа
        for row, (name, char_data) in enumerate(self.characters.items(), start=1):
            self.create_character_row(scrollable_frame, row, name, char_data)
        
        # Кнопки управления
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=2, column=0, columnspan=2, pady=10, sticky="ew")
        
        ttk.Button(button_frame, text="Сохранить", command=self.save_settings).grid(row=0, column=0, padx=5)
        ttk.Button(button_frame, text="Отмена", command=self.window.destroy).grid(row=0, column=1, padx=5)
        ttk.Button(button_frame, text="Применить", command=self.apply_settings).grid(row=0, column=2, padx=5)
    
    def create_character_row(self, parent_frame, row, name, char_data):
        """Создание строки настроек для персонажа"""
        
        # Имя персонажа
        name_label = ttk.Label(parent_frame, text=name, font=("Arial", 9, "bold"))
        name_label.grid(row=row, column=0, padx=4, pady=4, sticky=tk.W)
        
        # Пол
        gender_var = tk.StringVar(value=char_data.get('gender', 'unknown'))
        gender_combo = ttk.Combobox(parent_frame, textvariable=gender_var, 
                                  values=["male", "female", "unknown"], width=8)
        gender_combo.grid(row=row, column=1, padx=4, pady=4)
        
        # Включаем копирование/вставку
        self.enable_copy_paste(gender_combo)
        
        # TTS Движок
        engine_var = tk.StringVar()
        engine_combo = ttk.Combobox(parent_frame, textvariable=engine_var, 
                                  values=self.tts_engines, width=12)
        engine_combo.grid(row=row, column=2, padx=4, pady=4)
        engine_combo.bind("<<ComboboxSelected>>", 
                        lambda e, n=name: self.on_engine_change(n))
        
        # Включаем копирование/вставку
        self.enable_copy_paste(engine_combo)
        
        # Голос (стандартный выбор)
        voice_var = tk.StringVar()
        voice_combo = ttk.Combobox(parent_frame, textvariable=voice_var, width=18)
        voice_combo.grid(row=row, column=3, padx=4, pady=4)
        
        # Включаем копирование/вставку
        self.enable_copy_paste(voice_combo)
        
        # ID Голоса (для ElevenLabs) с отслеживанием изменений
        voice_id_var = tk.StringVar()
        voice_id_entry = ttk.Entry(parent_frame, textvariable=voice_id_var, width=20)
        voice_id_entry.grid(row=row, column=4, padx=4, pady=4)
        
        # Включаем копирование/вставку
        self.enable_copy_paste(voice_id_entry)
        
        # Привязываем отслеживание изменений voice_id
        voice_id_var.trace('w', lambda *args, n=name: self.on_voice_id_change(n))
        
        # API Ключ (только для ElevenLabs)
        api_key_var = tk.StringVar()
        api_entry = ttk.Entry(parent_frame, textvariable=api_key_var, width=20)
        api_entry.grid(row=row, column=5, padx=4, pady=4)
        
        # Включаем копирование/вставку для API ключа
        self.enable_copy_paste(api_entry)
        
        # Кнопки действий - используем только grid()
        button_frame = ttk.Frame(parent_frame)
        button_frame.grid(row=row, column=6, padx=2, pady=4)
        
        # Настраиваем grid для button_frame
        button_frame.grid_columnconfigure(0, weight=1)
        button_frame.grid_columnconfigure(1, weight=1)
        
        refresh_btn = ttk.Button(button_frame, text="⟳", width=3,
                               command=lambda n=name: self.check_api_limits(n))
        refresh_btn.grid(row=0, column=0, padx=1)
        
        test_btn = ttk.Button(button_frame, text="🔊", width=3,
                            command=lambda n=name: self.test_character_voice(n))
        test_btn.grid(row=0, column=1, padx=1)
        
        # Статус
        status_var = tk.StringVar(value="Не настроен")
        status_label = ttk.Label(parent_frame, textvariable=status_var, 
                               font=("Arial", 8), foreground="gray")
        status_label.grid(row=row, column=7, padx=4, pady=4, sticky=tk.W)
        
        # Сохраняем все переменные для персонажа
        self.character_vars[name] = {
            'gender': gender_var,
            'engine': engine_var,
            'voice': voice_var,
            'voice_id': voice_id_var,
            'api_key': api_key_var,
            'status': status_var,
            'voice_combo': voice_combo,
            'voice_id_entry': voice_id_entry,
            'api_entry': api_entry
        }
    
    def toggle_api_fields(self):
        """Переключение видимости полей API в зависимости от выбранного движка"""
        for name, vars_dict in self.character_vars.items():
            engine = vars_dict['engine'].get()
            voice_id_entry = vars_dict['voice_id_entry']
            api_entry = vars_dict['api_entry']
            
            if engine == "elevenlabs":
                # Показываем поля для ElevenLabs - используем только grid()
                voice_id_entry.grid()
                api_entry.grid()
            else:
                # Скрываем поля для других движков - используем grid_remove()
                voice_id_entry.grid_remove()
                api_entry.grid_remove()
    
    def enable_copy_paste(self, widget):
        """Включение копирования/вставки для виджета"""
        def copy_text(event):
            try:
                widget.clipboard_clear()
                if hasattr(widget, 'selection_get'):
                    widget.clipboard_append(widget.selection_get())
                else:
                    widget.clipboard_append(widget.get())
            except:
                pass
        
        def paste_text(event):
            try:
                text = widget.clipboard_get()
                if hasattr(widget, 'delete') and hasattr(widget, 'insert'):
                    widget.delete(0, tk.END)
                    widget.insert(0, text)
                elif hasattr(widget, 'set'):
                    widget.set(text)
            except:
                pass
        
        def cut_text(event):
            try:
                copy_text(event)
                if hasattr(widget, 'delete'):
                    widget.delete(0, tk.END)
            except:
                pass
        
        def select_all(event):
            try:
                if hasattr(widget, 'select_range'):
                    widget.select_range(0, tk.END)
                elif hasattr(widget, 'selection_range'):
                    widget.selection_range(0, tk.END)
            except:
                pass
        
        widget.bind('<Control-c>', copy_text)
        widget.bind('<Control-v>', paste_text)
        widget.bind('<Control-x>', cut_text)
        widget.bind('<Control-a>', select_all)
    
    def on_engine_change(self, character_name):
        """Обработка изменения TTS движка"""
        if character_name not in self.character_vars:
            return
            
        vars_dict = self.character_vars[character_name]
        engine = vars_dict['engine'].get()
        voice_combo = vars_dict['voice_combo']
        
        # Обновляем список доступных голосов
        voices = self.tts_manager.get_voices_for_engine(engine)
        voice_combo['values'] = voices
        
        # Очищаем текущий выбор
        vars_dict['voice'].set("")
        
        # Переключаем видимость API полей
        self.toggle_api_fields()
        
        # Обновляем статус
        self.update_character_status(character_name)
    
    def on_voice_id_change(self, character_name):
        """Обработка изменения Voice ID"""
        if character_name not in self.character_vars:
            return
            
        vars_dict = self.character_vars[character_name]
        voice_id = vars_dict['voice_id'].get().strip()
        
        if voice_id:
            # Если введен voice_id, очищаем стандартный voice
            vars_dict['voice'].set("")
        
        # Обновляем статус
        self.update_character_status(character_name)
    
    def update_character_status(self, character_name):
        """Обновление статуса настройки персонажа"""
        if character_name not in self.character_vars:
            return
            
        vars_dict = self.character_vars[character_name]
        engine = vars_dict['engine'].get()
        voice = vars_dict['voice'].get()
        voice_id = vars_dict['voice_id'].get().strip()
        api_key = vars_dict['api_key'].get().strip()
        
        if not engine:
            status = "Выберите TTS"
            color = "red"
        elif engine == "elevenlabs":
            if not api_key:
                status = "Нужен API ключ"
                color = "red"
            elif not voice_id and not voice:
                status = "Нужен Voice ID или голос"
                color = "red"
            else:
                status = "Настроен"
                color = "green"
        else:
            if not voice:
                status = "Выберите голос"
                color = "red"
            else:
                status = "Настроен"
                color = "green"
        
        vars_dict['status'].set(status)
        # Обновляем цвет статуса через parent widget
        status_label = None
        for child in vars_dict['status']._root().winfo_children():
            if hasattr(child, 'cget') and child.cget('textvariable') == str(vars_dict['status']):
                child.configure(foreground=color)
                break
    
    def check_api_limits(self, character_name):
        """Проверка лимитов API для персонажа"""
        if character_name not in self.character_vars:
            return
            
        vars_dict = self.character_vars[character_name]
        engine = vars_dict['engine'].get()
        api_key = vars_dict['api_key'].get().strip()
        
        if engine == "elevenlabs" and api_key:
            try:
                # Здесь можно добавить проверку лимитов через API
                messagebox.showinfo("Лимиты API", f"Проверка лимитов для {character_name}\nAPI: {api_key[:10]}...")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Ошибка проверки API: {e}")
        else:
            messagebox.showwarning("Предупреждение", "Для проверки лимитов нужен ElevenLabs API ключ")
    
    def test_character_voice(self, character_name):
        """Тестирование голоса персонажа"""
        if character_name not in self.character_vars:
            return
            
        vars_dict = self.character_vars[character_name]
        engine = vars_dict['engine'].get()
        voice = vars_dict['voice'].get()
        voice_id = vars_dict['voice_id'].get().strip()
        api_key = vars_dict['api_key'].get().strip()
        
        if not engine:
            messagebox.showwarning("Предупреждение", "Сначала выберите TTS движок")
            return
        
        # Проверяем настройки в зависимости от движка
        if engine == "elevenlabs":
            if not api_key:
                messagebox.showwarning("Предупреждение", "Для ElevenLabs нужен API ключ")
                return
            if not voice_id and not voice:
                messagebox.showwarning("Предупреждение", "Для ElevenLabs нужен Voice ID или голос")
                return
        else:
            if not voice:
                messagebox.showwarning("Предупреждение", "Выберите голос для тестирования")
                return
        
        try:
            # Тестовый текст
            test_text = f"Привет! Меня зовут {character_name}. Это тест моего голоса."
            
            # Создаем временные настройки персонажа
            temp_settings = {
                'tts_engine': engine,
                'voice': voice,
                'api_key': api_key,
                'voice_id': voice_id
            }
            
            # Генерируем аудио через TTS менеджер
            audio_data = self.tts_manager.generate_speech(test_text, temp_settings)
            
            if audio_data:
                # Сохраняем во временный файл и воспроизводим
                temp_file = f"temp_test_{character_name}.mp3"
                with open(temp_file, 'wb') as f:
                    f.write(audio_data)
                
                # Воспроизводим
                pygame.mixer.music.load(temp_file)
                pygame.mixer.music.play()
                
                messagebox.showinfo("Тест голоса", f"Воспроизводится тест голоса для {character_name}")
                
                # Удаляем временный файл после воспроизведения
                def cleanup():
                    try:
                        if os.path.exists(temp_file):
                            os.remove(temp_file)
                    except:
                        pass
                
                self.window.after(5000, cleanup)  # Удаляем через 5 секунд
            else:
                messagebox.showerror("Ошибка", "Не удалось сгенерировать тестовое аудио")
                
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка тестирования голоса: {e}")
    
    def load_character_data(self):
        """Загрузка данных персонажей из профиля"""
        if not self.profile:
            return
            
        for name in self.characters.keys():
            if name in self.character_vars:
                char_data = self.profile.get_character(name)
                if char_data:
                    vars_dict = self.character_vars[name]
                    
                    # Загружаем сохраненные данные
                    vars_dict['gender'].set(char_data.get('gender', 'unknown'))
                    vars_dict['engine'].set(char_data.get('tts_engine', ''))
                    vars_dict['voice'].set(char_data.get('voice', ''))
                    vars_dict['voice_id'].set(char_data.get('voice_id', ''))
                    vars_dict['api_key'].set(char_data.get('api_key', ''))
                    
                    # Обновляем доступные голоса
                    engine = char_data.get('tts_engine', '')
                    if engine:
                        voices = self.tts_manager.get_voices_for_engine(engine)
                        vars_dict['voice_combo']['values'] = voices
                    
                    # Обновляем статус
                    self.update_character_status(name)
        
        # Переключаем видимость API полей
        self.toggle_api_fields()
    
    def apply_settings(self):
        """Применение настроек без закрытия окна"""
        self.save_character_settings()
        messagebox.showinfo("Успех", "Настройки применены")
    
    def save_settings(self):
        """Сохранение настроек и закрытие окна"""
        self.save_character_settings()
        self.window.destroy()
    
    def save_character_settings(self):
        """Сохранение настроек всех персонажей в профиль"""
        if not self.profile:
            return
        
        for name, vars_dict in self.character_vars.items():
            # Получаем значения из полей
            gender = vars_dict['gender'].get()
            engine = vars_dict['engine'].get()
            voice = vars_dict['voice'].get()
            voice_id = vars_dict['voice_id'].get().strip()
            api_key = vars_dict['api_key'].get().strip()
            
            # Подсчет токенов для персонажа
            estimated_tokens = 0
            if name in self.characters and engine == 'elevenlabs':
                # Простая оценка: 1 токен = ~4 символа
                char_text = ' '.join([line.get('text', '') for line in self.characters[name]])
                estimated_tokens = len(char_text) // 4
            
            # Обновляем или добавляем персонажа в профиль
            if name in [char['name'] for char in self.profile.get_all_characters().values()]:
                # Обновляем существующего персонажа
                self.profile.update_character(
                    name,
                    tts_engine=engine,
                    voice=voice,
                    gender=gender,
                    api_key=api_key,
                    voice_id=voice_id,
                    estimated_tokens=estimated_tokens
                )
            else:
                # Добавляем нового персонажа
                self.profile.add_character(
                    name=name,
                    tts_engine=engine,
                    voice=voice,
                    gender=gender,
                    api_key=api_key,
                    voice_id=voice_id,
                    estimated_tokens=estimated_tokens
                )
        
        # Сохраняем профиль
        try:
            self.profile.save_profile()
            print("Настройки персонажей сохранены в профиль")
        except Exception as e:
            print(f"Ошибка сохранения профиля: {e}")
            messagebox.showerror("Ошибка", f"Ошибка сохранения: {e}")