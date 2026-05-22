# security/session.py
class Session:
    _user = None

    @classmethod
    def set_user(cls, user_data):
        cls._user = user_data

    @classmethod
    def get_user(cls):
        return cls._user

    @classmethod
    def clear(cls):
        cls._user = None
