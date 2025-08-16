# gui/character_setup.py - окно настройки голосов персонажей
import tkinter as tk
from tkinter import ttk, messagebox
from pathlib import Path
import sys

# Добавляем пути для импортов
sys.path.append(str(Path(__file__).parent.parent))

class CharacterSetupWindow:
    def __init__(self, parent, characters, profile, settings, subtitles=None):
        self.parent = parent
        self.characters = characters
        self.profile = profile
        self.settings = settings
        self.subtitles = subtitles
        
        # Создаем окно
        self.window = tk.Toplevel(parent)
        self.window.title("Настройка голосов персонажей")
        self.window.geometry("800x600")
        self.window.minsize(600, 400)
        
        # Делаем окно модальным
        self.window.transient(parent)
        self.window.grab_set()
        
        # Переменные для API настроек
        self.api_enabled = tk.BooleanVar()
        
        self.setup_ui()
        
    def setup_ui(self):
        """Настройка интерфейса"""
        # Основная рамка
        main_frame = ttk.Frame(self.window, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Заголовок
        title_label = ttk.Label(main_frame, text="Настройка голосов персонажей", 
                              font=("Arial", 14, "bold"))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 10), sticky=tk.W)
        
        # Таблица персонажей
        self.setup_character_table(main_frame)
        
        # Панель настроек
        self.setup_settings_panel(main_frame)
        
        # Кнопки управления - используем grid() вместо pack()
        self.setup_control_buttons(main_frame)
        
        # Настройка весов для изменения размера
        self.window.columnconfigure(0, weight=1)
        self.window.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(1, weight=1)
        
    def setup_character_table(self, parent):
        """Настройка таблицы персонажей"""
        # Рамка для таблицы
        table_frame = ttk.LabelFrame(parent, text="Персонажи", padding="5")
        table_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        
        # Таблица
        columns = ("Имя", "Реплики", "Время", "TTS", "Статус")
        self.character_tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=8)
        
        # Настройка колонок
        for col in columns:
            self.character_tree.heading(col, text=col)
            if col == "Имя":
                self.character_tree.column(col, width=150, minwidth=100)
            elif col == "Реплики":
                self.character_tree.column(col, width=80, minwidth=60)
            elif col == "Время":
                self.character_tree.column(col, width=80, minwidth=60)
            elif col == "TTS":
                self.character_tree.column(col, width=120, minwidth=80)
            else:
                self.character_tree.column(col, width=100, minwidth=80)
        
        # Скроллбар
        scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.character_tree.yview)
        self.character_tree.configure(yscrollcommand=scrollbar.set)
        
        self.character_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # Настройка весов
        table_frame.columnconfigure(0, weight=1)
        table_frame.rowconfigure(0, weight=1)
        
        # Привязка событий
        self.character_tree.bind('<<TreeviewSelect>>', self.on_character_select)
        
        # Заполняем таблицу
        self.populate_character_table()
        
    def setup_settings_panel(self, parent):
        """Настройка панели настроек"""
        # Рамка для настроек
        settings_frame = ttk.LabelFrame(parent, text="Настройки голоса", padding="5")
        settings_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)
        
        # Выбор TTS движка
        ttk.Label(settings_frame, text="TTS движок:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.tts_var = tk.StringVar()
        self.tts_combo = ttk.Combobox(settings_frame, textvariable=self.tts_var, 
                                     values=["ElevenLabs", "Azure", "Google"], width=20)
        self.tts_combo.grid(row=0, column=1, sticky=tk.W, padx=(5, 0), pady=2)
        self.tts_combo.bind('<<ComboboxSelected>>', self.on_tts_change)
        
        # Чекбокс для API настроек
        self.api_checkbox = ttk.Checkbutton(settings_frame, text="Использовать API", 
                                          variable=self.api_enabled, command=self.toggle_api_fields)
        self.api_checkbox.grid(row=0, column=2, sticky=tk.W, padx=(10, 0), pady=2)
        
        # API настройки (изначально скрыты)
        self.api_key_label = ttk.Label(settings_frame, text="API ключ:")
        self.api_key_var = tk.StringVar()
        self.api_key_entry = ttk.Entry(settings_frame, textvariable=self.api_key_var, width=30, show="*")
        
        self.voice_id_label = ttk.Label(settings_frame, text="Voice ID:")
        self.voice_id_var = tk.StringVar()
        self.voice_id_entry = ttk.Entry(settings_frame, textvariable=self.voice_id_var, width=30)
        
        # Голос (для обычного выбора)
        self.voice_label = ttk.Label(settings_frame, text="Голос:")
        self.voice_var = tk.StringVar()
        self.voice_combo = ttk.Combobox(settings_frame, textvariable=self.voice_var, width=20)
        
        # Размещаем элементы голоса (изначально видимые)
        self.voice_label.grid(row=1, column=0, sticky=tk.W, pady=2)
        self.voice_combo.grid(row=1, column=1, sticky=tk.W, padx=(5, 0), pady=2)
        
        # Настройка весов
        settings_frame.columnconfigure(1, weight=1)
        
    def setup_control_buttons(self, parent):
        """Настройка кнопок управления - используем grid() для всех кнопок"""
        # Рамка для кнопок
        button_frame = ttk.Frame(parent)
        button_frame.grid(row=3, column=0, columnspan=3, pady=10)
        
        # Кнопки - используем grid() вместо pack()
        self.refresh_button = ttk.Button(button_frame, text="Обновить", command=self.refresh)
        self.refresh_button.grid(row=0, column=0, padx=5)
        
        self.test_button = ttk.Button(button_frame, text="Тест голоса", command=self.test)
        self.test_button.grid(row=0, column=1, padx=5)
        
        ttk.Button(button_frame, text="Сохранить", 
                  command=self.save_settings).grid(row=0, column=2, padx=5)
        ttk.Button(button_frame, text="Закрыть", 
                  command=self.close_window).grid(row=0, column=3, padx=5)
        
    def populate_character_table(self):
        """Заполнение таблицы персонажей"""
        for item in self.character_tree.get_children():
            self.character_tree.delete(item)
            
        if not self.characters:
            return
            
        # Получаем статистику персонажей
        from processors.subtitle_analyzer import SubtitleAnalyzer
        analyzer = SubtitleAnalyzer()
        stats = analyzer.get_character_stats(self.characters)
        
        for stat in stats:
            # Получаем настройки из профиля
            char_settings = self.profile.get_character(stat['name']) if self.profile else {}
            tts_engine = char_settings.get('tts_engine', '—')
            
            # Определяем статус
            status = "Настроен" if char_settings else "Не настроен"
            
            self.character_tree.insert("", tk.END, values=(
                stat['name'], 
                stat['lines'], 
                f"{stat['duration']:.1f}s", 
                tts_engine,
                status
            ))
    
    def on_character_select(self, event):
        """Обработка выбора персонажа"""
        selected = self.character_tree.selection()
        if not selected:
            return
            
        # Получаем данные выбранного персонажа
        item = self.character_tree.item(selected[0])
        character_name = item['values'][0]
        
        # Загружаем настройки персонажа
        char_settings = self.profile.get_character(character_name) if self.profile else {}
        
        # Заполняем поля
        self.tts_var.set(char_settings.get('tts_engine', ''))
        self.api_key_var.set(char_settings.get('api_key', ''))
        self.voice_id_var.set(char_settings.get('voice_id', ''))
        self.voice_var.set(char_settings.get('voice', ''))
        
        # Настраиваем видимость API полей
        has_api_key = bool(char_settings.get('api_key', '').strip())
        self.api_enabled.set(has_api_key)
        self.toggle_api_fields()
        
    def on_tts_change(self, event=None):
        """Обработка изменения TTS движка"""
        tts_engine = self.tts_var.get()
        
        if tts_engine == "ElevenLabs":
            self.api_enabled.set(True)
            self.toggle_api_fields()
        else:
            self.api_enabled.set(False)
            self.toggle_api_fields()
            
    def toggle_api_fields(self):
        """Переключение видимости API полей - используем grid()/grid_remove()"""
        if self.api_enabled.get():
            # Показываем API поля
            self.api_key_label.grid(row=1, column=0, sticky=tk.W, pady=2)
            self.api_key_entry.grid(row=1, column=1, sticky=tk.W, padx=(5, 0), pady=2)
            self.voice_id_label.grid(row=2, column=0, sticky=tk.W, pady=2)
            self.voice_id_entry.grid(row=2, column=1, sticky=tk.W, padx=(5, 0), pady=2)
            
            # Скрываем обычное поле голоса
            self.voice_label.grid_remove()
            self.voice_combo.grid_remove()
            
            # Обновляем кнопки с grid позиционированием
            self.refresh_button.grid(row=0, column=0, padx=5)
            self.test_button.grid(row=0, column=1, padx=5)
        else:
            # Скрываем API поля
            self.api_key_label.grid_remove()
            self.api_key_entry.grid_remove()
            self.voice_id_label.grid_remove()
            self.voice_id_entry.grid_remove()
            
            # Показываем обычное поле голоса
            self.voice_label.grid(row=1, column=0, sticky=tk.W, pady=2)
            self.voice_combo.grid(row=1, column=1, sticky=tk.W, padx=(5, 0), pady=2)
            
            # Обновляем кнопки с grid позиционированием
            self.refresh_button.grid(row=0, column=0, padx=5)
            self.test_button.grid(row=0, column=1, padx=5)
    
    def refresh(self):
        """Обновление данных"""
        self.populate_character_table()
        messagebox.showinfo("Информация", "Данные обновлены")
    
    def test(self):
        """Тест выбранного голоса"""
        selected = self.character_tree.selection()
        if not selected:
            messagebox.showwarning("Предупреждение", "Выберите персонажа")
            return
            
        messagebox.showinfo("Информация", "Функция тестирования в разработке")
    
    def save_settings(self):
        """Сохранение настроек персонажа"""
        selected = self.character_tree.selection()
        if not selected:
            messagebox.showwarning("Предупреждение", "Выберите персонажа")
            return
            
        # Получаем данные персонажа
        item = self.character_tree.item(selected[0])
        character_name = item['values'][0]
        
        # Собираем настройки
        settings = {
            'tts_engine': self.tts_var.get(),
            'voice': self.voice_var.get(),
        }
        
        # Добавляем API настройки если включены
        if self.api_enabled.get():
            settings['api_key'] = self.api_key_var.get()
            settings['voice_id'] = self.voice_id_var.get()
        
        # Сохраняем в профиль
        if self.profile:
            self.profile.set_character(character_name, settings)
            
        # Обновляем таблицу
        self.populate_character_table()
        
        messagebox.showinfo("Успех", f"Настройки для '{character_name}' сохранены")
    
    def close_window(self):
        """Закрытие окна"""
        self.window.destroy()