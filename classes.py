import os
import sqlite3
import base64
from dataclasses import dataclass

from cryptography.fernet import Fernet, InvalidToken
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC


class PasswordManager:

    def __init__(self, directory=None):
        self.user_database = UserDatabase(directory)


    def check_user_existence_by_name(self, name):
        return name in self.user_database

    def create_user(self, name, password):
        salt = os.urandom(16)
        kek = self._derive_key_encryption_key_from_password(password, salt)
        dek = Fernet.generate_key()
        fernet = Fernet(kek)
        enc_dek = fernet.encrypt(dek)
        user = User(name, self.decode_salt(salt), enc_dek.decode())
        self.user_database.insert_user(user)

    def authenticate_user(self, name, password):
        user = self.user_database.get_user_by_name(name)
        salt = self.encode_salt(user.salt)
        kek = self._derive_key_encryption_key_from_password(password, salt)
        fernet = Fernet(kek)
        try:
            fernet.decrypt(user.enc_dek.encode())
        except InvalidToken:
            return False
        return True

    @staticmethod
    def _derive_key_encryption_key_from_password(password, salt):
        key_derivation_function = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
            backend=default_backend()
        )
        return base64.urlsafe_b64encode(key_derivation_function.derive(password.encode()))

    @staticmethod
    def decode_salt(encoded_salt):
        return base64.urlsafe_b64encode(encoded_salt).decode()

    @staticmethod
    def encode_salt(decoded_salt):
        return base64.urlsafe_b64decode(decoded_salt.encode())


class Database:

    def __init__(self, directory):
        if directory is None:
            directory = '.'
        self.connection = sqlite3.connect(os.path.join(directory, 'password_manager.db'))
        self.cursor = self.connection.cursor()


class UserDatabase(Database):

    def __init__(self, directory):
        super().__init__(directory)
        with self.connection:
            self.cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                name text,
                salt text,
                enc_dek text
                )''')

    def get_user_by_name(self, name):
        with self.connection:
            self._select_user_by_name(name)
            entries = self.cursor.fetchall()
            assert len(entries) == 1
            return User(*entries[0])

    def insert_user(self, user):
        with self.connection:
            self.cursor.execute('INSERT INTO users VALUES (:name, :salt, :enc_dek)',
                                {'name': user.name, 'salt': user.salt, 'enc_dek': user.enc_dek})

    def remove_user_by_name(self, name):
        with self.connection:
            self.cursor.execute('DELETE FROM users WHERE name = :name', {'name': name})

    def update_user_encrypted_data_encryption_key(self, name, new_enc_dek):
        with self.connection:
            self.cursor.execute('''UPDATE users SET encrypted_dek = :new_enc_dek
                WHERE name = :name''', {'new_enc_dek': new_enc_dek, 'name': name})

    def _select_user_by_name(self, name):
        self.cursor.execute('SELECT * FROM users WHERE name = :name', {'name': name})

    def __contains__(self, name):
        self._select_user_by_name(name)
        if self.cursor.fetchall():
            return True
        return False


@dataclass()
class User:
    name: str
    salt: str
    enc_dek: str


def main():
    manager = PasswordManager()
    print(manager.authenticate_user('test', 'test'))


if __name__ == '__main__':
    main()
