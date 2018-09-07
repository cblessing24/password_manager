import sqlite3
import os
from dataclasses import dataclass

import click


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

    def _select_user_by_name(self, name):
        self.cursor.execute('SELECT * FROM users WHERE name = :name', {'name': name})

    def _check_user_existence_by_name(self, name):
        self._select_user_by_name(name)
        if self.cursor.fetchall():
            return True
        return False

    def get_user_by_name(self, name):
        with self.connection:
            if not self._check_user_existence_by_name(name):
                raise DoesNotExist
            self._select_user_by_name(name)
            entries = self.cursor.fetchall()
            assert len(entries) == 1
            return User(*entries[0])

    def create_user(self, name, salt, enc_dek):
        with self.connection:
            if self._check_user_existence_by_name(name):
                raise AlreadyExists
            self.cursor.execute('INSERT INTO users VALUES (:name, :salt, :enc_dek)',
                                {'name': name, 'salt': salt, 'enc_dek': enc_dek})

    def remove_user_by_name(self, name):
        with self.connection:
            if not self._check_user_existence_by_name(name):
                raise DoesNotExist
            self.cursor.execute('DELETE FROM users WHERE name = :name', {'name': name})


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
