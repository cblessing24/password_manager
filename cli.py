import click
import pyperclip

import validation
from core import PasswordManager


help_texts = {
    'name': 'The name associated with the password.',
    'info': 'The info associated with the password.',
    'password': 'The password.',
    'new_password': 'The new password.',
    'master_password': 'Your master password.',
    'get_info': 'Copy the info instead of the password to the clipboard.'
}


def login_required(func):
    """Decorates a function to add the master password option."""
    return click.option(
        '--master_password',
        type=str,
        prompt=True,
        hide_input=True,
        expose_value=False,
        help=help_texts['master_password'],
        callback=validation.validate_master_password
    )(func)


@click.group()
@click.pass_context
def cli(ctx):
    """Manage your passwords."""
    ctx.obj = PasswordManager()


@cli.command()
@login_required
@click.option(
    '--name',
    type=str,
    prompt=True,
    help=help_texts['name'],
    callback=validation.validate_name
)
@click.option('--get_info', is_flag=True, help=help_texts['get_info'])
@click.pass_context
def get(ctx, name, get_info):
    """Get an existing password from the manager."""
    info, password = ctx.obj[name]
    if get_info:
        pyperclip.copy(info)
        click.echo('Info copied to clipboard.')
    else:
        pyperclip.copy(password)
        click.echo('Password copied to clipboard.')


@cli.command()
@login_required
@click.option(
    '--name',
    type=str,
    prompt=True,
    help=help_texts['name'],
    callback=validation.validate_new_name
)
@click.option('--info', type=str, prompt=True, help=help_texts['info'])
@click.option(
    '--password',
    type=str,
    prompt=True,
    hide_input=True,
    help=help_texts['password']
)
@click.pass_context
def new(ctx, name, info, password):
    """Add a new password to the manager."""
    ctx.obj.new(name, info, password)
    click.echo('New password added.')


@cli.command()
@login_required
@click.option(
    '--name',
    type=str,
    prompt=True,
    help=help_texts['name'],
    callback=validation.validate_name
)
@click.pass_context
def delete(ctx, name):
    """Delete an existing password from the manager."""
    del ctx.obj[name]
    click.echo('Password deleted.')


@cli.command('list')
@click.pass_context
def list_(ctx):
    """List all passwords in the password manager."""
    for name in ctx.obj:
        click.echo(name)


@cli.command()
@login_required
@click.pass_context
def reset(ctx):
    """Reset the password manager."""
    if click.confirm('Are you sure?'):
        ctx.obj.reset()
        click.echo('Reset successful.')
    else:
        click.echo('Aborted!')


@cli.command()
@login_required
@click.option(
    '--new_master_password',
    type=str,
    prompt=True,
    confirmation_prompt=True,
    help=help_texts['new_password'],
    hide_input=True
)
@click.pass_context
def change_password(ctx, new_master_password):
    """Change your master password."""
    ctx.obj.change_password(new_master_password)
    click.echo('Master password changed.')
