import sqlite3
import os
import base64

from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.fernet import Fernet, InvalidToken


class PasswordManager:

    def __init__(self):
        self.conn = sqlite3.connect('password_manager.db')
        self.c = self.conn.cursor()
        with self.conn:
            self.c.execute('''CREATE TABLE IF NOT EXISTS user (
            salt text,
            enc_data_enc_key text
            )''')
            self.c.execute('''CREATE TABLE IF NOT EXISTS passwords (
            name text,
            enc_info text,
            enc_password text
            )''')
        if self._select_user():
            self.user_exists = True
        else:
            self.user_exists = False
        self.data_enc_key = None

    def authenticate(self, master_password):
        if not self.user_exists:
            salt = os.urandom(16)
            key_enc_key = PasswordManager._derive_data_enc_key(
                salt, master_password)
            self.data_enc_key = Fernet.generate_key()
            enc_data_enc_key = Fernet(
                key_enc_key).encrypt(self.data_enc_key)
            with self.conn:
                self.c.execute('''INSERT INTO user VALUES (
                :salt, 
                :enc_data_enc_key
                )''', {
                    'salt': base64.urlsafe_b64encode(salt).decode(),
                    'enc_data_enc_key': enc_data_enc_key.decode()
                    })
        else:
            salt, enc_data_enc_key = self._select_user()
            enc_data_enc_key = enc_data_enc_key.encode()
            key_enc_key = PasswordManager._derive_data_enc_key(
                salt, master_password)
            try:
                self.data_enc_key = Fernet(
                    key_enc_key).decrypt(enc_data_enc_key)
            except InvalidToken:
                return False
        return True

    def get(self, name):
        _, enc_info, enc_password = self._select_password(name)
        f = Fernet(self.data_enc_key)
        info = f.decrypt(enc_info.encode()).decode()
        password = f.decrypt(enc_password.encode()).decode()
        return info, password

    def new(self, name, info, password):
        f = Fernet(self.data_enc_key)
        enc_info = f.encrypt(info.encode()).decode()
        enc_password = f.encrypt(password.encode()).decode()
        with self.conn:
            self.c.execute('''INSERT INTO passwords VALUES (
            :name,
            :enc_info,
            :enc_password
            )''', {
                'name': name,
                'enc_info': enc_info,
                'enc_password': enc_password
                })

    def delete(self, name):
        with self.conn:
            self.c.execute(
                'DELETE FROM passwords WHERE name = :name', {'name': name})

    def _select_user(self):
        return self.c.execute('SELECT * FROM user').fetchone()

    def _select_password(self, name):
        return self.c.execute(
            'SELECT * FROM passwords WHERE name = :name',
            {'name': name}
        ).fetchone()

    @staticmethod
    def _derive_data_enc_key(salt, master_password):
        if isinstance(salt, str):
            salt = base64.urlsafe_b64decode(salt.encode())
        key_derivation_func = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
            backend=default_backend()
        )
        return base64.urlsafe_b64encode(
            key_derivation_func.derive(master_password.encode()))
