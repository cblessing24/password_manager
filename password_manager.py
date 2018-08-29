from dataclasses import dataclass


class AccountInformationDatabase:

    def __init__(self):
        self.database = {}

    def add(self, name, login, password):
        if name in self.database:
            raise ValueError(f'"{name}" already exists!')
        self.database[name] = AccountInformation(login, password)

    def remove(self, name):
        if name not in self.database:
            raise ValueError(f'"{name}" does not exist!')
        del self.database[name]

    def get(self, name):
        if name not in self.database:
            raise ValueError(f'"{name}" does not exist!')
        return self.database[name]


@dataclass
class AccountInformation:
    login: str
    password: str


def main():
    account_information_database = AccountInformationDatabase()
    account_information_database.add('hallo', 'test@web.de', 'password123')
    account_information_database.remove('test')
    print(account_information_database.get('test'))


if __name__ == '__main__':
    main()
