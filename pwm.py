import json
import dataclasses

import click
import clipboard


class JSONDataclassEncoder(json.JSONEncoder):

    def default(self, object_):
        if dataclasses.is_dataclass(object_):
            return dataclasses.asdict(object_)
        return super().default(object_)


class Database:

    def __init__(self, database_path, class_):
        self.class_ = class_
        self.database_path = database_path
        self.database = None
        self.n_entries = None
        try:
            self.load()
        except FileNotFoundError:
            self.init()

    def get(self, name):
        if name not in self.database['data']:
            raise DoesNotExistError
        return self.database['data'][name]

    def new(self, name, instance):
        if name in self.database['data']:
            raise AlreadyExistsError
        self.database['data'][name] = instance
        self.update_n_entries()
        self.save()

    def remove(self, name):
        if name not in self.database['data']:
            raise DoesNotExistError
        del self.database['data'][name]
        self.update_n_entries()
        self.save()

    def save(self):
        with open(self.database_path, 'w') as f:
            json.dump(self.database, f, cls=JSONDataclassEncoder, indent=4, sort_keys=True)

    def load(self):
        with open(self.database_path, 'r') as f:
            database_as_dict = json.load(f)
            if database_as_dict['class'] != self.class_.__name__:
                raise DatabaseClassMismatchError
            # Convert the dicts back to dataclass objects
            self.database = {'class': database_as_dict['class'], 'data': {}}
            for key, object_as_dict in database_as_dict['data'].items():
                self.database['data'][key] = self.class_(*object_as_dict.values())
            self.update_n_entries()

    def init(self):
        self.database = {'class': self.class_.__name__, 'data': {}}
        self.update_n_entries()
        self.save()

    def drop(self):
        self.database['data'] = {}
        self.update_n_entries()
        self.save()

    def update_n_entries(self):
        self.n_entries = len(self.database['data'])

    def __iter__(self):
        for name, object_ in self.database['data'].items():
            yield name, object_


class DoesNotExistError(Exception):
    pass


class AlreadyExistsError(Exception):
    pass


class DatabaseClassMismatchError(Exception):
    pass


@dataclasses.dataclass()
class Site:
    login: str
    password: str


def abort_if_false(context, _, value):
    if not value:
        context.abort()


@click.group()
@click.pass_context
def cli(context):
    database = Database('sites.json', Site)
    context.obj = {'database': database}


@cli.command()
@click.option('--name', type=str, help='Name of the new site.', prompt=True)
@click.option('--login', type=str, help='Login information of the new site.', prompt=True)
@click.option('--password', type=str, help='Password of the new site.', prompt=True, hide_input=True)
@click.pass_context
def new(context, name, login, password):
    """Add a new site to the database."""
    database = context.obj['database']
    site = Site(login, password)
    try:
        database.new(name, site)
    except AlreadyExistsError:
        click.echo(f'Error: A site with the name "{name}" already exists. Please choose another name.')
    else:
        click.echo(f'Added entry with name "{name}".')


@cli.command()
@click.option('--name', type=str, help='Name of the site.', prompt=True)
@click.option('--yes', is_flag=True, callback=abort_if_false, expose_value=False,
              prompt=f'Are you sure you want to remove the site?')
@click.pass_context
def remove(context, name):
    """Remove a site from the database."""
    database = context.obj['database']
    try:
        database.remove(name)
    except DoesNotExistError:
        click.echo(f'Error: A site with the name "{name}" does not exist.')
    else:
        click.echo(f'Removed the site with the name "{name}".')


@cli.command()
@click.option('--name', type=str, help='Name of the site.', prompt=True)
@click.option('--login', 'copy_login', help='Copy the login instead of the password.', is_flag=True)
@click.pass_context
def get(context, name, copy_login):
    """Copy the password of a site to the clipboard."""
    database = context.obj['database']
    try:
        site = database.get(name)
    except DoesNotExistError:
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
@click.pass_context
def drop(context):
    """Drop the database."""
    database = context.obj['database']
    database.drop()
    click.echo('Database dropped.')


@cli.command()
@click.pass_context
def ls(context):
    """List all sites in the database."""
    database = context.obj['database']
    if database.n_entries == 0:
        click.echo('0 sites in database.')
    else:
        if database.n_entries == 1:
            click.echo(f'{database.n_entries} site in database:')
        else:
            click.echo(f'{database.n_entries} sites in database:')
        for name, site in database:
            click.echo(f'Name: {name}, Login: {site.login}, Password: {site.password}')


def main():
    pass


if __name__ == '__main__':
    main()
