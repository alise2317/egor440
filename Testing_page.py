import customtkinter as ctk
import random
import re
from tkinter import Text, messagebox


class TestingPage:
    def __init__(self, root, username, db_manager):
        self.root = root
        self.username = username
        self.db_manager = db_manager
        self.current_text_id = None
        self.words_to_insert = []
        self.selected_text = ""
        self.selected_word_positions = []
        self.user_answers = {}
        self.current_word = None  # Текущее выбранное слово
        self.current_button = None  # Текущая активная кнопка

        # Настраиваем окно
        window_width = 1100
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

        # Кнопка "Назад"
        self.back_button = ctk.CTkButton(self.frame, text="🠔", font=("Arial", 35), width=6, command=self.go_back)
        self.back_button.pack(padx=20, pady=2, anchor="nw")

        # Элементы интерфейса
        self.text_display = Text(self.frame, wrap="word", font=("Arial", 15), bg="#3F2F25", fg="#FAEBD7")
        self.text_display.pack(pady=10, padx=1, fill="both", expand=True)
        self.text_display.bind("<Button-1>", self.handle_space_click)
        self.text_display.config(state="disabled")  # Делаем текст не редактируемым

        # Фрейм со словами
        self.words_frame = ctk.CTkFrame(self.frame, height=50, fg_color = "#3F2F25")
        self.words_frame.pack(pady=5, fill="x")

        self.check_button = ctk.CTkButton(self.frame, text="Проверить", height=40, width=200, command=self.check_answers)
        self.check_button.pack(side="left", padx=10, pady=1)

        self.reset_button = ctk.CTkButton(self.frame, text="Сброс", height=40, width=200, command=self.reset_text)
        self.reset_button.pack(side="left", padx=10, pady=1)

        self.next_button = ctk.CTkButton(self.frame, text="Далее", height=40, width=200, command=self.load_next_text)
        self.next_button.pack(side="right", padx=10, pady=1)

        # Загрузка первого текста
        self.load_text()

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

    def load_text(self):
        """Загружаем случайный текст с exercise=0."""
        query = """
        SELECT ut.text_id, t.content 
        FROM UserTexts ut
        JOIN Text t ON ut.text_id = t.id
        WHERE ut.user_id = (SELECT id FROM User WHERE username = ?)
          AND ut.exercise = 0
        ORDER BY RANDOM()
        LIMIT 1;
        """
        result = self.db_manager.fetch_one(query, (self.username,))
        if not result:
            messagebox.showinfo("Информация", "Нет доступных текстов для упражнений.")
            self.go_back()
            return

        self.current_text_id, self.selected_text = result
        self.load_terms()
        self.process_text()

    def load_terms(self):
        """Загружаем термины из таблицы Term."""
        query = "SELECT termword FROM Term;"
        terms = self.db_manager.fetch_all(query)
        if terms:
            # Оставляем только одиночные слова
            term_words = [term[0] for term in terms if re.match(r"^\w+$", term[0])]
            self.terms_to_use = term_words
        else:
            self.terms_to_use = []

    def process_text(self):
        """Обрабатываем текст, выделяя до 10 уникальных терминов."""
        words_in_text = re.findall(r'\b\w+\b', self.selected_text)
        terms_in_text = [term for term in self.terms_to_use if term in words_in_text]

        # Исключаем повторное выделение слов
        terms_in_text = list(set(terms_in_text))

        # Ограничиваем количество терминов до 10
        if len(terms_in_text) > 10:
            terms_in_text = random.sample(terms_in_text, 10)

        # Инициализируем список initial_words_to_insert, даже если он пуст
        if not hasattr(self, "initial_words_to_insert"):
            self.initial_words_to_insert = terms_in_text[:]  # Сохраняем исходный список терминов для сброса

        # Сохраняем изначальное количество слов
        self.initial_words_count = len(terms_in_text)

        self.words_to_insert = terms_in_text  # Список терминов для вставки

        # Подготовка списка регулярных выражений
        self.contextual_regexes = []
        for word in self.words_to_insert:
            start_index = self.selected_text.find(word)
            if start_index != -1:
                before = self.selected_text[max(0, start_index - 3):start_index]
                after = self.selected_text[start_index + len(word):start_index + len(word) + 3]
                regex = rf"(?<={re.escape(before)})\w+(?={re.escape(after)})"
                self.contextual_regexes.append((regex, word))

        # Подготовка текста с пропусками
        self.selected_word_positions = []
        text_to_display = self.selected_text

        for word in self.words_to_insert:
            start_index = text_to_display.find(word)
            if start_index != -1:
                end_index = start_index + len(word)
                self.selected_word_positions.append((start_index, end_index))
                text_to_display = text_to_display[:start_index] + "___" + text_to_display[end_index:]

        self.cleared_text = text_to_display  # Сохраняем текст с пробелами
        self.update_text_display(text_to_display)
        self.update_words_list()

    def update_text_display(self, text):
        """Обновляем текстовое поле с пробелами."""
        self.text_display.config(state="normal")
        self.text_display.delete("1.0", "end")
        self.text_display.insert("1.0", text)
        self.text_display.config(state="disabled")

    def update_words_list(self):
        """Обновляем список доступных слов, размещая их в два ряда."""
        for widget in self.words_frame.winfo_children():
            widget.destroy()

        row1_frame = ctk.CTkFrame(self.words_frame, height=20, fg_color = "#3F2F25")
        row1_frame.pack(side="top", fill="x", pady=3)

        row2_frame = ctk.CTkFrame(self.words_frame, height=20, fg_color = "#3F2F25")
        row2_frame.pack(side="top", fill="x", pady=3)

        for i, word in enumerate(self.words_to_insert):
            # Создаём кнопку
            word_button = ctk.CTkButton(
                row1_frame if i < 5 else row2_frame,
                text=word,
                fg_color="#B8860B"
            )
            # Настраиваем её команду после создания
            word_button.configure(command=lambda w=word, b=word_button: self.select_word(w, b))
            word_button.pack(side="left", padx=5)

    def select_word(self, word, button):
        """Обрабатываем выбор слова для вставки."""
        if self.current_button:
            self.current_button.configure(fg_color='#B8860B')  # Снимаем подсветку с предыдущей кнопки

        if self.current_word == word:  # Отменяем выбор текущего слова
            self.current_word = None
            self.current_button = None
        else:
            self.current_word = word
            self.current_button = button
            self.current_button.configure(fg_color="#808000")  # Подсвечиваем новую кнопку

    def handle_space_click(self, event):
        """Обрабатываем нажатие на текст по месту клика."""
        if self.current_word is None:
            # messagebox.showinfo("Ошибка", "Сначала выберите слово.")
            return

        # Определяем индекс позиции, куда кликнул пользователь
        index = self.text_display.index(f"@{event.x},{event.y}")
        line, char = map(int, index.split("."))  # Получаем строку и символ

        self.text_display.config(state="normal")  # Делаем поле редактируемым
        current_line = self.text_display.get(f"{line}.0", f"{line}.end")  # Получаем строку текста

        # Проверяем, находится ли под курсором "___"
        if current_line[char:char + 3] == "___":
            self.text_display.delete(f"{line}.{char}", f"{line}.{char + 3}")  # Удаляем "___"
            self.text_display.insert(f"{line}.{char}", self.current_word)  # Вставляем слово
            self.words_to_insert.remove(self.current_word)  # Убираем из списка
            self.update_words_list()  # Обновляем список слов
            self.current_word = None  # Сбрасываем текущее слово
            self.current_button = None
        # else:
        #     messagebox.showinfo("Ошибка", "Выберите место с '___'.")  # Если клик не по "___"

        self.text_display.config(state="disabled")  # Блокируем редактировани

    def reset_text(self):
        """Сбрасываем текст и восстанавливаем начальный список слов."""
        self.words_to_insert = self.initial_words_to_insert[:]  # Восстанавливаем изначальный набор слов
        self.current_word = None  # Сбрасываем текущее выбранное слово
        self.current_button = None  # Сбрасываем текущую кнопку
        self.update_text_display(self.cleared_text)  # Сбрасываем текстовое поле
        self.update_words_list()  # Обновляем список кнопок

    def check_answers(self):
        """Проверяем правильность вставленных слов."""
        text_content = self.text_display.get("1.0", "end-1c")  # Получаем текущий текст

        if "___" in text_content:
            self.show_notification("Заполните все пропуски!")
            return

        self.text_display.config(state="normal")  # Разрешаем редактирование текста
        correct_count = 0
        total_count = len(self.words_to_insert)
        result_sequence = []  # Для хранения результатов проверки

        # Итерируемся по каждому из пропусков
        for regex, correct_word in self.contextual_regexes:
            match = re.search(regex, text_content)
            if not match:
                result_sequence.append("0")
                continue

            start, end = match.start(), match.end()
            inserted_word = text_content[start:end].strip()

            # Проверка корректности
            if inserted_word == correct_word:
                self.text_display.tag_add("correct", f"1.0+{start}c", f"1.0+{end}c")
                correct_count += 1
                result_sequence.append("1")
            else:
                self.text_display.tag_add("incorrect", f"1.0+{start}c", f"1.0+{end}c")
                result_sequence.append("0")

        # Настраиваем стили
        self.text_display.tag_config("correct", foreground="green")
        self.text_display.tag_config("incorrect", foreground="red")
        self.text_display.config(state="disabled")  # Блокируем редактирование текста

        # Сохраняем статистику
        self.update_statistics(correct_count, total_count, "".join(result_sequence))

        # Удаляем ненужные кнопки
        self.check_button.pack_forget()
        self.reset_button.pack_forget()

    def update_statistics(self, correct_count, total_count, result_sequence):
        """Обновляем статистику пользователя и состояние текста."""
        # Обновляем статистику текста в таблице UserTexts
        if correct_count == total_count:
            query = "UPDATE UserTexts SET exercise = 1 WHERE text_id = ?"
            self.db_manager.execute_query(query, (self.current_text_id,))

        # Обновляем статистику пользователя
        query = """
        UPDATE User
        SET exercise_cnt = exercise_cnt + ?,
            correct_exercise_cnt = correct_exercise_cnt + ?,
            daily_text = COALESCE(daily_text, '') || ?
        WHERE username = ?
        """
        self.db_manager.execute_query(query, (total_count, correct_count, result_sequence, self.username))

    def show_notification(self, message):
        """Показываем уведомление в верхней части экрана."""
        notification_label = ctk.CTkLabel(self.frame, text=message, fg_color="#8B4513",text_color="#B8860B", corner_radius=10, font=("Arial", 14))
        notification_label.place(relx=0.5, rely=0.05, anchor="center")

        # Убираем уведомление через 3 секунды
        self.frame.after(2000, notification_label.destroy)

    def load_next_text(self):
        """Загружаем следующий случайный текст."""
        self.load_text()