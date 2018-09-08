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
    click.echo(f'Success: Created a new user with the username "{username}".')


@account.command()
@click.option('--username', type=str, help='Your username.', prompt=True,
              callback=validation.username)
@click.option('--old_password', type=str, help='Your old password.', prompt=True, hide_input=True,
              callback=validation.password)
@click.option('--new_password', type=str, help='Your new password.', prompt=True, hide_input=True,
              callback=validation.new_password)
@click.pass_context
def change_password(ctx, username, old_password, new_password):
    """Change your password."""
    manager = ctx.obj['manager']
    manager.change_user_password(username, old_password, new_password)
    click.echo('Success: Password changed.')


@account.command()
@click.option('--username', type=str, help='Your username.', prompt=True,
              callback=validation.username)
@click.option('--password', type=str, help='Your password.', prompt=True, hide_input=True,
              callback=validation.password)
@click.pass_context
def delete(ctx, username, password):
    click.confirm('This action can not be reversed. Are you sure?', abort=True)
    manager = ctx.obj['manager']
    manager.delete_user(username)
    click.echo(f'Success: Deleted the user with the username "{username}".')


def main():
    manager = PasswordManager()
    print(manager.check_user_existence_by_name('Christoph'))


if __name__ == '__main__':
    main()
