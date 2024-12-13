import os
import customtkinter as ctk
from auth import AuthWindow

# Инициализируем CustomTkinter
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme(os.path.join(os.path.dirname(__file__), 'Themes', 'autumn.json'))

# Основная функция запуска приложения
if __name__ == "__main__":
    app = ctk.CTk()  # Создаём главное окно
    app.title("Textlator - Изучение eng. IT лексика")
    app.geometry("800x800")

    # Запускаем окно авторизации
    AuthWindow(app)

    app.mainloop()
