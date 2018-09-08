import click

import validation
from classes import PasswordManager


@click.group()
def cli():
    pass


@cli.group()
@click.pass_context
def account(ctx):
    """Manage your account."""
    manager = PasswordManager()
    ctx.obj = {'manager': manager}


@account.command()
@click.option('--username', type=str, help='Username for the new account.', prompt=True,
              callback=validation.new_username)
@click.option('--password', type=str, help='Password for the new account.', prompt=True,
              hide_input=True, confirmation_prompt=True)
@click.pass_context
def new(ctx, username, password):
    """Create a new account."""
    manager = ctx.obj['manager']
    manager.create_user(username, password)
    click.echo(f'Successfully created a new user with the username "{username}".')


def main():
    manager = PasswordManager()
    print(manager.check_user_existence_by_name('Christoph'))


if __name__ == '__main__':
    main()
