import customtkinter as ctk
import matplotlib
from tkinter import messagebox
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


class PerfomancePage:
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
        self.title_label = ctk.CTkLabel(self.frame, text="Статистика", font=("Arial", 30))
        self.title_label.pack(pady=10)

        # Фрейм для горизонтальной таблицы
        self.stats_frame = ctk.CTkFrame(self.frame)
        self.stats_frame.pack(pady=20, padx=20, fill="both", expand=True)

        # Загружаем статистику
        self.load_statistics()

    def load_statistics(self):
        """Загружает статистику и отображает её в таблице."""
        # Инициализируем статистику
        stats = {
            "Всего текстов пройдено": "-",
            "Процент прохождения текстов": "-",
            "Избранных слов добавлено": "-",
            "Пройдено упражнений": "-",
            "Правильность": "-",
            "Текстов закреплено": "-"
        }

        try:
            # Получаем ID пользователя
            user_query = "SELECT id, exercise_cnt, correct_exercise_cnt, daily_text FROM User WHERE username = ?"
            user = self.db_manager.fetch_one(user_query, (self.username,))
            if not user:
                messagebox.showerror("Ошибка", "Пользователь не найден.")
                return

            user_id, exercise_cnt, correct_exercise_cnt, daily_text = user

            # Всего текстов пройдено
            stats_query = "SELECT COUNT(*) FROM UserTexts WHERE user_id = ?"
            stats["Всего текстов пройдено"] = self.db_manager.fetch_one(stats_query, (user_id,))[0]

            # Процент прохождения текстов
            total_texts_query = "SELECT COUNT(*) FROM Text"
            total_texts = self.db_manager.fetch_one(total_texts_query)[0]
            stats["Процент прохождения текстов"] = (
                f"{(stats['Всего текстов пройдено'] / total_texts * 100):.2f}%" if total_texts > 0 else "-"
            )

            # Избранных слов добавлено
            favorites_query = "SELECT COUNT(*) FROM Favorites WHERE user_id = ?"
            stats["Избранных слов добавлено"] = self.db_manager.fetch_one(favorites_query, (user_id,))[0]

            # Пройдено упражнений
            stats["Пройдено упражнений"] = exercise_cnt or "-"

            # Правильность
            stats["Правильность"] = (
                f"{(correct_exercise_cnt / exercise_cnt * 100):.2f}%" if exercise_cnt > 0 else "-"
            )

            # Текстов закреплено
            secured_texts_query = "SELECT COUNT(*) FROM UserTexts WHERE user_id = ? AND exercise = 1"
            stats["Текстов закреплено"] = self.db_manager.fetch_one(secured_texts_query, (user_id,))[0]

            # Инфографик
            self.create_chart(daily_text)
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить статистику: {e}")
            return

        # Создаём таблицу
        for idx, (label, value) in enumerate(stats.items()):
            stat_label = ctk.CTkLabel(self.stats_frame, text=label, font=("Arial", 20), anchor="w")
            stat_label.grid(row=idx, column=0, padx=10, pady=5, sticky="w")
            stat_value = ctk.CTkLabel(self.stats_frame, text=value, font=("Arial", 20), anchor="e")
            stat_value.grid(row=idx, column=1, padx=10, pady=5, sticky="e")

    def create_chart(self, daily_text):
        """Создаёт график на основе истории решений."""
        if not daily_text:
            return

        # Преобразуем строку в массив данных
        try:
            data = [int(x) for x in daily_text if x in "01"]
        except ValueError:
            data = []

        if not data:
            return

        correct = data.count(1)
        incorrect = data.count(0)

        # Построение графика
        figure = Figure(figsize=(6, 3), dpi=150, facecolor='#3F2F25')
        ax = figure.add_subplot(111)
        ax.pie(
            [correct, incorrect],
            labels=["Верные", "Неверные"],
            autopct="%1.1f%%",
            colors=["#6B8E23", "#A52A2A"],
            startangle=90,
            textprops={"color": "#FFF0F5"}
        )
        ax.set_title("Решения", color="#FFF0F5")

        # Встраиваем график в окно
        chart_canvas = FigureCanvasTkAgg(figure, self.frame)
        chart_canvas.get_tk_widget().pack(pady=20)

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
