import json

import click


class SiteDatabase:

    def __init__(self, database_path='database.json'):
        self.database_path = database_path
        try:
            self.database = self.load()
            print(self.database)
        except FileNotFoundError:
            self.database = {}

    def add(self, name, login, password):
        if name in self.database:
            raise SiteAlreadyExists()
        self.database[name] = {'login': login, 'password': password}
        self.save()

    def remove(self, name):
        if name not in self.database:
            raise SiteDoesNotExist()
        del self.database[name]
        self.save()

    def get(self, name):
        if name not in self.database:
            raise SiteDoesNotExist()
        return self.database[name]

    def save(self):
        with open(self.database_path, 'w') as f:
            json.dump(self.database, f, indent=4, sort_keys=True)

    def load(self):
        with open(self.database_path, 'r') as f:
            return json.load(f)


class SiteAlreadyExists(Exception):
    pass


class SiteDoesNotExist(Exception):
    pass


@click.group()
def cli():
    pass


@cli.command()
@click.argument('name')
@click.argument('login')
@click.argument('password')
def add(name, login, password):
    db = SiteDatabase()
    try:
        db.add(name, login, password)
    except SiteAlreadyExists:
        click.echo(f'Error: A site with the name "{name}" already exists. Please choose another name.')
    else:
        click.echo(f'Added entry with name "{name}".')


@cli.command()
@click.argument('name')
def remove(name):
    db = SiteDatabase()
    try:
        db.remove(name)
    except SiteDoesNotExist:
        click.echo(f'Error: A site with the name "{name}" does not exist.')
    else:
        click.echo(f'Removed the site with the name "{name}".')


@cli.command()
@click.argument('name')
def get(name):
    db = SiteDatabase()
    try:
        site = db.get(name)
    except SiteDoesNotExist:
        click.echo(f'Error: A site with the name "{name}" does not exist.')
    else:
        click.echo(site)
