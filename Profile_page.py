import customtkinter as ctk
from tkinter import messagebox


class ProfilePage:
    def __init__(self, root, username, db_manager):
        self.root = root
        self.username = username
        self.db_manager = db_manager

        # Настраиваем окно
        window_width = 800
        window_height = 550
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        # self.root.geometry(f"{window_width}x{window_height}+"
        #                    f"{(screen_width - window_width) // 2}+"
        #                    f"{(screen_height - window_height) // 2}")
        self.root.resizable(False, False)

        # Создаём фрейм
        self.frame = ctk.CTkFrame(self.root)
        self.frame.pack(padx=20, pady=20, fill="both", expand=True)

        # Кнопка "Назад" для возврата на главную страницу
        self.back_button = ctk.CTkButton(self.frame, text="🠔", font=("Arial", 35), width=6, command=self.go_back)
        self.back_button.pack(padx=20, pady=20, anchor="nw")

        # Заголовок с именем пользователя
        self.title_label = ctk.CTkLabel(self.frame, text=f"{self.username}", font=("Impact", 40))
        self.title_label.pack(pady=20)

        # Поле "Имя пользователя"
        self.username_label = ctk.CTkLabel(self.frame, text="Имя пользователя:", font=("Arial", 20))
        self.username_label.pack(anchor="w", padx=20, pady=(10, 0))
        self.username_value = ctk.CTkLabel(self.frame, text=self.username, font=("Arial", 18))
        self.username_value.pack(anchor="w", padx=20)

        # Получаем реальный пароль из базы данных
        password = self.get_user_password()

        # Поле "Пароль"
        self.password_label = ctk.CTkLabel(self.frame, text="Пароль:", font=("Arial", 20))
        self.password_label.pack(anchor="w", padx=20, pady=(10, 0))
        self.password_value = ctk.CTkLabel(self.frame, text=password, font=("Arial", 18))
        self.password_value.pack(anchor="w", padx=20)

        # Кнопки "Статистика" и "Очистить статистику"
        self.buttons_frame = ctk.CTkFrame(self.frame, fg_color = "#3F2F25")
        self.buttons_frame.pack(pady=30)

        self.stats_button = ctk.CTkButton(self.buttons_frame, text="Статистика", font=("Arial", 16),
                                          command=self.open_statistics)
        self.stats_button.grid(row=0, column=0, padx=10)

        self.clear_stats_button = ctk.CTkButton(self.buttons_frame, text="Очистить статистику", font=("Arial", 16),
                                                command=self.clear_statistics)
        self.clear_stats_button.grid(row=0, column=1, padx=10)

        # Кнопка "Выйти"
        self.delete_account_button = ctk.CTkButton(self.frame, text="Выйти из аккаунта", font=("Arial", 20),
                                                   command=self.return_to_auth)
        self.delete_account_button.pack(pady=3, fill="x", padx=20)

        # Кнопка "Удалить аккаунт"
        self.delete_account_button = ctk.CTkButton(self.frame, text="Удалить аккаунт", font=("Arial", 20),
                                                   fg_color="red",
                                                   command=self.delete_account)
        self.delete_account_button.pack(pady=3, fill="x", padx=20)

    def open_statistics(self):
        """Открытие страницы статистики."""
        self.root.quit()
        self.root.destroy()
        from Perfomance_page import PerfomancePage
        stats_window = ctk.CTk()
        stats_window.title("Статистика")
        PerfomancePage(stats_window, self.username, self.db_manager)
        stats_window.mainloop()

    def clear_statistics(self):
        """Очистка статистики пользователя."""
        confirm = messagebox.askyesno("Подтверждение", "Вы уверены, что хотите очистить статистику?")
        if confirm:
            user_id = self.get_user_id()
            if user_id:
                # Удаляем историю пользователя
                self.db_manager.execute("DELETE FROM UserTexts WHERE user_id = ?", (user_id,))
                self.db_manager.execute("DELETE FROM Favorites WHERE user_id = ?", (user_id,))
                self.db_manager.execute("UPDATE User SET exercise_cnt = 0, correct_exercise_cnt = 0, daily_text = NULL WHERE id = ?",
                                        (user_id,))
                messagebox.showinfo("Успешно", "Статистика очищена.")

    def delete_account(self):
        """Удаление аккаунта пользователя."""
        confirm = messagebox.askyesno("Подтверждение", "Вы уверены, что хотите удалить аккаунт? Это действие необратимо!")
        if confirm:
            user_id = self.get_user_id()
            if user_id:
                self.db_manager.execute("DELETE FROM User WHERE id = ?", (user_id,))
                messagebox.showinfo("Успешно", "Аккаунт удалён.")
                self.return_to_auth()

    def return_to_auth(self):
        """Возвращаем пользователя на страницу авторизации."""
        self.root.quit()
        self.root.destroy()
        from auth import AuthWindow
        auth_window = ctk.CTk()
        auth_window.title("Авторизация")
        AuthWindow(auth_window)
        auth_window.mainloop()

    def get_user_id(self):
        """Получение ID текущего пользователя."""
        user = self.db_manager.fetch_one("SELECT id FROM User WHERE username = ?", (self.username,))
        return user[0] if user else None

    def get_user_password(self):
        """Получение пароля текущего пользователя из базы данных."""
        user = self.db_manager.fetch_one("SELECT password FROM User WHERE username = ?", (self.username,))
        return user[0] if user else ""

    def go_back(self):
        """Возвращаемся на главную страницу."""
        x_coordinate = self.root.winfo_x()
        y_coordinate = self.root.winfo_y()
        self.root.quit()
        self.root.destroy()
        from main_window import MainWindow
        main_window = ctk.CTk()
        main_window.title("Главное меню")
        main_window.geometry(f"800x800+{x_coordinate}+{y_coordinate}")
        MainWindow(main_window, self.username)
        main_window.mainloop()