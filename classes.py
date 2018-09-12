class Password:

    def __init__(self, name, info, password):
        self.name = name
        self.info = info
        self.password = password


class PasswordManager:

    def __init__(self):
        pass

    def authenticate(self, master_password):
        pass

    def get(self, name):
        pass

    def new(self, name, info, password):
        pass

    def delete(self, name):
        pass
