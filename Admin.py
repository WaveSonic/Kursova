import customtkinter as ctk
import matplotlib.pyplot as plt
from sqlalchemy import extract, func
from datetime import datetime
from Session import AppSession
from sqlalchemy.orm import sessionmaker
from tkinter import messagebox
from db import engine, Patient, MedicalRecord, Appointment, Doctor, User, Log
Session = sessionmaker(bind=engine)
session = Session()
from tkinter import Canvas, Tk, Scrollbar, Frame

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

def delete_user(user_id, user_frame, canvas):
    """Функція для видалення користувача з бази даних і з інтерфейсу."""
    try:
        user = session.query(User).get(user_id)
        if user and user.role != 'admin':
            session.delete(user)
            session.commit()
            log_action(AppSession.user_id, "Видалення користувача", f"Aдміністратор {AppSession.username} видалив "
                                                                    f"користувача {user_id}")
            messagebox.showinfo("Успіх", "Користувач успішно видалений.")
            user_frame.destroy()  # Видаляємо віджет користувача з інтерфейсу
            show_users(canvas)
        else:
            if user.role == 'admin':
                messagebox.showerror("Помилка", "Неможливо видалити адміністратора")
            else:
                messagebox.showerror("Помилка", "Користувача не знайдено.")
    except Exception as e:
        session.rollback()
        messagebox.showerror("Помилка", f"Помилка при видаленні користувача: {e}")

def edit_user(user_id, users_window):
    # Знаходимо користувача в базі даних
    user = session.query(User).filter(User.id == user_id).first()
    if not user:
        messagebox.showerror("Помилка", "Користувача не знайдено.")
        return

    # Створення вікна для редагування користувача
    edit_window = ctk.CTkToplevel(users_window)
    edit_window.title("Редагування користувача")

    # Розміри вікна
    window_width = 400
    window_height = 300
    edit_window.geometry(f"{window_width}x{window_height}")

    # Поля для редагування інформації користувача
    ctk.CTkLabel(edit_window, text="Логін:").pack()
    username_entry = ctk.CTkEntry(edit_window)
    username_entry.insert(0, user.username)
    username_entry.pack()

    ctk.CTkLabel(edit_window, text="Роль:").pack()
    role_entry = ctk.CTkEntry(edit_window)
    role_entry.insert(0, user.role)
    role_entry.pack()

    # Функція для збереження змін
    def save_changes():
        user.username = username_entry.get()
        user.role = role_entry.get()
        try:
            session.commit()
            log_action(AppSession.user_id, "Корегування користувача", f"Aдміністратор {AppSession.username} корегував "
                                                                    f"користувача {user_id}")
            messagebox.showinfo("Успіх", "Користувача успішно оновлено.")
            edit_window.destroy()
        except Exception as e:
            messagebox.showerror("Помилка", f"Не вдалося оновити користувача: {e}")
            session.rollback()

    # Кнопка для збереження змін
    save_button = ctk.CTkButton(edit_window, text="Зберегти", command=save_changes)
    save_button.pack(pady=10)

def show_users(main_window):
    print(AppSession.user_id)
    main_window.destroy()
    users_window = ctk.CTk()
    users_window.title("Користувачі")

    # Розміри вікна
    window_width = 1200
    window_height = 500
    users_window.geometry(f"{window_width}x{window_height}")

    # Canvas для скролінга
    canvas = Canvas(users_window)
    canvas.pack(side="top", fill="both", expand=True)

    scrollbar = Scrollbar(users_window, command=canvas.yview)
    scrollbar.pack(side="right", fill="y")

    canvas.configure(yscrollcommand=scrollbar.set)

    def on_mousewheel(event):
        canvas.yview_scroll(int(-1*(event.delta/120)), "units")

    canvas.bind_all("<MouseWheel>", on_mousewheel)

    users_frame = Frame(canvas)
    canvas.create_window((0, 0), window=users_frame, anchor="nw", width=window_width)

    # Вміст користувачів
    for user in session.query(User).all():
        user_frame = ctk.CTkFrame(users_frame)
        user_frame.pack(fill="x", padx=5, pady=5)

        ctk.CTkLabel(user_frame, text=f"ID: {user.id} Логін: {user.username} Роль: {user.role}").pack(side="left")

        delete_button = ctk.CTkButton(user_frame, text="Видалити",
                                      command=lambda user_id=user.id: delete_user(user_id, user_frame, users_window))
        delete_button.pack(side="right")

        edit_button = ctk.CTkButton(user_frame, text="Редагувати",
                                    command=lambda user_id=user.id: edit_user(user_id, users_window))
        edit_button.pack(side="right", padx=5)

    canvas.bind('<Configure>', lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

    # Кнопка "Назад"
    back_button_frame = ctk.CTkFrame(users_window)
    back_button_frame.pack(side="bottom", fill="x")
    back_button = ctk.CTkButton(back_button_frame, text="Назад", command=lambda: open_main_window_admin(users_window))
    back_button.pack(pady=10)
    users_window.mainloop()

def show_logs(main_window):
    main_window.destroy()
    logs_window = ctk.CTk()
    logs_window.title("Логи")

    # Розміри вікна
    window_width = 1200
    window_height = 400
    logs_window.geometry(f"{window_width}x{window_height}")

    # Canvas для скролінга
    canvas = Canvas(logs_window)
    canvas.pack(side="top", fill="both", expand=True)

    scrollbar = Scrollbar(logs_window, command=canvas.yview)
    scrollbar.pack(side="right", fill="y")

    canvas.configure(yscrollcommand=scrollbar.set)

    def on_mousewheel(event):
        canvas.yview_scroll(int(-1*(event.delta/120)), "units")

    canvas.bind_all("<MouseWheel>", on_mousewheel)

    logs_frame = Frame(canvas)
    canvas.create_window((0, 0), window=logs_frame, anchor="nw", width=window_width)

    for log in session.query(Log).all():
        log_frame = ctk.CTkFrame(logs_frame)
        log_frame.pack(fill="x", padx=5, pady=5)

        ctk.CTkLabel(log_frame, text=f"{log.timestamp} - {log.action} - {log.details}").pack(side="left")

    canvas.bind('<Configure>', lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

    # Кнопка "Очистити таблицю"
    def clear_logs():
        try:
            # Видаляємо всі записи з таблиці логів
            session.query(Log).delete()
            session.commit()
            messagebox.showinfo("Очищення логів", "Всі логи були успішно видалені.")
            open_main_window_admin(logs_window)
        except Exception as e:
            # В разі помилки відкочуємо зміни
            session.rollback()
            messagebox.showerror("Помилка", f"Сталася помилка під час видалення логів: {e}")

    clear_button_frame = ctk.CTkFrame(logs_window)
    clear_button_frame.pack(side="bottom", fill="x")
    clear_button = ctk.CTkButton(clear_button_frame, text="Очистити таблицю", command=clear_logs)
    clear_button.pack(pady=10)

    # Кнопка "Назад"
    back_button = ctk.CTkButton(clear_button_frame, text="Назад",  command=lambda: open_main_window_admin(logs_window))
    back_button.pack(pady=10)

    logs_window.mainloop()

def show_doctors(main_window):
    main_window.destroy()
    doctors_window = ctk.CTk()
    doctors_window.title("Лікарі")

    # Розміри вікна
    window_width = 1200
    window_height = 400
    doctors_window.geometry(f"{window_width}x{window_height}")

    # Canvas для скролінга
    canvas = Canvas(doctors_window)
    canvas.pack(side="top", fill="both", expand=True)

    scrollbar = Scrollbar(doctors_window, command=canvas.yview)
    scrollbar.pack(side="right", fill="y")

    canvas.configure(yscrollcommand=scrollbar.set)

    def on_mousewheel(event):
        canvas.yview_scroll(int(-1*(event.delta/120)), "units")

    canvas.bind_all("<MouseWheel>", on_mousewheel)

    doctors_frame = Frame(canvas)
    canvas.create_window((0, 0), window=doctors_frame, anchor="nw", width=window_width)

    # Вміст таблиці лікарів
    for doctor in session.query(Doctor).all():
        doctor_frame = ctk.CTkFrame(doctors_frame)
        doctor_frame.pack(fill="x", padx=5, pady=5, expand=True)

        doctor_info = f"ID: {doctor.id} Ім'я: {doctor.first_name} {doctor.last_name}, Спеціалізація: {doctor.specialization}"
        ctk.CTkLabel(doctor_frame, text=doctor_info).pack(side="left", fill="x", expand=True)
        edit_button = ctk.CTkButton(doctor_frame, text="Редагувати",
                                    command=lambda doctor_id=doctor.id: edit_doctor(doctor_id, doctors_window))
        edit_button.pack(side="right", padx=5)

        delete_button = ctk.CTkButton(doctor_frame, text="Видалити",
                                      command=lambda doctor_id=doctor.id: delete_doctor(doctor_id, doctors_window))
        delete_button.pack(side="right", padx=5)
    canvas.bind('<Configure>', lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

    # Кнопка "Назад"
    add_doctor_button = ctk.CTkButton(doctors_window, text="Додати нового лікаря",
                                      command=lambda: add_new_doctor(doctors_window))
    add_doctor_button.pack(pady=10)  # Пакування перед кнопкою "Назад"

    back_button_frame = ctk.CTkFrame(doctors_window)
    back_button_frame.pack(side="bottom", fill="x")
    back_button = ctk.CTkButton(back_button_frame, text="Назад", command=lambda: open_main_window_admin(doctors_window))
    back_button.pack(pady=10)

    doctors_window.mainloop()

def add_new_doctor(doctors_window):
    doctors_window.destroy()
    new_doctor_window = ctk.CTk()
    new_doctor_window.title("Додавання нового лікаря")
    new_doctor_window.geometry("400x400")

    ctk.CTkLabel(new_doctor_window, text="Ім'я:").pack(pady=(10,0))
    first_name_entry = ctk.CTkEntry(new_doctor_window)
    first_name_entry.pack()

    ctk.CTkLabel(new_doctor_window, text="Прізвище:").pack(pady=(10,0))
    last_name_entry = ctk.CTkEntry(new_doctor_window)
    last_name_entry.pack()

    ctk.CTkLabel(new_doctor_window, text="Спеціалізація:").pack(pady=(10,0))
    specialization_entry = ctk.CTkEntry(new_doctor_window)
    specialization_entry.pack()

    ctk.CTkLabel(new_doctor_window, text="Email").pack(pady=(10, 0))
    email_entry = ctk.CTkEntry(new_doctor_window)
    email_entry.pack()

    ctk.CTkLabel(new_doctor_window, text="Пароль").pack(pady=(10, 0))
    password_entry = ctk.CTkEntry(new_doctor_window)
    password_entry.pack()

    def save_new_doctor():
        try:
            new_doctor = Doctor(
                first_name=first_name_entry.get(),
                last_name=last_name_entry.get(),
                specialization=specialization_entry.get(),
                contact_info=email_entry.get()
            )

            new_user = User(
                username = email_entry.get(),
                password = password_entry.get(),
                role='doctor'
            )
            session.add(new_doctor)
            session.add(new_user)
            session.commit()
            messagebox.showinfo("Успіх", "Нового лікаря успішно додано.")
            show_doctors(new_doctor_window)
        except Exception as e:
            session.rollback()
            messagebox.showerror("Помилка", f"Не вдалося додати нового лікаря: {e}")

    ctk.CTkButton(new_doctor_window, text="Зберегти", command=save_new_doctor).pack(pady=20)
    new_doctor_window.mainloop()

def edit_doctor(doctor_id, parent_window):
    parent_window.destroy()
    doctor = session.query(Doctor).filter(Doctor.id == doctor_id).first()
    if not doctor:
        messagebox.showerror("Помилка", "Лікаря не знайдено.")
        return

    edit_window = ctk.CTk()
    edit_window.title("Редагування лікаря")
    edit_window.geometry("300x300")

    ctk.CTkLabel(edit_window, text="Ім'я:").pack()
    first_name_entry = ctk.CTkEntry(edit_window)
    first_name_entry.insert(0, doctor.first_name)
    first_name_entry.pack()

    ctk.CTkLabel(edit_window, text="Прізвище:").pack()
    last_name_entry = ctk.CTkEntry(edit_window)
    last_name_entry.insert(0, doctor.last_name)
    last_name_entry.pack()

    ctk.CTkLabel(edit_window, text="Спеціалізація:").pack()
    specialization_entry = ctk.CTkEntry(edit_window)
    specialization_entry.insert(0, doctor.specialization)
    specialization_entry.pack()

    def save_changes():
        try:
            doctor.first_name = first_name_entry.get()
            doctor.last_name = last_name_entry.get()
            doctor.specialization = specialization_entry.get()
            session.commit()
            messagebox.showinfo("Успіх", "Лікаря успішно оновлено.")
        except Exception as e:
            session.rollback()
            messagebox.showerror("Помилка", f"Не вдалося оновити дані лікаря: {e}")

    ctk.CTkButton(edit_window, text="Зберегти зміни", command=lambda: [save_changes(), show_doctors(edit_window)]).pack(pady=10)
    edit_window.mainloop()

def delete_doctor(doctor_id, parent_window):
    try:
        doctor = session.query(Doctor).filter(Doctor.id == doctor_id).first()
        if doctor:
            session.delete(doctor)
            session.commit()
            messagebox.showinfo("Успіх", "Лікаря успішно видалено.")
            show_doctors(parent_window)  # Оновіть або закрийте поточне вікно і відкрийте знову, щоб показати оновлений список
        else:
            messagebox.showerror("Помилка", "Лікаря не знайдено.")
    except Exception as e:
        session.rollback()
        messagebox.showerror("Помилка", f"Не вдалося видалити лікаря: {e}")

def show_patients(main_window):
    main_window.destroy()
    patients_window = ctk.CTk()
    patients_window.title("Пацієнти")

    # Розміри вікна
    window_width = 1200
    window_height = 400
    patients_window.geometry(f"{window_width}x{window_height}")

    # Canvas для скролінга
    canvas = Canvas(patients_window)
    canvas.pack(side="top", fill="both", expand=True)

    scrollbar = Scrollbar(patients_window, command=canvas.yview)
    scrollbar.pack(side="right", fill="y")

    canvas.configure(yscrollcommand=scrollbar.set)
    canvas.bind_all("<MouseWheel>", lambda event: canvas.yview_scroll(int(-1*(event.delta/120)), "units"))

    patients_frame = Frame(canvas)
    canvas.create_window((0, 0), window=patients_frame, anchor="nw", width=window_width)

    for patient in session.query(Patient).all():
        patient_frame = ctk.CTkFrame(patients_frame)
        patient_frame.pack(fill="x", padx=5, pady=5, expand=True)

        patient_info = f"ID: {patient.id} Ім'я: {patient.first_name} {patient.last_name}, Телефон: {patient.phone_number}, Email: {patient.email}"
        ctk.CTkLabel(patient_frame, text=patient_info).pack(side="left", fill="x", expand=True)

        edit_button = ctk.CTkButton(patient_frame, text="Редагувати",
                                    command=lambda patient_id=patient.id: edit_patient(patient_id, patients_window))
        edit_button.pack(side="right", padx=5)

        delete_button = ctk.CTkButton(patient_frame, text="Видалити",
                                      command=lambda patient_id=patient.id: delete_patient(patient_id, patients_window))
        delete_button.pack(side="right", padx=5)

    canvas.bind('<Configure>', lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

    back_button_frame = ctk.CTkFrame(patients_window)
    back_button_frame.pack(side="bottom", fill="x")
    back_button = ctk.CTkButton(back_button_frame, text="Назад", command=lambda: open_main_window_admin(patients_window))
    back_button.pack(pady=10)

    patients_window.mainloop()

def edit_patient(patient_id, parent_window):
    parent_window.destroy()
    patient = session.query(Patient).filter(Patient.id == patient_id).first()
    if not patient:
        messagebox.showerror("Помилка", "Пацієнта не знайдено.")
        return

    edit_window = ctk.CTk()
    edit_window.title("Редагування пацієнта")
    edit_window.geometry("300x500")

    ctk.CTkLabel(edit_window, text="Ім'я:").pack(pady=(10,0))
    first_name_entry = ctk.CTkEntry(edit_window)
    first_name_entry.insert(0, patient.first_name)
    first_name_entry.pack()

    ctk.CTkLabel(edit_window, text="Прізвище:").pack(pady=(10,0))
    last_name_entry = ctk.CTkEntry(edit_window)
    last_name_entry.insert(0, patient.last_name)
    last_name_entry.pack()

    ctk.CTkLabel(edit_window, text="Дата народження:").pack(pady=(10,0))
    dob_entry = ctk.CTkEntry(edit_window)
    dob_entry.insert(0, patient.dob)
    dob_entry.pack()

    ctk.CTkLabel(edit_window, text="Стать:").pack(pady=(10,0))
    gender_entry = ctk.CTkEntry(edit_window)
    gender_entry.insert(0, patient.gender)
    gender_entry.pack()

    ctk.CTkLabel(edit_window, text="Номер телефону:").pack(pady=(10,0))
    phone_number_entry = ctk.CTkEntry(edit_window)
    phone_number_entry.insert(0, patient.phone_number)
    phone_number_entry.pack()

    ctk.CTkLabel(edit_window, text="Email:").pack(pady=(10,0))
    email_entry = ctk.CTkEntry(edit_window)
    email_entry.insert(0, patient.email)
    email_entry.pack()

    def save_changes():
        try:
            patient.first_name = first_name_entry.get()
            patient.last_name = last_name_entry.get()
            patient.dob = dob_entry.get()
            patient.gender = gender_entry.get()
            patient.phone_number = phone_number_entry.get()
            patient.email = email_entry.get()
            session.commit()
            messagebox.showinfo("Успіх", "Дані пацієнта успішно оновлено.")
            show_patients(edit_window)
        except Exception as e:
            session.rollback()
            messagebox.showerror("Помилка", f"Не вдалося оновити дані пацієнта: {e}")

    ctk.CTkButton(edit_window, text="Зберегти зміни", command=save_changes).pack(pady=20)

    edit_window.mainloop()

def delete_patient(patient_id, parent_window):
    try:
        patient = session.query(Patient).filter(Patient.id == patient_id).first()
        if patient:
            session.delete(patient)
            session.commit()
            messagebox.showinfo("Успіх", "Пацієнта успішно видалено.")
            show_patients(parent_window)
        else:
            messagebox.showerror("Помилка", "Пацієнта не знайдено.")
    except Exception as e:
        session.rollback()
        messagebox.showerror("Помилка", f"Не вдалося видалити пацієнта: {e}")

def plot_appointments_by_month(session):
    current_year = datetime.now().year
    current_month = datetime.now().month

    # Запит до бази даних для отримання кількості призначень по дням поточного місяця
    appointments_by_day = session.query(extract('day', Appointment.appointment_date).label('day'),
                                        func.count(Appointment.id).label('appointments_count')) \
        .filter(extract('year', Appointment.appointment_date) == current_year,
                extract('month', Appointment.appointment_date) == current_month) \
        .group_by('day') \
        .all()

    # Визначення кількості днів у поточному місяці
    days_in_month = (datetime(current_year, current_month + 1, 1) - datetime(current_year, current_month, 1)).days

    # Підготовка даних для графіка
    days = range(1, days_in_month + 1)
    appointments_count = [0] * days_in_month  # Ініціалізація списку з нулями

    for day, count in appointments_by_day:
        appointments_count[int(day) - 1] = count

    # Створення графіка
    plt.figure(figsize=(12, 6))
    plt.bar(days, appointments_count, color='lightgreen')
    plt.title('Кількість призначень по днях за ' + str(current_month) + ' місяць ' + str(current_year) + ' року')
    plt.xlabel('День')
    plt.ylabel('Кількість призначень')
    plt.xticks(days)
    plt.show()

def open_main_window_admin(login_window):
    login_window.destroy()

    # Створення головного вікна програми
    main_window = ctk.CTk()
    main_window.title("Головне вікно")
    main_window.update_idletasks()

    # Отримуємо розміри екрану
    screen_width = main_window.winfo_screenwidth()
    screen_height = main_window.winfo_screenheight()

    # Визначаємо розміри вікна
    window_width = 300
    window_height = 400

    # Розраховуємо позицію для центрування
    center_x = int((screen_width - window_width) / 2)
    center_y = int((screen_height - window_height) / 2)
    main_window.geometry(f"{window_width}x{window_height}+{center_x}+{center_y}")


    # Відображення ніку користувача у верхньому правому куті
    username_label = ctk.CTkLabel(main_window, text=f"Вітаємо:Admin {AppSession.username.split('@')[0]}", anchor='e')
    username_label.pack(side='top', fill='x', padx=10, pady=5)
    button_show_users = ctk.CTkButton(main_window, text="Показати користувачів",
                                      command=lambda: show_users(main_window))
    button_show_users.pack(pady=10)

    button_show_doctors = ctk.CTkButton(main_window, text="Показати лікарів",
                                        command=lambda: show_doctors(main_window))
    button_show_doctors.pack(pady=10)
    button_show_patient = ctk.CTkButton(main_window, text="Показати пацієнтів",
                                        command=lambda: show_patients(main_window))
    button_show_patient.pack(pady=10)
    button_show_info = ctk.CTkButton(main_window, text="Показати інформацію",
                                        command=lambda: plot_appointments_by_month(session))
    button_show_info.pack(pady=10)

    button_show_logs = ctk.CTkButton(main_window, text="Показати логи",
                                     command=lambda: show_logs(main_window))
    button_show_logs.pack(pady=10)
    # Додавання кнопки "Вихід"
    from main import show_login_window
    button_exit = ctk.CTkButton(main_window, text="Вихід", command=lambda: [main_window.destroy(), show_login_window() ])
    button_exit.pack(pady=20)


    # Запуск головного циклу програми
    main_window.mainloop()

if __name__ == "__main__":
    pass