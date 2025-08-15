# main.py - точка входа приложения, запуск GUI и инициализация компонентов
import sys
import os
from pathlib import Path

# Добавляем пути для импортов
src_path = Path(__file__).parent
sys.path.append(str(src_path))

from gui.main_window import MainWindow
from config.settings import Settings

def main():
    try:
        # Инициализация настроек
        settings = Settings()
        
        # Запуск GUI
        app = MainWindow(settings)
        app.run()
        
    except Exception as e:
        print(f"Ошибка запуска: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()