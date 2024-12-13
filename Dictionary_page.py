import customtkinter as ctk
from tkinter import messagebox


class DictionaryPage:
    def __init__(self, root, username, db_manager):
        self.root = root
        self.username = username
        self.db_manager = db_manager

        # Настраиваем окно
        window_width = 800
        window_height = 800
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

        # Заголовок
        self.title_label = ctk.CTkLabel(self.frame, text="Мои слова", font=("Arial", 30))
        self.title_label.pack(pady=10)

        # Создаём прокручиваемую таблицу
        self.table_frame = ctk.CTkScrollableFrame(self.frame, width=760, height=600)
        self.table_frame.pack(fill="both", expand=True, padx=10, pady=10)

        self.create_table_headers()
        self.load_favorites()

    def create_table_headers(self):
        """Создаём заголовки таблицы."""
        headers = ["Английское слово", "Перевод", "Действие"]
        for col, text in enumerate(headers):
            header = ctk.CTkLabel(self.table_frame, text=text, font=("Arial", 16), anchor="center")
            header.grid(row=0, column=col, padx=1, pady=1, sticky="nsew")

        # Растягиваем столбцы по ширине
        for col in range(len(headers)):
            self.table_frame.grid_columnconfigure(col, weight=1)

    def load_favorites(self):
        """Загружаем избранные слова пользователя."""
        user_query = "SELECT id FROM User WHERE username = ?"
        user = self.db_manager.fetch_one(user_query, (self.username,))
        if not user:
            messagebox.showerror("Ошибка", "Пользователь не найден.")
            return
        user_id = user[0]

        query = """
            SELECT Word.id, Word.engword, Word.translation
            FROM Favorites
            JOIN Word ON Favorites.word_id = Word.id
            WHERE Favorites.user_id = ?
        """
        favorites = self.db_manager.fetch_all(query, (user_id,))

        # Очистка таблицы перед загрузкой
        for widget in self.table_frame.winfo_children():
            widget.destroy()

        # Добавление строк в таблицу
        for row, (word_id, engword, translation) in enumerate(favorites, start=1):
            # Создание ячеек с границами
            for col, text in enumerate([engword, translation]):
                cell_frame = ctk.CTkFrame(self.table_frame, border_width=1, corner_radius=0)
                cell_frame.grid(row=row, column=col, sticky="nsew", padx=1, pady=1)
                label = ctk.CTkLabel(cell_frame, text=text, font=("Arial", 14))
                label.pack(fill="both", expand=True)

            # Кнопка удаления с границами
            button_frame = ctk.CTkFrame(self.table_frame, border_width=1, corner_radius=0)
            button_frame.grid(row=row, column=2, sticky="nsew", padx=1, pady=1)
            delete_button = ctk.CTkButton(
                button_frame, text="Удалить", font=("Arial", 12),
                command=lambda wid=word_id: self.delete_favorite(wid, row)
            )
            delete_button.pack(fill="both", expand=True)

        # Растягиваем столбцы по ширине
        for col in range(3):
            self.table_frame.grid_columnconfigure(col, weight=1)

    def delete_favorite(self, word_id, row):
        """Удаляет слово из избранного."""
        user_query = "SELECT id FROM User WHERE username = ?"
        user = self.db_manager.fetch_one(user_query, (self.username,))
        if not user:
            return
        user_id = user[0]

        delete_query = "DELETE FROM Favorites WHERE user_id = ? AND word_id = ?"
        self.db_manager.execute(delete_query, (user_id, word_id))

        self.show_in_app_notification(f"Слово удалено из избранного.")
        self.load_favorites()

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

    def show_in_app_notification(self, message):
        """Отображаем уведомление внутри приложения."""
        # Создаём метку для уведомления
        notification_label = ctk.CTkLabel(
            self.frame,
            text=message,
            fg_color="#8B4513",
            text_color="#B8860B",
            corner_radius=10,
            font=("Arial", 14, "bold")
        )
        # Размещаем метку в верхней части окна
        notification_label.place(relx=0.5, rely=0.05, anchor="center")

        # Используем метод after() для автоматического скрытия уведомления через 2 секунды
        self.root.after(2000, notification_label.destroy)
