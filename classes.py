import sqlite3
import os
import base64

from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.fernet import Fernet, InvalidToken


class PasswordManager:
    """A password managing class.

    Attributes:
        user_exists: A boolean indicating if a already user exists or not.
        data_enc_key: A key that is used to encrypt/decrypt passwords. Only
            available after "authenticate" method has been run.
    """

    def __init__(self):
        """Initializes PasswordManager"""
        self._conn = sqlite3.connect('password_manager.db')
        self._c = self._conn.cursor()
        with self._conn:
            self._c.execute('''CREATE TABLE IF NOT EXISTS user (
            salt text,
            enc_data_enc_key text
            )''')
            self._c.execute('''CREATE TABLE IF NOT EXISTS passwords (
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
        """Authenticate the user.

        Args:
            master_password: A string, the user's master password.

        Returns:
            True if the authentication was successful, otherwise False.
        """
        # Run initial setup if no user exists.
        if not self.user_exists:
            salt = os.urandom(16)
            # Derive the key encryption key from the user's master password.
            key_enc_key = PasswordManager._derive_data_enc_key(
                salt, master_password)
            # Generate static data encryption key.
            self.data_enc_key = Fernet.generate_key()
            # Encrypt the data encryption key using the key encryption key.
            enc_data_enc_key = Fernet(
                key_enc_key).encrypt(self.data_enc_key)
            # Add the encrypted data encryption key and the salt to the user
            # table.
            with self._conn:
                self._c.execute('''INSERT INTO user VALUES (
                :salt, 
                :enc_data_enc_key
                )''', {
                    'salt': base64.urlsafe_b64encode(salt).decode(),
                    'enc_data_enc_key': enc_data_enc_key.decode()
                    })
        # Run this code if a user already exists.
        else:
            # Retrieve the user's salt and encrypted data encryption key from
            # the user table.
            salt, enc_data_enc_key = self._select_user()
            enc_data_enc_key = enc_data_enc_key.encode()
            # Derive the key encryption key from the user's master password.
            key_enc_key = PasswordManager._derive_data_enc_key(
                salt, master_password)
            # Try to decrypt the encrypted data encryption key using the key
            # encryption key. Return False if this fails.
            try:
                self.data_enc_key = Fernet(
                    key_enc_key).decrypt(enc_data_enc_key)
            except InvalidToken:
                return False
        return True

    def get(self, name):
        """Get a password from the manager.

        Args:
            name: A string, the name associated with the requested password.

        Returns:
            Two strings, the info and the password associated with the
            requested name.
        """
        _, enc_info, enc_password = self._select_password(name)
        # Decrypt the encrypted info and password using the data encryption
        # key.
        f = Fernet(self.data_enc_key)
        info = f.decrypt(enc_info.encode()).decode()
        password = f.decrypt(enc_password.encode()).decode()
        return info, password

    def new(self, name, info, password):
        """Add a new password to the manager.

        Args:
            name: A string, the name for the new password.
            info: A string, the info associated with the new password.
            password: A string, the new password.

        Returns:
            None.
        """
        # Encrypt the info and password  using the data encryption key.
        f = Fernet(self.data_enc_key)
        enc_info = f.encrypt(info.encode()).decode()
        enc_password = f.encrypt(password.encode()).decode()
        with self._conn:
            self._c.execute('''INSERT INTO passwords VALUES (
            :name,
            :enc_info,
            :enc_password
            )''', {
                'name': name,
                'enc_info': enc_info,
                'enc_password': enc_password
                })

    def delete(self, name):
        """Deletes a password from the manager.

        Args:
            name: A string, the name associated with the to be deleted
                password.

        Returns:
            None.
        """
        with self._conn:
            self._c.execute(
                'DELETE FROM passwords WHERE name = :name', {'name': name})

    def _select_user(self):
        return self._c.execute('SELECT * FROM user').fetchone()

    def _select_password(self, name):
        return self._c.execute(
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

    def __contains__(self, name):
        if self._select_password(name):
            return True
        return False

    def __iter__(self):
        passwords = self._c.execute('SELECT * FROM passwords ORDER BY name')
        while True:
            password = passwords.fetchone()
            if password is None:
                break
            name, _, _ = password
            yield name


def main():
    pass


if __name__ == '__main__':
    main()
