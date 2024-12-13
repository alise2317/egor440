import customtkinter as ctk
from tkinter import messagebox
from Learning_page import LearningPage
from Testing_page import TestingPage
from Dictionary_page import DictionaryPage
from Perfomance_page import PerfomancePage
from Profile_page import ProfilePage
from db_manager import DatabaseManager

class MainWindow:
    def __init__(self, root, username):
        self.root = root
        self.username = username
        self.root.title("Главная")
        self.db_manager = DatabaseManager()

        # Устанавливаем размеры окна и центрируем его
        window_width = 800
        window_height = 800
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        # x_coordinate = (screen_width // 2) - (window_width // 2)
        # y_coordinate = (screen_height // 2) - (window_height // 2)
        # self.root.geometry(f"{window_width}x{window_height}+{x_coordinate}+{y_coordinate}")
        self.root.resizable(False, False)

        # Создаём фрейм для кнопок
        self.frame = ctk.CTkFrame(self.root)
        self.frame.pack(pady=20, padx=20, fill="both", expand=True)

        # Заголовок
        self.label = ctk.CTkLabel(self.frame, text="Главная страница", font=("Arial", 30))
        self.label.pack(pady=40)

        # Кнопка "Обучение"
        self.learn_button = ctk.CTkButton(self.frame, text="Обучение", font=("Arial", 20), command=self.open_learning_page, height=75,  width=300)
        self.learn_button.pack(pady=20)

        # Кнопка "Тестирование"
        self.test_button = ctk.CTkButton(self.frame, text="Тестирование", font=("Arial", 20), command=self.open_testing_page, height=75,  width=300)
        self.test_button.pack(pady=20)

        # # Кнопка "Сгенерировать упражнение"
        # self.generate_button = ctk.CTkButton(self.frame, text="Сгенерировать упражнение", font=("Arial", 20), command=self.open_generate_page, height=75,  width=300)
        # self.generate_button.pack(pady=20)

        # Кнопка "Мой словарь"
        self.dictionary_button = ctk.CTkButton(self.frame, text="Мой словарь", font=("Arial", 20), command=self.open_dictionary_page, height=75,  width=300)
        self.dictionary_button.pack(pady=20)

        # Кнопка "Моя успеваемость"
        self.performance_button = ctk.CTkButton(self.frame, text="Статистика", font=("Arial", 20), command=self.open_performance_page, height=75,  width=300)
        self.performance_button.pack(pady=20)

        # Иконка профиля в правом верхнем углу
        self.create_profile_icon()

    def create_profile_icon(self):
        # Берём первые две буквы из username
        initials = self.username[:2].upper()
        self.profile_button = ctk.CTkButton(
            self.root,
            text=initials,
            width=40,
            height=40,
            corner_radius=20,
            fg_color="#DAA520",
            font=("Arial", 15),
            command=self.open_profile_page
        )
        # Размещаем иконку в правом верхнем углу
        self.profile_button.place(relx=0.95, rely=0.05, anchor="ne")

    # Обработчики кнопок (пока заглушки)
    def open_learning_page(self):
        x_coordinate = self.root.winfo_x()
        y_coordinate = self.root.winfo_y() # Получаем текущее положение главного окна
        self.root.quit()  # Завершаем цикл mainloop() главного окна
        self.root.destroy()  # Закрываем главное окно
        learning_window = ctk.CTk()
        learning_window.title("Изучение текстов")
        learning_window.geometry(f"1100x800+{x_coordinate}+{y_coordinate}")
        LearningPage(learning_window, self.username, self.db_manager)
        # LearningPage(learning_window, self.username, self.db)
        learning_window.mainloop()  # Запускаем цикл mainloop() для нового окна

    def open_testing_page(self):
        x_coordinate = self.root.winfo_x()
        y_coordinate = self.root.winfo_y()  # Получаем текущее положение главного окна
        self.root.quit()  # Завершаем цикл mainloop() главного окна
        self.root.destroy()  # Закрываем главное окно
        testing_window = ctk.CTk()
        testing_window.title("Тестирование")
        testing_window.geometry(f"1100x800+{x_coordinate}+{y_coordinate}")
        TestingPage(testing_window, self.username, self.db_manager)
        # LearningPage(learning_window, self.username, self.db)
        testing_window.mainloop()  # Запускаем цикл mainloop() для нового окна

    # def open_generate_page(self):
    #     messagebox.showinfo("Сгенерировать упражнение", "Переход к генерации упражнения.")

    def open_dictionary_page(self):
        x_coordinate = self.root.winfo_x()
        y_coordinate = self.root.winfo_y()  # Получаем текущее положение окна
        self.root.quit()  # Завершаем цикл mainloop()
        self.root.destroy()  # Закрываем окно
        dictionary_window = ctk.CTk()
        dictionary_window.title("Избранное")
        dictionary_window.geometry(f"800x800+{x_coordinate}+{y_coordinate}")
        DictionaryPage(dictionary_window, self.username, self.db_manager)
        dictionary_window.mainloop()  # Запускаем цикл mainloop() для нового окна

    def open_performance_page(self):
        x_coordinate = self.root.winfo_x()
        y_coordinate = self.root.winfo_y()  # Получаем текущее положение окна
        self.root.quit()  # Завершаем цикл mainloop()
        self.root.destroy()  # Закрываем окно
        Perfomance_window = ctk.CTk()
        Perfomance_window.title("Статистика решений")
        Perfomance_window.geometry(f"800x800+{x_coordinate}+{y_coordinate}")
        PerfomancePage(Perfomance_window, self.username, self.db_manager)
        Perfomance_window.mainloop()  # Запускаем цикл mainloop() для нового окна

    def open_profile_page(self):
        x_coordinate = self.root.winfo_x()
        y_coordinate = self.root.winfo_y()  # Получаем текущее положение окна
        self.root.quit()  # Завершаем цикл mainloop()
        self.root.destroy()  # Закрываем окно
        Profile_window = ctk.CTk()
        Profile_window.title("Профиль")
        Profile_window.geometry(f"800x550+{x_coordinate}+{y_coordinate}")
        ProfilePage(Profile_window, self.username, self.db_manager)
        Profile_window.mainloop()  # Запускаем цикл mainloop() для нового окна


    def on_close(self):
        """Закрываем подключение к базе данных при выходе."""
        self.db_manager.close()
        self.root.destroy()

# Тестовый запуск
# if __name__ == "__main__":
#     root = ctk.CTk()
#     app = MainPage(root, "DemoUser")
#     root.mainloop()
