import click

import validation
from classes import PasswordManager


def login_required(func):
    func = click.option('--password', type=str, help='Your password.', prompt=True, hide_input=True,
                        callback=validation.validate_password, expose_value=False)(func)
    func = click.option('--username', type=str, help='Your username.', prompt=True,
                        callback=validation.validate_username, expose_value=False)(func)
    return func


@click.group()
@click.pass_context
def cli(ctx):
    """A basic password manager."""
    manager = PasswordManager()
    ctx.obj = {'manager': manager}


@cli.command()
@click.option('--username', type=str, help='Username for the new account.', prompt=True,
              callback=validation.validate_new_username)
@click.option('--password', type=str, help='Password for the new account.', prompt=True,
              hide_input=True, confirmation_prompt=True)
@click.pass_context
def new(ctx, username, password):
    """Create a new account."""
    manager = ctx.obj['manager']
    manager.create_user(username, password)
    click.echo(f'Success: Created a new account with the username "{username}".')


@cli.group()
@click.pass_context
def account(_ctx):
    """Manage your account."""
    pass


@account.command()
@login_required
@click.option('--new_password', type=str, help='Your new password.', prompt=True, hide_input=True,
              callback=validation.validate_new_password)
@click.pass_context
def change_password(ctx, new_password):
    """Change the password of your account."""
    ctx.obj['manager'].change_user_password(ctx.obj['username'], ctx.obj['password'], new_password)
    click.echo('Success: Your password has been changed.')


@account.command()
@login_required
@click.pass_context
def delete(ctx):
    """Delete your account."""
    click.confirm('This action can not be reversed. Are you sure?', abort=True)
    username = ctx.obj['username']
    ctx.obj['manager'].delete_user(username)
    click.echo('Success: Your account has been deleted.".')


def main():
    manager = PasswordManager()
    print(manager.check_user_existence_by_name('Christoph'))


if __name__ == '__main__':
    main()
