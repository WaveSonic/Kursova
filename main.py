# main.py
from datetime import datetime
from sqlalchemy.orm import sessionmaker
from db import engine, Patient, MedicalRecord, Appointment, Doctor, User, Log
from werkzeug.security import generate_password_hash, check_password_hash
from tkinter import messagebox
import customtkinter
import customtkinter as ctk
from validate_email import validate_email
from Doctor import open_main_window_doctor
from Patient import open_main_window_user
from Admin import open_main_window_admin
from Session import AppSession

Session = sessionmaker(bind=engine)
session = Session()

def log_action(user_id, action, details):
    """Функція для логування дій користувачів."""
    new_log = Log(
        user_id=user_id,
        action=action,
        timestamp=datetime.now(),
        details=details
    )
    session.add(new_log)
    session.commit()

def is_valid_email(email):
    return validate_email(email)

def focus_next_widget(event):
    event.widget.tk_focusNext().focus()
    return("break")

def on_enter(event, entry_username, entry_password, login_window):
    login(entry_username, entry_password, login_window)


def switch_role(registration_window):
    global entries
    def on_register_click():
        user_data = {field: widget.get() for field, widget in entries.items() if
                     widget.winfo_manager()}  # Отримання даних тільки для видимих віджетів
        register_user(user_data, role.get(), registration_window)
    # Видаляємо існуючі поля вводу
    for widget in input_frame.winfo_children():
        widget.destroy()

    entries = {}
    common_fields = ["Ім'я", "Прізвище", "Email", "Пароль", "Перевірка пароля"]
    patient_fields = common_fields + ["Дата народження", "Номер телефону", "Гендер"]
    doctor_fields = common_fields + ["Спеціалізація", "Контактна інформація"]
    fields = patient_fields if role.get() == "Пацієнт" else doctor_fields

    for field in fields:
        ctk.CTkLabel(input_frame, text=field).pack(fill='x', padx=10, pady=2)
        if field == "Гендер":
            widget = ctk.CTkComboBox(input_frame, values=["Чоловік", "Жінка", "Інше"])
            widget.bind("<Return>", lambda event: on_register_click())
        else:
            widget = ctk.CTkEntry(input_frame)
            if field == "Контактна інформація":
                widget.bind("<Return>", lambda event: on_register_click())
            else:
                widget.bind("<Return>", focus_next_widget)
        widget.pack(fill='x', padx=10, pady=2)
        entries[field] = widget



    ctk.CTkButton(input_frame, text="Зареєструвати", command=on_register_click).pack(pady=(10, 2))
    ctk.CTkButton(input_frame, text="Назад", command=lambda: [registration_window.destroy(), show_login_window()]).pack(
        pady=2)

def login(entry_username, entry_password, login_window):
    username = entry_username.get()
    password = entry_password.get()
    user = session.query(User).filter(User.username == username).first()

    if user and check_password_hash(user.password, password):
        AppSession.set_session(user.id, user.username)
        log_action(user.id, "Вхід в систему", "Вхід користувача в систему")
        if user.role == 'admin':
            open_main_window_admin(login_window)
        elif user.role == 'patient':
            open_main_window_user(login_window)
        elif user.role == 'doctor':
            open_main_window_doctor(login_window)
    else:
        # Якщо користувач не знайдений, реєструємо спробу входу з невірними даними
        log_action(None, "Вхід в систему", "Неправильний логін або пароль")
        messagebox.showerror("Помилка", "Неправильний логін або пароль.")

def show_login_window():
    login_window = customtkinter.CTk()
    login_window.title("Вхід в систему")
    login_window.update_idletasks()

    # Отримуємо розміри екрану
    screen_width = login_window.winfo_screenwidth()
    screen_height = login_window.winfo_screenheight()

    # Визначаємо розміри вікна
    window_width = 300
    window_height = 250

    # Розраховуємо позицію для центрування
    center_x = int((screen_width - window_width) / 2)
    center_y = int((screen_height - window_height) / 2)

    # Налаштування розмірів і позиції вікна
    login_window.geometry(f"{window_width}x{window_height}+{center_x}+{center_y}")
    # Налаштування розмірів вікна
    login_window.geometry("400x250")

    # Елементи інтерфейсу для входу
    label_username = customtkinter.CTkLabel(login_window, text="Логін")
    label_password = customtkinter.CTkLabel(login_window, text="Пароль")
    entry_username = customtkinter.CTkEntry(login_window)
    entry_password = customtkinter.CTkEntry(login_window, show="*")
    entry_username.focus()
    entry_password.bind("<Return>", lambda event: on_enter(event, entry_username, entry_password, login_window))
    button_login = customtkinter.CTkButton(login_window, text="Увійти",
                             command=lambda: login(entry_username, entry_password, login_window))
    button_cancel = customtkinter.CTkButton(login_window, text="Реєстрація",
                                            command=lambda: show_registration_window(login_window))

    # Розташування елементів у вікні для входу
    label_username.pack(pady=(10, 0))
    entry_username.pack()
    label_password.pack(pady=(10, 0))
    entry_password.pack()
    button_login.pack(pady=(10, 0))
    button_cancel.pack(pady=(10, 0))
    entry_username.bind("<Return>", focus_next_widget)
    # Запуск головного циклу програми для входу
    login_window.mainloop()


def show_registration_window(login_window):
    global input_frame, role
    login_window.destroy()
    registration_window = customtkinter.CTk()
    registration_window.title("Реєстрація")
    registration_window.update_idletasks()

    # Отримуємо розміри екрану
    screen_width = registration_window.winfo_screenwidth()
    screen_height = registration_window.winfo_screenheight()

    # Визначаємо розміри вікна
    window_width = 500
    window_height = 800

    # Розраховуємо позицію для центрування
    center_x = int((screen_width - window_width) / 2)
    center_y = int((screen_height - window_height) / 2)

    # Налаштування розмірів і позиції вікна
    registration_window.geometry(f"{window_width}x{window_height}+{center_x}+{center_y}")  # Трохи більше розмір для реєстраційного вікна

    role = customtkinter.StringVar(value="Пацієнт")
    ctk.CTkRadioButton(registration_window, text="Пацієнт", variable=role, value="Пацієнт", command=lambda: switch_role(registration_window)).pack(
        anchor='w', padx=10, pady=2)
    ctk.CTkRadioButton(registration_window, text="Лікар", variable=role, value="Лікар", command=lambda: switch_role(registration_window)).pack(anchor='w',
                                                                                                           padx=10,
                                                                                                           pady=2)

    # Фрейм для полів вводу, які будуть змінюватися
    input_frame = ctk.CTkFrame(registration_window)
    input_frame.pack(fill='both', expand=True, padx=10, pady=10)

    # Початкове заповнення полів для ролі "Пацієнт"
    switch_role(registration_window)
    registration_window.mainloop()


def register_user(entries, role, registration_window):
    # entries - словник з полями та їх значеннями
    session = Session()  # Створення сесії SQLAlchemy
    email = entries['Email']
    password = entries['Пароль']
    password_confirm = entries["Перевірка пароля"]
    if not validate_email(email):
        messagebox.showerror("Помилка валідації", "Введено некоректний Email")
        return

        # Перевірка на співпадіння паролів
    if password != password_confirm:
        messagebox.showerror("Помилка валідації", "Паролі не співпадають")
        return

    if role == "Пацієнт":
        # Створення екземпляра пацієнта
        patient = Patient(
            first_name=entries['Ім\'я'],
            last_name=entries['Прізвище'],
            dob=entries['Дата народження'],
            gender=entries['Гендер'],
            phone_number=entries['Номер телефону'],
            email=entries['Email']
        )
        session.add(patient)  # Додавання пацієнта до сесії

        # Створення користувача
        user = User(
            username=entries['Email'],  # Припускаємо, що логін - це email
            password=generate_password_hash(entries['Пароль']),
            role='patient'
        )
        session.add(user)
        registration_window.destroy()
    elif role == "Лікар":
        # Створення екземпляра лікаря
        doctor = Doctor(
            first_name=entries['Ім\'я'],
            last_name=entries['Прізвище'],
            specialization=entries['Спеціалізація'],
            contact_info=entries['Контактна інформація']
        )
        session.add(doctor)

        # Створення користувача
        user = User(
            username=entries['Email'],  # Можливо, потрібно використовувати інше поле для логіну
            password=generate_password_hash(entries['Пароль']),
            role='doctor'
        )
        session.add(user)
        registration_window.destroy()
    try:
        session.commit()  # Збереження змін у базі даних
        messagebox.showinfo("Успіх", "Реєстрація пройшла успішно!")
        show_login_window()
    except Exception as e:
        session.rollback()  # Відкат змін у разі помилки
        messagebox.showerror("Помилка", f"Помилка реєстрації: {e}")
    finally:
        session.close()  # Закриття сесії

session.close()


if __name__ == '__main__':
    show_login_window()


