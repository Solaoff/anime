# gui/main_window.py - главное окно приложения, интерфейс для работы с проектом
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pathlib import Path
import sys
import os

# Добавляем пути для импортов
sys.path.append(str(Path(__file__).parent.parent))

from processors.subtitle_analyzer import SubtitleAnalyzer
from profiles.character_profile import ProfileManager
from gui.character_setup import CharacterSetupWindow

class MainWindow:
    def __init__(self, settings):
        self.settings = settings
        self.root = tk.Tk()
        self.root.title("Anime Dubbing Tool")
        self.root.geometry("1200x800")  # Увеличен размер
        self.root.minsize(1000, 600)    # Минимальный размер
        
        self.analyzer = SubtitleAnalyzer()
        self.profile_manager = ProfileManager()
        
        self.current_subtitles = None
        self.current_characters = None
        self.current_profile = None
        
        self.setup_ui()
        
    def setup_ui(self):
        """Настройка интерфейса"""
        # Главное меню
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Файл", menu=file_menu)
        file_menu.add_command(label="Загрузить субтитры", command=self.load_subtitles)
        file_menu.add_command(label="Сохранить профиль", command=self.save_profile)
        file_menu.add_command(label="Загрузить профиль", command=self.load_profile)
        
        # Основная рамка
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Создаем status_var в начале
        self.status_var = tk.StringVar(value="Готов к работе")
        
        # Настройка проекта
        project_frame = ttk.LabelFrame(main_frame, text="Проект", padding="5")
        project_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        ttk.Label(project_frame, text="Название аниме:").grid(row=0, column=0, sticky=tk.W)
        self.anime_name_var = tk.StringVar()
        
        # Выпадающий список вместо обычного поля
        self.anime_name_combo = ttk.Combobox(project_frame, textvariable=self.anime_name_var, width=35)
        self.anime_name_combo.grid(row=0, column=1, padx=5, sticky=(tk.W, tk.E))
        
        ttk.Button(project_frame, text="Обновить список", 
                  command=self.update_anime_list, width=15).grid(row=0, column=2, padx=2)
        ttk.Button(project_frame, text="Загрузить субтитры", 
                  command=self.load_subtitles, width=18).grid(row=0, column=3, padx=2)
        
        # Анализ персонажей
        analysis_frame = ttk.LabelFrame(main_frame, text="Анализ персонажей", padding="5")
        analysis_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        
        # Таблица персонажей
        columns = ("Имя", "Реплики", "Время", "Пол", "TTS", "Голос")
        self.character_tree = ttk.Treeview(analysis_frame, columns=columns, show="headings", height=10)
        
        # Настройка колонок с оптимальными размерами
        column_widths = {
            "Имя": 180,
            "Реплики": 80,
            "Время": 100,
            "Пол": 80,
            "TTS": 140,
            "Голос": 200
        }
        
        for col in columns:
            self.character_tree.heading(col, text=col)
            self.character_tree.column(col, width=column_widths[col], minwidth=50)
        
        scrollbar = ttk.Scrollbar(analysis_frame, orient=tk.VERTICAL, command=self.character_tree.yview)
        self.character_tree.configure(yscrollcommand=scrollbar.set)
        
        self.character_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # Кнопки управления
        button_frame = ttk.Frame(analysis_frame)
        button_frame.grid(row=1, column=0, columnspan=2, pady=10)
        
        ttk.Button(button_frame, text="Настроить голоса", 
                  command=self.setup_voices, width=20).pack(side=tk.LEFT, padx=10)
        ttk.Button(button_frame, text="Тест голоса", 
                  command=self.test_voice, width=15).pack(side=tk.LEFT, padx=10)
        ttk.Button(button_frame, text="Начать дубляж", 
                  command=self.start_dubbing, width=18).pack(side=tk.LEFT, padx=10)
        
        # Статус (перемещен в конец)
        status_bar = ttk.Label(main_frame, textvariable=self.status_var, relief=tk.SUNKEN)
        status_bar.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        # Настройка весов для изменения размера
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(1, weight=1)
        analysis_frame.columnconfigure(0, weight=1)
        analysis_frame.rowconfigure(0, weight=1)
        project_frame.columnconfigure(1, weight=1)
        
        # Обновляем список профилей ПОСЛЕ создания всех виджетов
        self.update_anime_list()
    
    def update_anime_list(self):
        """Обновление списка доступных профилей аниме"""
        try:
            available_profiles = self.profile_manager.get_available_profiles()
            self.anime_name_combo['values'] = available_profiles
            print(f"Список профилей обновлен: {available_profiles}")
            
            if available_profiles:
                self.status_var.set(f"Найдено профилей: {len(available_profiles)}")
            else:
                self.status_var.set("Профили не найдены")
                
        except Exception as e:
            print(f"Ошибка обновления списка: {e}")
            self.status_var.set("Ошибка загрузки профилей")
        
    def load_subtitles(self):
        """Загрузка файла субтитров"""
        file_path = filedialog.askopenfilename(
            title="Выберите файл субтитров",
            filetypes=[("SRT files", "*.srt"), ("All files", "*.*")]
        )
        
        if not file_path:
            return
            
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            self.current_subtitles = self.analyzer.parse_srt(content)
            self.current_characters = self.analyzer.analyze_characters(self.current_subtitles)
            
            # Автозаполнение названия аниме из имени файла, если поле пустое
            if not self.anime_name_var.get():
                import os
                filename = os.path.basename(file_path)
                anime_name = filename.replace('.srt', '').replace('_', ' ')
                self.anime_name_var.set(anime_name)
                print(f"Название аниме установлено автоматически: {anime_name}")
            
            self.update_character_table()
            self.status_var.set(f"Загружено {len(self.current_subtitles)} субтитров, {len(self.current_characters)} персонажей")
            print(f"Субтитры загружены: {len(self.current_subtitles)} реплик, {len(self.current_characters)} персонажей")
            
        except Exception as e:
            print(f"Ошибка загрузки субтитров: {e}")
            messagebox.showerror("Ошибка", f"Не удалось загрузить субтитры: {e}")
    
    def update_character_table(self):
        """Обновление таблицы персонажей"""
        for item in self.character_tree.get_children():
            self.character_tree.delete(item)
            
        if not self.current_characters:
            return
            
        stats = self.analyzer.get_character_stats(self.current_characters)
        for stat in stats:
            # Получаем TTS и голос из профиля если есть
            tts_engine = "—"
            voice = "—"
            
            if self.current_profile:
                char_settings = self.current_profile.get_character(stat['name'])
                if char_settings:
                    tts_engine = char_settings.get('tts_engine', '—')
                    voice = char_settings.get('voice', '—')
            
            self.character_tree.insert("", tk.END, values=(
                stat['name'], 
                stat['lines'], 
                f"{stat['duration']:.1f}s", 
                stat['gender'],
                tts_engine,
                voice
            ))
    
    def setup_voices(self):
        """Открыть окно настройки голосов"""
        if not self.current_characters:
            messagebox.showwarning("Предупреждение", "Сначала загрузите субтитры")
            return
            
        if not self.anime_name_var.get():
            messagebox.showwarning("Предупреждение", "Введите название аниме")
            return
        
        anime_name = self.anime_name_var.get()
        print(f"Открываем настройки для аниме: {anime_name}")
        
        # Пытаемся загрузить существующий профиль
        self.current_profile = self.profile_manager.load_profile(anime_name)
        
        # Если профиль не найден, создаем новый
        if not self.current_profile:
            self.current_profile = self.profile_manager.create_profile(anime_name)
            self.status_var.set(f"Создан новый профиль для '{anime_name}'")
            print(f"Создан новый профиль для {anime_name}")
        else:
            self.status_var.set(f"Загружен профиль для '{anime_name}'")
            print(f"Загружен существующий профиль для {anime_name}")
            print(f"В профиле персонажей: {len(self.current_profile.get_all_characters())}")
            
        setup_window = CharacterSetupWindow(self.root, self.current_characters, 
                                          self.current_profile, self.settings)
        self.root.wait_window(setup_window.window)
        
        # Обновляем таблицу и список профилей после настройки
        self.update_character_table()
        self.update_anime_list()
        print("Таблица персонажей и список профилей обновлены")
    
    def test_voice(self):
        """Тест выбранного голоса"""
        selected = self.character_tree.selection()
        if not selected:
            messagebox.showwarning("Предупреждение", "Выберите персонажа")
            return
            
        messagebox.showinfo("Информация", "Функция тестирования в разработке")
    
    def start_dubbing(self):
        """Начать процесс дубляжа"""
        if not self.current_characters:
            messagebox.showwarning("Предупреждение", "Сначала загрузите субтитры")
            return
            
        if not self.current_profile:
            messagebox.showwarning("Предупреждение", "Сначала настройте голоса персонажей")
            return
            
        messagebox.showinfo("Информация", "Функция дубляжа в разработке")
    
    def save_profile(self):
        """Сохранение профиля"""
        if not self.current_profile:
            messagebox.showwarning("Предупреждение", "Нет профиля для сохранения")
            return
            
        try:
            self.current_profile.save_profile()
            messagebox.showinfo("Успех", "Профиль сохранен")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить профиль: {e}")
    
    def load_profile(self):
        """Загрузка профиля"""
        profiles = self.profile_manager.get_available_profiles()
        if not profiles:
            messagebox.showinfo("Информация", "Нет сохраненных профилей")
            return
            
        # Простой диалог выбора профиля
        messagebox.showinfo("Информация", "Функция загрузки профиля в разработке")
    
    def run(self):
        """Запуск приложения"""
        self.root.mainloop()