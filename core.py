import sqlite3
import os
import base64
from typing import Optional, Tuple

from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.fernet import Fernet, InvalidToken


def enforce_authentication(func):
    """Raise a runtime error if the user is not authenticated."""
    def wrapper(self, *args, **kwargs):
        if not self.authenticated:
            raise RuntimeError('Not authenticated.')
        return func(self, *args, **kwargs)
    return wrapper


def enforce_name_str_type(func):
    """Raise a type error if the name is not a string."""
    def wrapper(self, name, *args, **kwargs):
        if not isinstance(name, str):
            raise TypeError('Name must be a string.')
        return func(self, name, *args, **kwargs)
    return wrapper


class PasswordManager:
    """A password managing class.

    Attributes:
        user_exists: A boolean indicating if a already user exists or not.
        user: An instance of the User class.
        authenticated: A boolean indicating if the authentication was
            successful or not.
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
        self.user: Optional[User] = None
        self.authenticated: bool = False

    def authenticate(self, master_password: str) -> None:
        """Authenticate the user.

        Args:
            master_password: A string, the user's master password.

        Returns:
            None.
        """
        if self.authenticated:
            raise RuntimeError('A user is already authenticated.')
        if not isinstance(master_password, str):
            raise TypeError('Master password must be a string.')
        if self.user_exists:
            self._authenticate_existing_user(master_password)
        else:
            self._authenticate_new_user(master_password)

    def _authenticate_existing_user(self, master_password):
        # Retrieve the user's salt and encrypted data encryption key from
        # the user table.
        salt, enc_data_enc_key = self._select_user()
        salt = base64.urlsafe_b64decode(salt.encode())
        enc_data_enc_key = enc_data_enc_key.encode()
        # Initialize an instance of the user class using the retrieved
        # data.
        self.user = User(salt, enc_data_enc_key, master_password)
        # User instance's success attribute is False if the password was
        # incorrect.
        if self.user.initialized:
            self.authenticated = True

    def _authenticate_new_user(self, master_password):
        # Initialize a completely new user by just passing the master
        # password to the User constructor.
        self.user = User(master_password=master_password)
        # Add the encrypted data encryption key and the salt of the User
        # instance to the user table.
        if self.user.initialized:
            with self._conn:
                self._c.execute('''INSERT INTO user VALUES (
                                        :salt, 
                                        :enc_data_enc_key
                                        )''', {
                    'salt': base64.urlsafe_b64encode(
                        self.user.salt).decode(),
                    'enc_data_enc_key': self.user.enc_data_enc_key.decode()
                })
            self.authenticated = True

    @enforce_authentication
    @enforce_name_str_type
    def __getitem__(self, name: str) -> Tuple[str, str]:
        """Get a password from the manager.

        Args:
            name: A string, the name associated with the requested password.

        Returns:
            Two strings, the info and the password associated with the
            requested name.
        """
        if name not in self:
            raise KeyError('Name does not exist.')
        _, enc_info, enc_password = self._select_password(name)
        info = self.user.decrypt(enc_info.encode())
        password = self.user.decrypt(enc_password.encode())
        return info, password

    @enforce_authentication
    @enforce_name_str_type
    def __setitem__(self, name: str, value: Tuple[str, str]) -> None:
        """Add a new password to the manager.

        Args:
            name: A string, the name for the new password.
            value: A tuple containing two strings, the info associated with the
                new password and the new password itself.

        Returns:
            None.
        """
        if not isinstance(value, tuple):
            raise TypeError('Value must be a tuple.')
        if not len(value) == 2:
            raise ValueError('Tuple must have two elements.')
        if not isinstance(value[0], str) or not isinstance(value[1], str):
            raise TypeError('Both tuple elements must be strings.')
        info, password = value
        enc_info = self.user.encrypt(info)
        enc_password = self.user.encrypt(password)
        with self._conn:
            self._c.execute('''INSERT INTO passwords VALUES (
                        :name,
                        :enc_info,
                        :enc_password
                        )''', {
                'name': name,
                'enc_info': enc_info.decode(),
                'enc_password': enc_password.decode()
            })

    @enforce_authentication
    @enforce_name_str_type
    def __delitem__(self, name: str) -> None:
        """Deletes a password from the manager.

        Args:
            name: A string, the name associated with the to be deleted
                password.

        Returns:
            None.
        """
        if name not in self:
            raise KeyError
        with self._conn:
            self._c.execute(
                'DELETE FROM passwords WHERE name = :name', {'name': name})

    @enforce_authentication
    def reset(self) -> None:
        """Deletes the user and any passwords in the manager."""
        with self._conn:
            self._c.execute('DELETE FROM user')
            self._c.execute('DELETE FROM passwords')

    @enforce_authentication
    def change_password(self, new_password: str) -> None:
        """Change the user's master password.

        Args:
            new_password: A string, the new master password.

        Returns:
            None.
        """
        if not isinstance(new_password, str):
            raise TypeError('New password must be a string.')
        self.user.change_password(new_password)
        with self._conn:
            self._c.execute(
                'UPDATE user SET enc_data_enc_key = :enc_data_enc_key',
                {'enc_data_enc_key': self.user.enc_data_enc_key.decode()}
            )

    def _select_user(self):
        users = self._c.execute('SELECT * FROM user').fetchall()
        assert len(users) <= 1
        if not users:
            return False
        return users[0]

    def _select_password(self, name):
        passwords = self._c.execute(
            'SELECT * FROM passwords WHERE name = :name',
            {'name': name}
        ).fetchall()
        assert len(passwords) <= 1
        if not passwords:
            return False
        return passwords[0]

    def __contains__(self, name: str) -> bool:
        if self._select_password(name):
            return True
        return False

    def __iter__(self) -> str:
        passwords = self._c.execute('SELECT * FROM passwords ORDER BY name')
        while True:
            password = passwords.fetchone()
            if password is None:
                break
            name, _, _ = password
            yield name


class User:
    """A class that represents a user of the password manager.

    Attributes:
        initialized: Bool, True if the initialization was successful, false
            otherwise.
        salt: Bytes, the user's salt.
        data_enc_key: Bytes, the data encryption key used to encrypt/decrypt
            the user's passwords.
        enc_data_enc_key: Bytes, the user's encrypted data encryption key.
    """

    def __init__(
            self,
            salt: Optional[bytes] = None,
            enc_data_enc_key: Optional[bytes] = None,
            master_password: Optional[str] = None
    ):
        """Initializes User.

        An instance of this class can be initialized with just the master
        password to create a completely new user. Alternatively a existing user
        can be reinstated by passing all three arguments.

        Args:
            salt: Bytes, the user's salt.
            enc_data_enc_key: Bytes, the user's encrypted data encryption key.
            master_password: A string, the user's master password or a new
                password for creating a completely new user.
        """
        # Check whether a completely new user should be created or an existing
        # user reinstated.
        if (salt is None and enc_data_enc_key is None and
                master_password is not None):
            initialized = False
        elif (salt is not None and enc_data_enc_key is not None and
              master_password is not None):
            initialized = True
        else:
            raise RuntimeError('Incorrect combination of arguments passed.')
        if initialized:
            # An existing user should be reinstated.
            # Derive the key encryption key from the user's master password.
            key_enc_key = User._derive_data_enc_key(
                salt, master_password)
            # Try to decrypt the encrypted data encryption key using the key
            # encryption key.
            try:
                self.data_enc_key: bytes = Fernet(
                    key_enc_key).decrypt(enc_data_enc_key)
            except InvalidToken:
                self.initialized = False
            else:
                self.initialized = True
        else:
            # A completely new user should  be created.
            salt = os.urandom(16)
            # Derive the key encryption key from the user's master password.
            key_enc_key = User._derive_data_enc_key(
                salt, master_password)
            # Generate static data encryption key.
            self.data_enc_key: bytes = Fernet.generate_key()
            # Encrypt the data encryption key using the key encryption key.
            enc_data_enc_key = Fernet(key_enc_key).encrypt(self.data_enc_key)
            self.initialized = True
        self.salt: bytes = salt
        self.enc_data_enc_key: bytes = enc_data_enc_key

    def encrypt(self, data: str) -> bytes:
        """Encrypt data using the user's data encryption key."""
        return Fernet(self.data_enc_key).encrypt(data.encode())

    def decrypt(self, token: bytes) -> str:
        """Decrypt a token using the user's data encryption key."""
        return Fernet(self.data_enc_key).decrypt(token).decode()

    def change_password(self, new_password: str) -> None:
        """Change the master password of the user.

        Args:
            new_password: A string, the new password.

        Returns:
            None.
        """
        key_enc_key = User._derive_data_enc_key(self.salt, new_password)
        self.enc_data_enc_key = Fernet(key_enc_key).encrypt(self.data_enc_key)

    @staticmethod
    def _derive_data_enc_key(salt: bytes, master_password: str) -> bytes:
        key_derivation_func = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
            backend=default_backend()
        )
        return base64.urlsafe_b64encode(
            key_derivation_func.derive(master_password.encode()))


def main():
    pass


if __name__ == '__main__':
    main()
