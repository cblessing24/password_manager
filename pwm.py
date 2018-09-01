import json
from dataclasses import dataclass

import click
import clipboard


class SiteDatabase:

    def __init__(self, database_path='database.json'):
        self.database_path = database_path
        try:
            self.database = self.load()
        except FileNotFoundError:
            self.database = {}
        self.n_sites = len(self.database)

    def add(self, name, login, password):
        if name in self.database:
            raise SiteAlreadyExists()
        self.database[name] = Site(login, password)
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
            json_database = {name: {'login': site.login, 'password': site.password} for name, site in self}
            json.dump(json_database, f, indent=4, sort_keys=True)

    def load(self):
        with open(self.database_path, 'r') as f:
            json_database = json.load(f)
            return {name: Site(json_site['login'], json_site['password']) for name, json_site in json_database.items()}

    def drop(self):
        self.database = {}
        self.save()

    def __iter__(self):
        for name, site in self.database.items():
            yield name, site


@dataclass()
class Site:
    login: str
    password: str


class SiteAlreadyExists(Exception):
    pass


class SiteDoesNotExist(Exception):
    pass


def abort_if_false(context, _, value):
    if not value:
        context.abort()


@click.group()
def cli():
    pass


@cli.command()
@click.option('--name', type=str, help='Name of the new site.', prompt=True)
@click.option('--login', type=str, help='Login information of the new site.', prompt=True)
@click.option('--password', type=str, help='Password of the new site.', prompt=True, hide_input=True)
def new(name, login, password):
    """Add a new site to the database."""
    db = SiteDatabase()
    try:
        db.add(name, login, password)
    except SiteAlreadyExists:
        click.echo(f'Error: A site with the name "{name}" already exists. Please choose another name.')
    else:
        click.echo(f'Added entry with name "{name}".')


@cli.command()
@click.option('--name', type=str, help='Name of the site.', prompt=True)
@click.option('--yes', is_flag=True, callback=abort_if_false, expose_value=False,
              prompt=f'Are you sure you want to remove the site?')
def remove(name):
    """Remove a site from the database."""
    db = SiteDatabase()
    try:
        db.remove(name)
    except SiteDoesNotExist:
        click.echo(f'Error: A site with the name "{name}" does not exist.')
    else:
        click.echo(f'Removed the site with the name "{name}".')


@cli.command()
@click.option('--name', type=str, help='Name of the site.', prompt=True)
@click.option('--login', 'copy_login', help='Copy the login instead of the password.', is_flag=True)
def get(name, copy_login):
    """Copy the password of a site to the clipboard."""
    db = SiteDatabase()
    try:
        site = db.get(name)
    except SiteDoesNotExist:
        click.echo(f'Error: A site with the name "{name}" does not exist.')
    else:
        if copy_login:
            clipboard.copy(site.login)
            click.echo('Copied login to clipboard.')
        else:
            clipboard.copy(site.password)
            click.echo('Copied password to clipboard.')


@cli.command()
@click.option('--yes', is_flag=True, callback=abort_if_false, expose_value=False,
              prompt=f'Are you sure you want to drop the database?')
def drop():
    """Drop the database."""
    db = SiteDatabase()
    db.drop()
    click.echo('Database dropped.')


@cli.command()
def ls():
    """List all sites in the database."""
    db = SiteDatabase()
    if db.n_sites == 0:
        click.echo('0 sites in database.')
    else:
        if db.n_sites == 1:
            click.echo(f'{db.n_sites} site in database:')
        else:
            click.echo(f'{db.n_sites} sites in database:')
        for name, site in db:
            click.echo(f'Name: {name}, Login: {site.login}, Password: {site.password}')


def main():
    db = SiteDatabase()
    # db.add('Test1', 'mail1@test.de', 'password1')
    # db.add('Test2', 'mail2@test.de', 'password2')
    # db.add('Test3', 'mail3@test.de', 'password3')
    # db.add('Test4', 'mail4@test.de', 'password4')
    # db.add('Test5', 'mail5@test.de', 'password5')
    db.drop()


if __name__ == '__main__':
    main()
