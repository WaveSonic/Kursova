class AppSession:
    """Клас для зберігання стану сесії користувача."""
    user_id = None
    username = None

    @classmethod
    def set_session(cls, user_id, username):
        cls.user_id = user_id
        cls.username = username

    @classmethod
    def clear_session(cls):
        cls.user_id = None
        cls.username = None