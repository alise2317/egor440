import customtkinter as ctk
from tkinter import messagebox
from tkinter import messagebox, Text, Scrollbar
import re
import requests  # Импортируем модуль для выполнения HTTP-запросов

import nltk
# nltk.download('punkt')
# nltk.download('wordnet')
# nltk.download('omw-1.4')
from nltk.stem import WordNetLemmatizer

class LearningPage:
    def __init__(self, root, username, db_manager):
        self.root = root
        self.username = username
        self.db_manager = db_manager

        # Настраиваем окно
        window_width = 1100
        window_height = 800
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        # x_coordinate = (screen_width // 2) - (window_width // 2)
        # y_coordinate = (screen_height // 2) - (window_height // 2)
        # self.root.geometry(f"{window_width}x{window_height}+{x_coordinate}+{y_coordinate}")
        self.root.resizable(False, False)

        # Загружаем термины из базы данных
        self.terms = self.load_terms()

        # Создаём переменную для всплывающей подсказки
        self.tooltip = None

        # Инициализируем лемматизатор
        self.lemmatizer = WordNetLemmatizer()

        # Создаём фрейм
        self.frame = ctk.CTkFrame(self.root)
        self.frame.pack(padx=20, pady=20, fill="both", expand=True)

        # Кнопка "Назад" для возврата на главную страницу
        self.back_button = ctk.CTkButton(self.frame, text="🠔", font=("Arial", 35), width=6, command=self.go_back)
        self.back_button.pack(padx=20, pady=20, anchor="nw")

        # Поле для отображения названия текста
        self.text_name_label = ctk.CTkLabel(self.frame, text="", font=("Arial", 26, "bold"))
        self.text_name_label.pack(pady=1)

        # Создаём текстовое поле и скроллбар
        self.text_box = Text(self.frame, wrap="word", font=("Arial", 17), bg="#3F2F25",fg="#FAEBD7", bd=0, height=20)
        self.text_box.pack(pady=10, fill="both", expand=True)

        self.text_scrollbar = ctk.CTkScrollbar(self.frame,button_color="#3F2F25", command=self.text_box.yview)
        self.text_scrollbar.pack(side="right", fill="y")
        self.text_box.config(yscrollcommand=self.text_scrollbar.set)

        # Отключаем редактирование текста
        self.text_box.configure(state="disabled")


        # Создаем подфрейм для кнопок и центрируем его в основном фрейме
        button_frame = ctk.CTkFrame(self.frame, fg_color = "#3F2F25")
        button_frame.pack(pady=10)  # Центрируем button_frame внутри self.frame

        # Кнопка "Пройдено"
        self.completed_button = ctk.CTkButton(button_frame, text="Пройдено ✔", font=("Arial", 15), height=40, width=200, command=self.mark_as_completed)
        self.completed_button.pack(side="left", padx=10)

        # Кнопка "Пропустить"
        self.skip_button = ctk.CTkButton(button_frame, text="Пропустить 🠖", font=("Arial", 15), height=40, width=200, command=self.load_next_text)
        self.skip_button.pack(side="left", padx=10)

        # Загружаем первый текст
        self.load_next_text()

    def go_back(self):
        """Возвращаемся на главную страницу."""
        x_coordinate = self.root.winfo_x()
        y_coordinate = self.root.winfo_y() # Получаем текущее положение главного окна
        self.root.quit()  # Завершаем цикл mainloop() окна обучения
        self.root.destroy()  # Закрываем окно обучения
        from main_window import MainWindow  # Импортируем здесь, чтобы избежать циклического импорта
        main_window = ctk.CTk()
        main_window.title("Главное меню")
        main_window.geometry(f"800x800+{x_coordinate}+{y_coordinate}")
        MainWindow(main_window, self.username)
        main_window.mainloop()  # Запускаем цикл mainloop() для главного окна

    def mark_as_completed(self):
        """Отмечаем текст как пройденный и загружаем следующий."""
        try:
            query = """
            INSERT INTO UserTexts (user_id, text_id)
            VALUES (?, ?);
            """
            user_id = self.get_user_id()
            self.db_manager.cursor.execute(query, (user_id, self.current_text_id))
            self.db_manager.conn.commit()
            self.load_next_text()
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось обновить данные: {e}")

    def get_user_id(self):
        """Получаем ID текущего пользователя из базы данных."""
        user_data = self.db_manager.fetch_one(
            "SELECT id FROM User WHERE username = ?", (self.username,)
        )
        return user_data[0] if user_data else None

    def load_terms(self):
        """Загружаем все термины из таблицы Term."""
        try:
            query = "SELECT termword FROM Term;"
            terms = [row[0] for row in self.db_manager.cursor.execute(query).fetchall()]
            # Сортируем термины по длине (от длинных к коротким), чтобы сначала искать словосочетания
            terms.sort(key=len, reverse=True)
            return terms
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить термины: {e}")
            return []

    def load_next_text(self):
        """Загружаем случайный текст и выделяем термины."""
        try:
            query = """
            SELECT id, name, content
            FROM Text
            WHERE id NOT IN (SELECT text_id FROM UserTexts WHERE user_id = ?)
            ORDER BY RANDOM() LIMIT 1;
            """
            user_id = self.get_user_id()
            if user_id is None:
                raise ValueError("Не удалось получить ID пользователя.")
            result = self.db_manager.cursor.execute(query, (user_id,)).fetchone()

            if result:
                self.current_text_id, self.text_name, self.text_content = result
                self.text_name_label.configure(text=self.text_name)
                self.display_text_with_highlighting()
            else:
                self.text_name_label.configure(text="Тексты закончились.")
                self.text_box.delete("1.0", "end")
                self.text_box.insert("1.0", "Тексты закончились.")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить текст: {e}")

    def lemmatize_word(self, word):
        """Приводим слово к базовой форме (лемматизируем)."""
        return self.lemmatizer.lemmatize(word.lower())

    def display_text_with_highlighting(self):
        """Отображаем текст и выделяем термины, но выделяем оригинальные слова из текста."""
        self.text_box.configure(state="normal")
        self.text_box.delete("1.0", "end")
        self.text_box.insert("1.0", self.text_content)

        # Обычный поиск терминов без лемматизации
        for term in self.terms:
            pattern = r'\b' + re.escape(term) + r'\b'
            matches = list(re.finditer(pattern, self.text_content, re.IGNORECASE))

            for match in matches:
                start_index = f"1.0 + {match.start()}c"
                end_index = f"1.0 + {match.end()}c"
                tag_name = f"term_{term}"
                self.text_box.tag_add(tag_name, start_index, end_index)
                self.text_box.tag_config(tag_name, foreground="#708090", underline=True)
                self.text_box.tag_bind(tag_name, "<Enter>", lambda event, term=term: self.on_word_hover(event, term))
                self.text_box.tag_bind(tag_name, "<Leave>", self.on_word_leave)
                self.text_box.tag_bind(tag_name, "<Button-1>", self.on_word_click)

        # Лемматизация слов из текста и сопоставление с исходными терминами
        terms_lower = set(term.lower() for term in self.terms)
        words = re.findall(r'\b\w+\b', self.text_content)  # Получаем список всех целых слов
        for word in words:
            lemmatized_word = self.lemmatize_word(word)
            for term in self.terms:
                # Если лемматизированное слово совпадает с термином, выделяем оригинальное слово
                if lemmatized_word.lower() == term.lower() and word.lower() != term.lower() and word.lower() not in terms_lower:
                    # Находим индекс целого слова (не части слова)
                    pattern = r'\b' + re.escape(word) + r'\b'
                    match = re.search(pattern, self.text_content, re.IGNORECASE)
                    if match:
                        start_index = f"1.0 + {match.start()}c"
                        end_index = f"1.0 + {match.end()}c"
                        tag_name = f"term_lemma_{lemmatized_word}"
                        self.text_box.tag_add(tag_name, start_index, end_index)
                        self.text_box.tag_config(tag_name, foreground="#708090", underline=True)
                        self.text_box.tag_bind(tag_name, "<Enter>",lambda event, term=word: self.on_word_hover(event, term))
                        self.text_box.tag_bind(tag_name, "<Leave>", self.on_word_leave)
                        self.text_box.tag_bind(tag_name, "<Button-1>", self.on_word_click)

        self.text_box.configure(state="disabled")

    def get_translation(self, word):
        """
            Переводит слово с помощью Yandex.Translate API.
            Аутентификация осуществляется через API-ключ.
            """
        # Вставьте ваши данные ниже
        API_KEY = "AQVN2TUgLk6tgZnl226osrv4aB460GgrhZZU_tSX"  # Укажите ваш API-ключ Yandex Translate
        # FOLDER_ID = "<ИДЕНТИФИКАТОР_КАТАЛОГА>"  # Укажите идентификатор вашего каталога - не указывается в сервисном аккаунте
        TARGET_LANGUAGE = "ru"  # Язык перевода (измените при необходимости)

        # URL Yandex Translate API
        url = "https://translate.api.cloud.yandex.net/translate/v2/translate"

        # Заголовки запроса с использованием API-ключа
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Api-Key {API_KEY}"
        }

        # Тело запроса с текстом для перевода
        body = {
            "targetLanguageCode": TARGET_LANGUAGE,
            "texts": [word],
            # "folderId": FOLDER_ID
        }

        try:
            # Выполняем запрос к Yandex Translate API
            response = requests.post(url, json=body, headers=headers)

            # Проверяем статус ответа
            if response.status_code == 200:
                data = response.json()
                # Извлекаем переведенный текст
                translation = data['translations'][0]['text']
                return translation
            else:
                return f"Ошибка перевода: {response.status_code} - {response.text}"

        except Exception as e:
            return f"Не удалось получить перевод: {e}"

    def on_word_hover(self, event, term):
        """Обработчик события при наведении на словосочетание."""
        translation = self.get_translation(term)

        # Создаём всплывающую подсказку
        self.show_tooltip(event, translation)

    def on_word_leave(self, event):
        """Обработчик события при уходе курсора с выделенного слова."""
        self.hide_tooltip()

    def show_tooltip(self, event, translation):
        """Отображаем всплывающую подсказку с переводом над выделенным словом."""
        # Создаём метку для подсказки, если она ещё не создана
        if not hasattr(self, "tooltip") or self.tooltip is None:
            self.tooltip = ctk.CTkLabel(
                self.text_box,
                text=translation,
                fg_color="#B8860B",
                text_color="#000000",
                corner_radius=5,
                font=("Arial", 12)
            )

        # Определяем позицию слова в текстовом виджете
        index = self.text_box.index(f"@{event.x},{event.y}")
        bbox = self.text_box.bbox(index)

        if bbox:
            x, y, width, height = bbox
            # Располагаем подсказку над словом
            try:
                self.tooltip.configure(text=translation)  # Обновляем текст
                self.tooltip.place(x=x, y=y)
                self.tooltip.lift()  # Поднимаем виджет над остальными
            except Exception as e:
                print(f"Ошибка при отображении подсказки: {e}")

    def hide_tooltip(self):
        """Скрываем всплывающую подсказку."""
        if hasattr(self, "tooltip") and self.tooltip is not None:
            try:
                self.tooltip.place_forget()
            except Exception as e:
                print(f"Ошибка при скрытии подсказки: {e}")

    # Добавление в избранное
    def on_word_click(self, event):
        """Обрабатываем нажатие на выделенное слово и добавляем его в избранное."""
        try:
            # Получаем слово под курсором
            index = self.text_box.index(f"@{event.x},{event.y}")
            word = self.text_box.get(f"{index} wordstart", f"{index} wordend").strip().lower()

            # Проверяем, существует ли слово в таблице Word
            word_data = self.db_manager.fetch_one(
                "SELECT id, translation FROM Word WHERE engword = ?", (word,)
            )

            if word_data is None:
                # Получаем перевод слова через API, если его нет в базе
                translation = self.get_translation(word)
                if not translation:
                    print("Ошибка при получении перевода.")
                    return

                # Добавляем слово в таблицу Word
                self.db_manager.execute(
                    "INSERT INTO Word (engword, translation) VALUES (?, ?)",
                    (word, translation)
                )
                word_id = self.db_manager.get_last_inserted_id()
            else:
                word_id = word_data[0]
                translation = word_data[1]

            # Получаем ID текущего пользователя
            user_id = self.get_user_id()

            # Проверяем, есть ли уже запись в таблице Favorites
            favorite_exists = self.db_manager.fetch_one(
                "SELECT id FROM Favorites WHERE user_id = ? AND word_id = ?",
                (user_id, word_id)
            )

            if favorite_exists is None:
                # Добавляем слово в избранное
                self.db_manager.execute(
                    "INSERT INTO Favorites (user_id, word_id) VALUES (?, ?)",
                    (user_id, word_id)
                )
                self.show_in_app_notification(f"Слово '{word}' добавлено в избранное.")
            else:
                self.show_in_app_notification(f"Слово '{word}' уже есть в избранном.")

        except Exception as e:
            print(f"Ошибка при добавлении слова в избранное: {e}")

    # окно с уведомлением
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