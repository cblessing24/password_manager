import sqlite3
import os
import base64

from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.fernet import Fernet


class Password:

    def __init__(self, name, info, password):
        self.name = name
        self.info = info
        self.password = password


class PasswordManager:

    def __init__(self, master_password):
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
        if not self.c.execute('SELECT * FROM user').fetchone():
            salt = os.urandom(16)
            key_derivation_func = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=salt,
                iterations=100000,
                backend=default_backend()
            )
            key_enc_key = base64.urlsafe_b64encode(
                key_derivation_func.derive(master_password.encode()))
            data_enc_key = Fernet.generate_key()
            enc_data_enc_key = Fernet(key_enc_key).encrypt(data_enc_key)
            with self.conn:
                self.c.execute('''INSERT INTO user VALUES (
                :salt, 
                :enc_data_enc_key
                )''', {
                    'salt': base64.urlsafe_b64encode(salt).decode(),
                    'enc_data_enc_key': enc_data_enc_key.decode()
                    })
        else:
            salt, enc_data_enc_key =  self.c.execute(
                'SELECT * FROM user').fetchone()
            salt = base64.urlsafe_b64decode(salt.encode())
            enc_data_enc_key = enc_data_enc_key.encode()
            key_derivation_func = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=salt,
                iterations=100000,
                backend=default_backend()
            )
            key_enc_key = base64.urlsafe_b64encode(
                key_derivation_func.derive(master_password.encode()))
            self.data_enc_key = Fernet(key_enc_key).decrypt(enc_data_enc_key)


    def authenticate(self, master_password):
        pass

    def get(self, name):
        pass

    def new(self, name, info, password):
        pass

    def delete(self, name):
        pass
