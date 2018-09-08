import click

import validation
from classes import UserDatabase


@click.group()
def cli():
    pass


@cli.group()
@click.pass_context
def account(ctx):
    """Manage your account."""
    user_db = UserDatabase()
    ctx.obj = {'user_db': user_db}


@account.command()
@click.option('--username', type=str, help='Username for the new account.', prompt=True,
              callback=validation.new_username)
@click.option('--password', type=str, help='Password for the new account.', prompt=True,
              hide_input=True, confirmation_prompt=True)
@click.pass_context
def new(ctx, username, password):
    """Create a new account."""
    user_db = ctx.obj['user_db']
    user_db.create_user(username, password)
    click.echo(f'Successfully created a new user with the username "{username}".')


def main():
    db = UserDatabase()
    print(db.check_user_existence_by_name('Christoph'))


if __name__ == '__main__':
    main()
