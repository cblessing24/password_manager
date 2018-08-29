import pickle
from dataclasses import dataclass


class AccountInformationDatabase:

    def __init__(self, database_path='database.pickle'):
        self.database_path = database_path
        try:
            with open(database_path, 'rb') as f:
                self.database = pickle.load(f)
        except FileNotFoundError:
            self.database = {}

    def add(self, name, login, password):
        if name in self.database:
            raise ValueError(f'"{name}" already exists!')
        self.database[name] = AccountInformation(login, password)
        self.save()

    def remove(self, name):
        if name not in self.database:
            raise ValueError(f'"{name}" does not exist!')
        del self.database[name]
        self.save()

    def get(self, name):
        if name not in self.database:
            raise ValueError(f'"{name}" does not exist!')
        return self.database[name]

    def save(self):
        with open(self.database_path, 'wb') as f:
            pickle.dump(self.database, f)


@dataclass
class AccountInformation:
    login: str
    password: str


def main():
    account_information_database = AccountInformationDatabase()
    account_information_database.remove('hallo')
    print(account_information_database.get('hallo'))


if __name__ == '__main__':
    main()
