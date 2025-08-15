# gui/character_setup.py - окно настройки голосов персонажей, выбор TTS и голосов + API ключи
import tkinter as tk
from tkinter import ttk, messagebox

class CharacterSetupWindow:
    def __init__(self, parent, characters, profile, settings):
        self.parent = parent
        self.characters = characters
        self.profile = profile
        self.settings = settings
        
        self.window = tk.Toplevel(parent)
        self.window.title("Настройка голосов персонажей")
        self.window.geometry("1400x700")  # Увеличен для новых колонок
        self.window.minsize(1200, 600)
        self.window.transient(parent)
        self.window.grab_set()
        
        self.tts_engines = ["google_tts", "edge_tts", "gtts", "coqui_tts", "elevenlabs"]
        self.voices_data = self.load_voices_data()
        
        self.setup_ui()
        self.load_existing_settings()
        
    def setup_ui(self):
        """Настройка интерфейса"""
        main_frame = ttk.Frame(self.window, padding="15")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Заголовок
        ttk.Label(main_frame, text="Настройка голосов для персонажей", 
                 font=("Arial", 14, "bold")).grid(row=0, column=0, columnspan=8, pady=15)
        
        # Заголовки колонок с новой колонкой API ключей и ID голоса
        headers = ["Персонаж", "Пол", "TTS Движок", "Голос", "ID Голоса", "API Ключ", "", "Статус"]
        widths = [18, 8, 12, 18, 20, 20, 3, 12]
        
        for i, (header, width) in enumerate(zip(headers, widths)):
            if header:  # Пропускаем пустой заголовок для кнопки
                label = ttk.Label(main_frame, text=header, font=("Arial", 10, "bold"))
                label.grid(row=1, column=i, padx=5, pady=8, sticky=tk.W)
        
        # Скроллируемая область
        canvas = tk.Canvas(main_frame, height=450)
        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.grid(row=2, column=0, columnspan=8, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        scrollbar.grid(row=2, column=8, sticky=(tk.N, tk.S), pady=5)
        
        # Создание строк для каждого персонажа
        self.character_widgets = {}
        
        for i, (name, char_data) in enumerate(self.characters.items()):
            row = i
            
            # Имя персонажа
            name_label = ttk.Label(scrollable_frame, text=name, font=("Arial", 9))
            name_label.grid(row=row, column=0, padx=4, pady=4, sticky=tk.W)
            
            # Пол
            gender_var = tk.StringVar(value=char_data.get('gender', 'unknown'))
            gender_combo = ttk.Combobox(scrollable_frame, textvariable=gender_var, 
                                      values=["male", "female", "unknown"], width=8)
            gender_combo.grid(row=row, column=1, padx=4, pady=4)
            
            # TTS Движок
            engine_var = tk.StringVar()
            engine_combo = ttk.Combobox(scrollable_frame, textvariable=engine_var, 
                                      values=self.tts_engines, width=12)
            engine_combo.grid(row=row, column=2, padx=4, pady=4)
            engine_combo.bind("<<ComboboxSelected>>", 
                            lambda e, n=name: self.on_engine_change(n))
            
            # Голос
            voice_var = tk.StringVar()
            voice_combo = ttk.Combobox(scrollable_frame, textvariable=voice_var, width=18)
            voice_combo.grid(row=row, column=3, padx=4, pady=4)
            
            # ID Голоса (для ElevenLabs)
            voice_id_var = tk.StringVar()
            voice_id_entry = ttk.Entry(scrollable_frame, textvariable=voice_id_var, width=20)
            voice_id_entry.grid(row=row, column=4, padx=4, pady=4)
            
            # API Ключ (только для ElevenLabs) - БЕЗ СКРЫТИЯ
            api_key_var = tk.StringVar()
            api_entry = ttk.Entry(scrollable_frame, textvariable=api_key_var, width=20)
            api_entry.grid(row=row, column=5, padx=4, pady=4)
            
            # Кнопка проверки лимитов
            refresh_btn = ttk.Button(scrollable_frame, text="⟳", width=3,
                                   command=lambda n=name: self.check_api_limits(n))
            refresh_btn.grid(row=row, column=6, padx=2, pady=4)
            
            # Статус
            status_var = tk.StringVar(value="Не настроен")
            status_label = ttk.Label(scrollable_frame, textvariable=status_var, 
                                   font=("Arial", 8), foreground="gray")
            status_label.grid(row=row, column=7, padx=4, pady=4, sticky=tk.W)
            
            # Сохраняем виджеты
            self.character_widgets[name] = {
                'gender': gender_var,
                'engine': engine_var,
                'voice': voice_var,
                'voice_combo': voice_combo,
                'voice_id': voice_id_var,
                'voice_id_entry': voice_id_entry,
                'api_key': api_key_var,
                'api_entry': api_entry,
                'refresh_btn': refresh_btn,
                'status': status_var
            }
            
            # Изначально скрываем API поля
            self.toggle_api_fields(name, False)
        
        # Кнопки
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=3, column=0, columnspan=8, pady=15)
        
        ttk.Button(button_frame, text="Автонастройка", 
                  command=self.auto_setup, width=18).pack(side=tk.LEFT, padx=10)
        ttk.Button(button_frame, text="Сохранить", 
                  command=self.save_settings, width=15).pack(side=tk.LEFT, padx=10)
        ttk.Button(button_frame, text="Отмена", 
                  command=self.window.destroy, width=12).pack(side=tk.LEFT, padx=10)
        
        # Настройка весов для изменения размера
        main_frame.columnconfigure(3, weight=1)  # Колонка голосов
        main_frame.columnconfigure(4, weight=1)  # Колонка ID голосов
        main_frame.columnconfigure(5, weight=1)  # Колонка API ключей
        main_frame.rowconfigure(2, weight=1)     # Скроллируемая область
        
        self.window.columnconfigure(0, weight=1)
        self.window.rowconfigure(0, weight=1)
        
    def toggle_api_fields(self, character_name, show):
        """Показать/скрыть поля API ключей и ID голосов для ElevenLabs"""
        widgets = self.character_widgets[character_name]
        
        if show:
            widgets['voice_id_entry'].grid()
            widgets['api_entry'].grid()
            widgets['refresh_btn'].grid()
        else:
            widgets['voice_id_entry'].grid_remove()
            widgets['api_entry'].grid_remove()
            widgets['refresh_btn'].grid_remove()
        
    def load_voices_data(self):
        """Загрузка данных о голосах для TTS движков"""
        return {
            "google_tts": ["pl-PL-Standard-A", "pl-PL-Standard-B", "pl-PL-Standard-C", "pl-PL-Standard-D"],
            "edge_tts": ["pl-PL-MarekNeural", "pl-PL-ZofiaNeural"],
            "gtts": ["pl"],
            "coqui_tts": ["tts_models/pl/mai_female/glow-tts"],
            "elevenlabs": ["Rachel", "Domi", "Bella", "Antoni", "Elli", "Josh", "Arnold", "Adam", "Sam"]
        }
    
    def on_engine_change(self, character_name):
        """Обработка изменения TTS движка"""
        widgets = self.character_widgets[character_name]
        engine = widgets['engine'].get()
        
        if engine in self.voices_data:
            voices = self.voices_data[engine]
            widgets['voice_combo']['values'] = voices
            if voices:
                widgets['voice'].set(voices[0])
                widgets['status'].set("⚠ Изменен")
        else:
            widgets['voice_combo']['values'] = []
            widgets['voice'].set('')
            widgets['status'].set("Не настроен")
        
        # Показать/скрыть API поля только для ElevenLabs
        show_api = (engine == "elevenlabs")
        self.toggle_api_fields(character_name, show_api)
    
    def check_api_limits(self, character_name):
        """Проверка лимитов API для персонажа"""
        widgets = self.character_widgets[character_name]
        api_key = widgets['api_key'].get().strip()
        
        if not api_key:
            widgets['status'].set("⚠ Нет API ключа")
            return
        
        widgets['status'].set("⏳ Проверка...")
        self.window.update()
        
        try:
            # Импортируем модуль для работы с ElevenLabs API
            from tts_engines.elevenlabs.elevenlabs_api import ElevenLabsAPI
            
            api = ElevenLabsAPI(api_key)
            credits_info = api.get_credits_info()
            
            if credits_info:
                available = credits_info['credits_available']
                total = credits_info['credits_total']
                
                # Получаем оценку нужных токенов для персонажа
                needed_tokens = self.estimate_character_tokens(character_name)
                
                if available >= needed_tokens:
                    widgets['status'].set(f"✓ {available}/{total} (+{needed_tokens})")
                else:
                    widgets['status'].set(f"⚠ {available}/{total} нужно {needed_tokens}")
            else:
                widgets['status'].set("❌ Ошибка API")
                
        except ImportError:
            widgets['status'].set("❌ API модуль не найден")
        except Exception as e:
            widgets['status'].set(f"❌ {str(e)[:15]}...")
    
    def estimate_character_tokens(self, character_name):
        """Оценка нужных токенов для персонажа"""
        try:
            from utils.text_counter import TextCounter
            
            counter = TextCounter()
            # Здесь будет логика подсчета токенов из субтитров
            # Пока возвращаем примерное значение
            return 500  # Заглушка
            
        except ImportError:
            return 500  # Заглушка если модуль не найден
    
    def auto_setup(self):
        """Автоматическая настройка голосов только для новых персонажей"""
        male_voices = {
            "google_tts": ["pl-PL-Standard-B", "pl-PL-Standard-D"],
            "edge_tts": ["pl-PL-MarekNeural"],
            "elevenlabs": ["Antoni", "Josh", "Arnold", "Adam", "Sam"]
        }
        
        female_voices = {
            "google_tts": ["pl-PL-Standard-A", "pl-PL-Standard-C"],
            "edge_tts": ["pl-PL-ZofiaNeural"],
            "elevenlabs": ["Rachel", "Domi", "Bella", "Elli"]
        }
        
        engine_priority = ["edge_tts", "google_tts", "elevenlabs", "gtts", "coqui_tts"]
        
        used_voices = {"male": {}, "female": {}}
        new_characters_configured = 0
        
        for name, widgets in self.character_widgets.items():
            char_settings = self.profile.get_character(name)
            if char_settings and char_settings.get('tts_engine') and char_settings.get('voice'):
                print(f"Пропускаем {name} - уже настроен")
                continue
                
            gender = widgets['gender'].get()
            print(f"Настраиваем нового персонажа: {name} ({gender})")
            
            selected_engine = engine_priority[0]
            widgets['engine'].set(selected_engine)
            self.on_engine_change(name)
            
            if gender == "male" and selected_engine in male_voices:
                available_voices = male_voices[selected_engine]
                voice_index = used_voices["male"].get(selected_engine, 0)
                if voice_index < len(available_voices):
                    voice = available_voices[voice_index]
                    widgets['voice'].set(voice)
                    widgets['status'].set("🔧 Автонастройка")
                    used_voices["male"][selected_engine] = voice_index + 1
                    new_characters_configured += 1
            elif gender == "female" and selected_engine in female_voices:
                available_voices = female_voices[selected_engine]
                voice_index = used_voices["female"].get(selected_engine, 0)
                if voice_index < len(available_voices):
                    voice = available_voices[voice_index]
                    widgets['voice'].set(voice)
                    widgets['status'].set("🔧 Автонастройка")
                    used_voices["female"][selected_engine] = voice_index + 1
                    new_characters_configured += 1
        
        if new_characters_configured > 0:
            print(f"Автонастройка завершена. Настроено: {new_characters_configured}")
        else:
            print("Все персонажи уже настроены")
    
    def load_existing_settings(self):
        """Загрузка существующих настроек из профиля"""
        print(f"\n=== ЗАГРУЗКА СУЩЕСТВУЮЩИХ НАСТРОЕК ===")
        
        for name, widgets in self.character_widgets.items():
            char_settings = self.profile.get_character(name)
            if char_settings:
                print(f"Загружаем настройки для {name}")
                
                widgets['gender'].set(char_settings.get('gender', 'unknown'))
                widgets['engine'].set(char_settings.get('tts_engine', ''))
                
                if char_settings.get('tts_engine'):
                    self.on_engine_change(name)
                    widgets['voice'].set(char_settings.get('voice', ''))
                    
                    # Загружаем настройки для ElevenLabs
                    if char_settings.get('tts_engine') == 'elevenlabs':
                        api_key = char_settings.get('api_key', '')
                        voice_id = char_settings.get('voice_id', '')
                        widgets['api_key'].set(api_key)
                        widgets['voice_id'].set(voice_id)
                    
                    widgets['status'].set("✓ Настроен")
                    
                print(f"✓ Загружены настройки для {name}")
            else:
                widgets['status'].set("Не настроен")
                print(f"✗ Настройки для {name} не найдены")
    
    def save_settings(self):
        """Сохранение настроек в профиль"""
        try:
            saved_count = 0
            print("\n=== НАЧИНАЕМ СОХРАНЕНИЕ ПРОФИЛЯ ===")
            
            for name, widgets in self.character_widgets.items():
                gender = widgets['gender'].get()
                engine = widgets['engine'].get()
                voice = widgets['voice'].get()
                api_key = widgets['api_key'].get() if engine == 'elevenlabs' else ''
                voice_id = widgets['voice_id'].get() if engine == 'elevenlabs' else ''
                
                print(f"Обрабатываем {name}: {engine}, {voice}, voice_id: {voice_id}")
                
                if engine and voice:
                    # Добавляем персонажа с API ключом и voice_id
                    self.profile.add_character(name, engine, voice, gender, api_key, voice_id)
                    widgets['status'].set("✓ Сохранен")
                    print(f"✓ Добавлен: {name}")
                    saved_count += 1
                else:
                    widgets['status'].set("Ошибка")
                    print(f"✗ Пропущен {name}")
            
            self.profile.save_profile()
            print(f"Профиль сохранен: {self.profile.profile_path}")
            
            messagebox.showinfo("Успех", f"Настройки сохранены\nПерсонажей: {saved_count}")
            self.window.destroy()
            
        except Exception as e:
            print(f"ОШИБКА сохранения: {e}")
            messagebox.showerror("Ошибка", f"Не удалось сохранить: {e}")