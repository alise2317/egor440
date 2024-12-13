import customtkinter as ctk
from db_manager import DatabaseManager
from main_window import MainWindow  # Импортируем класс главного окна

class AuthWindow:
    def __init__(self, root):
        self.root = root
        self.db = DatabaseManager()

        # Окно
        window_width = 800
        window_height = 800
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x_coordinate = (screen_width // 2) - (window_width // 2)
        y_coordinate = (screen_height // 2) - (window_height // 2)
        self.root.geometry(f"{window_width}x{window_height}+{x_coordinate}+{y_coordinate}")
        self.root.resizable(False, False)

        # Создаём фрейм авторизации
        self.frame = ctk.CTkFrame(self.root)
        self.frame.pack(pady=20, padx=60, fill="both", expand=True)

        # Заголовок
        self.label = ctk.CTkLabel(self.frame, text="Авторизация", font=("Arial", 25))
        self.label.pack(pady=40, padx=10)

        # Поле ввода логина
        self.username_entry = ctk.CTkEntry(self.frame, placeholder_text="Логин", height=40, width=300)
        self.username_entry.pack(pady=12, padx=10)

        # Поле ввода пароля
        self.password_entry = ctk.CTkEntry(self.frame, placeholder_text="Пароль", show="*", height=40, width=300)
        self.password_entry.pack(pady=20, padx=10)

        # Текст ошибки (изначально скрыт)
        self.error_label = ctk.CTkLabel(self.frame, text="", font=("Arial", 12), text_color="red")
        self.error_label.pack(pady=1)

        # Кнопка "Войти"
        self.login_button = ctk.CTkButton(self.frame, text="Вход", command=self.login, height=60,  width=240)
        self.login_button.pack(pady=12, padx=10)

        # Кнопка "Зарегистрироваться"
        self.register_button = ctk.CTkButton(self.frame, text="Регистрация", command=self.register, height=60, width=240)
        self.register_button.pack(pady=12, padx=10)

    def login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()

        if self.db.check_user_credentials(username, password):
            # Скрываем окно авторизации
            self.root.withdraw()
            # Переход на главное окно
            self.open_main_window(username)
        else:
            # Показываем сообщение об ошибке
            self.error_label.configure(text="Неверный логин или пароль!")

    def register(self):
        username = self.username_entry.get()
        password = self.password_entry.get()

        if self.db.add_user(username, password):
            self.error_label.configure(text="Регистрация прошла успешно!", text_color="green")
        else:
            self.error_label.configure(text="Логин уже существует!", text_color="red")

    def open_main_window(self, username):
        x_coordinate = self.root.winfo_x()
        y_coordinate = self.root.winfo_y()  # Получаем текущее положение главного окна
        # Создаём главное окно
        main_window = ctk.CTkToplevel(self.root)
        main_window.title("Главное меню")
        main_window.geometry(f"800x800+{x_coordinate}+{y_coordinate}")
        MainWindow(main_window, username)
