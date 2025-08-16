# gui/character_setup.py - окно настройки голосов персонажей, выбор TTS и голосов + API ключи + тестирование
import tkinter as tk
from tkinter import ttk, messagebox
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

# Импортируем TTS менеджер
from tts_engines.tts_manager import TTSManager

class CharacterSetupWindow:
    def __init__(self, parent, characters, profile, settings, subtitles=None):
        self.parent = parent
        self.characters = characters
        self.profile = profile
        self.settings = settings
        self.subtitles = subtitles  # Данные субтитров для расчета токенов
        self.character_tokens = {}  # Кеш рассчитанных токенов
        
        # Инициализируем TTS менеджер
        self.tts_manager = TTSManager(settings)
        
        self.window = tk.Toplevel(parent)
        self.window.title("Настройка голосов персонажей")
        self.window.geometry("1200x700")  # Уменьшен размер
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
                 font=("Arial", 14, "bold")).grid(row=0, column=0, columnspan=7, pady=15)
        
        # Заголовки колонок
        headers = ["Персонаж", "Пол", "TTS Движок", "Голос", "ID Голоса", "API Ключ", "Тест", "Статус"]
        widths = [18, 8, 12, 18, 20, 20, 8, 12]
        
        for i, (header, width) in enumerate(zip(headers, widths)):
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
        
        canvas.grid(row=2, column=0, columnspan=7, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        scrollbar.grid(row=2, column=7, sticky=(tk.N, tk.S), pady=5)
        
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
            
            # Включаем копирование/вставку
            self.enable_copy_paste(gender_combo)
            
            # TTS Движок
            engine_var = tk.StringVar()
            engine_combo = ttk.Combobox(scrollable_frame, textvariable=engine_var, 
                                      values=self.tts_engines, width=12)
            engine_combo.grid(row=row, column=2, padx=4, pady=4)
            engine_combo.bind("<<ComboboxSelected>>", 
                            lambda e, n=name: self.on_engine_change(n))
            
            # Включаем копирование/вставку
            self.enable_copy_paste(engine_combo)
            
            # Голос (стандартный выбор)
            voice_var = tk.StringVar()
            voice_combo = ttk.Combobox(scrollable_frame, textvariable=voice_var, width=18)
            voice_combo.grid(row=row, column=3, padx=4, pady=4)
            
            # Включаем копирование/вставку
            self.enable_copy_paste(voice_combo)
            
            # ID Голоса (для ElevenLabs) с отслеживанием изменений
            voice_id_var = tk.StringVar()
            voice_id_entry = ttk.Entry(scrollable_frame, textvariable=voice_id_var, width=20)
            voice_id_entry.grid(row=row, column=4, padx=4, pady=4)
            
            # Включаем копирование/вставку
            self.enable_copy_paste(voice_id_entry)
            
            # Привязываем отслеживание изменений voice_id
            voice_id_var.trace('w', lambda *args, n=name: self.on_voice_id_change(n))
            
            # API Ключ (только для ElevenLabs)
            api_key_var = tk.StringVar()
            api_entry = ttk.Entry(scrollable_frame, textvariable=api_key_var, width=20)
            api_entry.grid(row=row, column=5, padx=4, pady=4)
            
            # Включаем копирование/вставку для API ключа
            self.enable_copy_paste(api_entry)
            
            # Кнопка проверки лимитов и теста в одной колонке
            button_frame = ttk.Frame(scrollable_frame)
            button_frame.grid(row=row, column=6, padx=2, pady=4)
            
            refresh_btn = ttk.Button(button_frame, text="⟳", width=3,
                                   command=lambda n=name: self.check_api_limits(n))
            refresh_btn.grid(row=0, column=0)
            
            test_btn = ttk.Button(button_frame, text="🔊", width=3,
                                command=lambda n=name: self.test_character_voice(n))
            test_btn.grid(row=0, column=1)
            
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
                'test_btn': test_btn,
                'status': status_var
            }
            
            # Изначально скрываем API поля
            self.toggle_api_fields(name, False)
        
        # Кнопки
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=3, column=0, columnspan=7, pady=15)
        
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
        
    def enable_copy_paste(self, widget):
        """Включаем копирование и вставку для любого виджета"""
        def on_copy(event=None):
            try:
                widget.tk.call('tk::TextCopy', widget)
            except:
                try:
                    if hasattr(widget, 'selection_get'):
                        text = widget.selection_get()
                        widget.clipboard_clear()
                        widget.clipboard_append(text)
                except:
                    pass
                    
        def on_paste(event=None):
            try:
                widget.tk.call('tk::TextPaste', widget)
            except:
                try:
                    text = widget.clipboard_get()
                    if hasattr(widget, 'insert'):
                        pos = widget.index(tk.INSERT) if hasattr(widget, 'index') else tk.END
                        widget.insert(pos, text)
                except:
                    pass
                    
        def on_cut(event=None):
            try:
                widget.tk.call('tk::TextCut', widget)
            except:
                try:
                    if hasattr(widget, 'selection_get'):
                        text = widget.selection_get()
                        widget.clipboard_clear()
                        widget.clipboard_append(text)
                        widget.delete(tk.SEL_FIRST, tk.SEL_LAST)
                except:
                    pass
                    
        def on_select_all(event=None):
            try:
                if hasattr(widget, 'select_range'):
                    widget.select_range(0, tk.END)
                elif hasattr(widget, 'tag_add'):
                    widget.tag_add(tk.SEL, "1.0", tk.END)
                elif hasattr(widget, 'selection_range'):
                    widget.selection_range(0, tk.END)
            except:
                pass
            return 'break'
        
        # Привязываем горячие клавиши
        widget.bind('<Control-c>', on_copy)
        widget.bind('<Control-v>', on_paste) 
        widget.bind('<Control-x>', on_cut)
        widget.bind('<Control-a>', on_select_all)
        
        # Дополнительные бинды для контекстного меню
        try:
            widget.bind('<Button-3>', lambda e: self.show_context_menu(e, widget))
        except:
            pass
    
    def show_context_menu(self, event, widget):
        """Показать контекстное меню"""
        try:
            menu = tk.Menu(self.window, tearoff=0)
            menu.add_command(label="Копировать", command=lambda: widget.event_generate('<<Copy>>'))
            menu.add_command(label="Вставить", command=lambda: widget.event_generate('<<Paste>>'))
            menu.add_command(label="Вырезать", command=lambda: widget.event_generate('<<Cut>>'))
            menu.add_separator()
            menu.add_command(label="Выделить все", command=lambda: widget.select_range(0, tk.END) if hasattr(widget, 'select_range') else None)
            menu.tk_popup(event.x_root, event.y_root)
        except:
            pass
        finally:
            try:
                menu.grab_release()
            except:
                pass
        
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
    
    def toggle_voice_selection(self, character_name, show_standard_voice):
        """Показать/скрыть стандартный выбор голоса в зависимости от voice_id"""
        widgets = self.character_widgets[character_name]
        
        if show_standard_voice:
            # Показываем стандартный выбор голоса
            widgets['voice_combo'].grid()
        else:
            # Скрываем стандартный выбор голоса (когда есть voice_id)
            widgets['voice_combo'].grid_remove()
    
    def on_voice_id_change(self, character_name):
        """Обработка изменения voice_id - умное скрытие голосов"""
        widgets = self.character_widgets[character_name]
        voice_id = widgets['voice_id'].get().strip()
        
        if voice_id:
            # Есть voice_id - скрываем стандартный выбор голоса
            self.toggle_voice_selection(character_name, False)
            # Очищаем стандартный голос чтобы не было конфликтов
            widgets['voice'].set('')
        else:
            # Нет voice_id - показываем стандартный выбор голоса
            self.toggle_voice_selection(character_name, True)
        
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
        
        # Если не ElevenLabs, то всегда показываем стандартный выбор голоса
        if not show_api:
            self.toggle_voice_selection(character_name, True)
            widgets['voice_id'].set('')  # Очищаем voice_id для других движков
    
    def check_api_limits(self, character_name):
        """Проверка лимитов API и расчет токенов для персонажа"""
        widgets = self.character_widgets[character_name]
        api_key = widgets['api_key'].get().strip()
        
        if not api_key:
            widgets['status'].set("⚠ Нет API ключа")
            return
        
        widgets['status'].set("⏳ Расчет токенов...")
        self.window.update()
        
        # 1. Рассчитываем токены персонажа
        character_tokens = self.calculate_character_tokens(character_name)
        
        # 2. Проверяем API лимиты
        widgets['status'].set("⏳ Проверка API...")
        self.window.update()
        
        try:
            from tts_engines.elevenlabs.elevenlabs_api import ElevenLabsAPI
            
            api = ElevenLabsAPI(api_key)
            credits_info = api.get_credits_info()
            
            if credits_info and 'error' not in credits_info:
                available = credits_info['credits_available']
                total = credits_info['credits_total']
                
                # 3. Сохраняем токены в профиль
                self.save_character_tokens(character_name, character_tokens)
                
                # 4. Отображаем результат
                if available >= character_tokens:
                    widgets['status'].set(f"✓ {available}/{total} ({character_tokens} ток.)")
                else:
                    widgets['status'].set(f"⚠ {available}/{total} нужно {character_tokens}")
            else:
                error_msg = credits_info.get('error', 'Неизвестная ошибка') if credits_info else 'Нет ответа'
                if 'Неверный API ключ' in error_msg:
                    widgets['status'].set("❌ Неверный ключ")
                else:
                    widgets['status'].set(f"❌ {error_msg[:15]}...")
                    
        except ImportError:
            widgets['status'].set("❌ API модуль не найден")
        except Exception as e:
            widgets['status'].set(f"❌ {str(e)[:15]}...")
    
    def calculate_character_tokens(self, character_name):
        """Подсчет токенов для персонажа из правильно распарсенных субтитров"""
        if not self.subtitles:
            return 1
        
        character_tokens = 0
        character_lines = 0
        found_texts = []
        
        # Теперь субтитры правильно распарсены, поэтому просто ищем по character
        for subtitle in self.subtitles:
            if subtitle.get('character') == character_name:
                text = subtitle.get('text', '').strip()
                if text:
                    found_texts.append(text)
                    character_lines += 1
                    
                    # Считаем символы в реплике
                    tokens = len(text)
                    character_tokens += tokens
        
        print(f"\n=== ТОКЕНЫ ДЛЯ {character_name.upper()} ===")
        print(f"Найдено реплик: {character_lines}")
        
        # Показываем первые 3 реплики
        for i, text in enumerate(found_texts[:3]):
            print(f"{i+1}: '{text[:40]}{'...' if len(text) > 40 else ''}'")
        
        if len(found_texts) > 3:
            print("   ...")
            
        print(f"Итого: {character_tokens} символов")
        
        return max(character_tokens, 1)
    
    def test_character_voice(self, character_name):
        """Тестирование голоса персонажа"""
        widgets = self.character_widgets[character_name]
        
        # Получаем настройки персонажа
        engine_name = widgets['engine'].get().strip()
        voice = widgets['voice'].get().strip()
        voice_id = widgets['voice_id'].get().strip()
        api_key = widgets['api_key'].get().strip()
        
        if not engine_name:
            widgets['status'].set("⚠ Нет TTS движка")
            return
        
        # Проверяем ElevenLabs
        if engine_name == 'elevenlabs':
            if not api_key:
                widgets['status'].set("⚠ Нет API ключа")
                return
                
            if not voice_id:
                widgets['status'].set("⚠ Нет Voice ID")
                return
                
            # Обновляем статус
            widgets['status'].set("⏳ Тестируем...")
            self.window.update()
            
            # Подготавливаем данные персонажа
            character_data = {
                'api_key': api_key,
                'voice_id': voice_id
            }
            
            test_text = f"Hello, I am {character_name}. This is a voice test."
            
            try:
                result = self.tts_manager.test_voice('ElevenLabs', character_data, test_text)
                
                if result['success']:
                    widgets['status'].set("✅ Тест ок")
                else:
                    widgets['status'].set(f"❌ {result.get('error', 'Ошибка')[:10]}")
                    
            except Exception as e:
                widgets['status'].set(f"❌ Ошибка: {str(e)[:10]}")
        else:
            widgets['status'].set(f"⚠ {engine_name} не поддерживается")

    
    def save_character_tokens(self, character_name, tokens):
        """Сохранить токены в профиль"""
        char_settings = self.profile.get_character(character_name)
        if char_settings:
            self.profile.update_character(character_name, estimated_tokens=tokens)
        else:
            gender = self.character_widgets[character_name]['gender'].get()
            self.profile.add_character(character_name, '', '', gender, '', '', tokens)
    
    def load_existing_settings(self):
        """Загрузка настроек из профиля"""
        for name, widgets in self.character_widgets.items():
            char_settings = self.profile.get_character(name)
            if char_settings:
                widgets['gender'].set(char_settings.get('gender', 'unknown'))
                widgets['engine'].set(char_settings.get('tts_engine', ''))
                
                if char_settings.get('tts_engine'):
                    self.on_engine_change(name)
                    
                    voice_id = char_settings.get('voice_id', '')
                    voice = char_settings.get('voice', '')
                    
                    if voice_id:
                        widgets['voice_id'].set(voice_id)
                        self.toggle_voice_selection(name, False)
                    else:
                        widgets['voice'].set(voice)
                        self.toggle_voice_selection(name, True)
                    
                    if char_settings.get('tts_engine') == 'elevenlabs':
                        api_key = char_settings.get('api_key', '')
                        widgets['api_key'].set(api_key)
                    
                    estimated_tokens = char_settings.get('estimated_tokens', 0)
                    if estimated_tokens > 0:
                        widgets['status'].set(f"✓ Настроен ({estimated_tokens} ток.)")
                    else:
                        widgets['status'].set("✓ Настроен")
            else:
                widgets['status'].set("Не настроен")
    
    def auto_setup(self):
        """Автонастройка голосов"""
        male_voices = {"edge_tts": ["pl-PL-MarekNeural"], "google_tts": ["pl-PL-Standard-B"]}
        female_voices = {"edge_tts": ["pl-PL-ZofiaNeural"], "google_tts": ["pl-PL-Standard-A"]}
        
        used_voices = {"male": {}, "female": {}}
        
        for name, widgets in self.character_widgets.items():
            char_settings = self.profile.get_character(name)
            if char_settings and char_settings.get('tts_engine'):
                continue
                
            gender = widgets['gender'].get()
            engine = "edge_tts"
            
            widgets['engine'].set(engine)
            self.on_engine_change(name)
            
            if gender == "male" and engine in male_voices:
                voice = male_voices[engine][0]
                widgets['voice'].set(voice)
                widgets['status'].set("🔧 Автонастройка")
            elif gender == "female" and engine in female_voices:
                voice = female_voices[engine][0]
                widgets['voice'].set(voice)
                widgets['status'].set("🔧 Автонастройка")
    
    def save_settings(self):
        """Сохранение настроек"""
        try:
            saved_count = 0
            
            for name, widgets in self.character_widgets.items():
                gender = widgets['gender'].get()
                engine = widgets['engine'].get()
                
                voice_id = widgets['voice_id'].get().strip() if engine == 'elevenlabs' else ''
                voice = widgets['voice'].get() if not voice_id else ''
                api_key = widgets['api_key'].get() if engine == 'elevenlabs' else ''
                
                if engine and (voice or voice_id):
                    char_settings = self.profile.get_character(name)
                    estimated_tokens = char_settings.get('estimated_tokens', 0) if char_settings else 0
                    
                    self.profile.add_character(name, engine, voice, gender, api_key, voice_id, estimated_tokens)
                    
                    if estimated_tokens > 0:
                        widgets['status'].set(f"✓ Сохранен ({estimated_tokens} ток.)")
                    else:
                        widgets['status'].set("✓ Сохранен")
                    
                    saved_count += 1
                else:
                    widgets['status'].set("Ошибка")
            
            self.profile.save_profile()
            messagebox.showinfo("Успех", f"Настройки сохранены\nПерсонажей: {saved_count}")
            self.window.destroy()
            
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить: {e}")