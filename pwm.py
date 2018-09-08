import click

import validation
from classes import PasswordManager


@click.group()
@click.pass_context
def cli(ctx):
    manager = PasswordManager()
    ctx.obj = {'manager': manager}


@cli.command()
@click.option('--username', type=str, help='Username for the new account.', prompt=True,
              callback=validation.new_username)
@click.option('--password', type=str, help='Password for the new account.', prompt=True,
              hide_input=True, confirmation_prompt=True)
@click.pass_context
def new(ctx, username, password):
    """Create a new account."""
    manager = ctx.obj['manager']
    manager.create_user(username, password)
    click.echo(f'Success: Created a new user with the username "{username}".')


@cli.group()
@click.pass_context
def account(ctx):
    """Manage your account."""
    manager = ctx.obj['manager']
    while True:
        username = click.prompt('Username', type=str)
        if manager.check_user_existence_by_name(username):
            break
        click.echo(f'Error: A user with the username "{username}" does not exist.')
    while True:
        password = click.prompt('Password', type=str, hide_input=True)
        if manager.authenticate_user(username, password):
            break
        click.echo(f'Error: Invalid password for user "{username}".')
    ctx.obj.update({'username': username, 'password': password})


@account.command()
@click.option('--new_password', type=str, help='Your new password.', prompt=True, hide_input=True,
              callback=validation.new_password)
@click.pass_context
def change_password(ctx, new_password):
    """Change the password of your account."""
    ctx.obj['manager'].change_user_password(ctx.obj['username'], ctx.obj['password'], new_password)
    click.echo('Success: Password changed.')


@account.command()
@click.pass_context
def delete(ctx):
    """Delete your account."""
    click.confirm('This action can not be reversed. Are you sure?', abort=True)
    username = ctx.obj['username']
    ctx.obj['manager'].delete_user(username)
    click.echo(f'Success: Deleted the user with the username "{username}".')


def main():
    manager = PasswordManager()
    print(manager.check_user_existence_by_name('Christoph'))


if __name__ == '__main__':
    main()
