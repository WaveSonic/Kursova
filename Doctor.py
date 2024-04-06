import customtkinter
from Session import AppSession


def open_main_window_doctor(login_window):
    login_window.destroy()

    # Створення головного вікна програми
    main_window = customtkinter.CTk()
    main_window.title("Головне вікно")
    main_window.update_idletasks()

    # Отримуємо розміри екрану
    screen_width = main_window.winfo_screenwidth()
    screen_height = main_window.winfo_screenheight()

    # Визначаємо розміри вікна
    window_width = 300
    window_height = 250

    # Розраховуємо позицію для центрування
    center_x = int((screen_width - window_width) / 2)
    center_y = int((screen_height - window_height) / 2)
    main_window.geometry(f"{window_width}x{window_height}+{center_x}+{center_y}")


    # Відображення ніку користувача у верхньому правому куті
    username_label = customtkinter.CTkLabel(main_window, text=f"Вітаємо:Докотор {AppSession.username.split('@')[0]}", anchor='e')
    username_label.pack(side='top', fill='x', padx=10, pady=5)

    # Додавання кнопки "Вихід"
    from main import show_login_window
    button_exit = customtkinter.CTkButton(main_window, text="Вихід", command=lambda: [main_window.destroy(), show_login_window()])
    button_exit.pack(pady=20)

    # Запуск головного циклу програми
    main_window.mainloop()

if __name__ == "__main__":
    pass