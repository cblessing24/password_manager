import sqlite3
import os
import base64
from dataclasses import dataclass

import click
from cryptography.fernet import Fernet
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC


class Database:

    def __init__(self, directory):
        if directory is None:
            directory = '.'
        self.connection = sqlite3.connect(os.path.join(directory, 'password_manager.db'))
        self.cursor = self.connection.cursor()


class UserDatabase(Database):

    def __init__(self, directory=None):
        super().__init__(directory)
        with self.connection:
            self.cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                name text,
                salt text,
                enc_dek text
                )''')

    def get_user_by_name(self, name):
        with self.connection:
            if not self._check_user_existence_by_name(name):
                raise DoesNotExist
            self._select_user_by_name(name)
            entries = self.cursor.fetchall()
            assert len(entries) == 1
            return User(*entries[0])

    def create_user(self, name, password):
        salt = os.urandom(16)
        kek = self._derive_key_encryption_key_from_password(password, salt)
        dek = Fernet.generate_key()
        fernet = Fernet(kek)
        enc_dek = fernet.encrypt(dek)
        user = User(name, base64.urlsafe_b64encode(salt).decode(), enc_dek.decode())
        self.insert_user(user)
            
    def insert_user(self, user):
        with self.connection:
            if self._check_user_existence_by_name(user.name):
                raise AlreadyExists
            self.cursor.execute('INSERT INTO users VALUES (:name, :salt, :enc_dek)',
                                {'name': user.name, 'salt': user.salt, 'enc_dek': user.enc_dek})

    def remove_user_by_name(self, name):
        with self.connection:
            if not self._check_user_existence_by_name(name):
                raise DoesNotExist
            self.cursor.execute('DELETE FROM users WHERE name = :name', {'name': name})

    def _select_user_by_name(self, name):
        self.cursor.execute('SELECT * FROM users WHERE name = :name', {'name': name})

    def _check_user_existence_by_name(self, name):
        self._select_user_by_name(name)
        if self.cursor.fetchall():
            return True
        return False

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


class AlreadyExists(Exception):
    pass


class DoesNotExist(Exception):
    pass


@dataclass()
class User:
    name: str
    salt: str
    enc_dek: str


@click.group()
def cli():
    pass


@cli.group()
def account():
    pass


@account.command()
@click.option('--username', type=str, help='Username for the new account.', prompt=True)
@click.option('--password', type=str, help='Password for the new account.', prompt=True,
              hide_input=True, confirmation_prompt=True)
def new(username, password):
    pass


def main():
    db = UserDatabase()
    print(db.get_user_by_name('Adolf'))


if __name__ == '__main__':
    main()
