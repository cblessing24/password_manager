import click
import pyperclip

from classes import PasswordManager


help_texts = {
    'name': 'The name associated with the password.',
    'info': 'The info associated with the password.',
    'password': 'The password.',
    'get_info': 'Copy the info instead of the password to the clipboard.'
}


@click.group()
@click.pass_context
@click.option('--master_password', type=str, prompt=True, hide_input=True)
def cli(ctx, master_password):
    """Manage your passwords."""
    ctx.obj = PasswordManager()
    if not ctx.obj.user_exists:
        repeated_master_password = click.prompt(
            'Repeat for confirmation', type=str, hide_input=True)
        if repeated_master_password != master_password:
            ctx.fail('The two passwords do not match.')
    if not ctx.obj.authenticate(master_password):
        ctx.fail('Incorrect password.')


@cli.command()
@click.option('--name', type=str, prompt=True, help=help_texts['name'])
@click.option('--get_info', is_flag=True, help=help_texts['get_info'])
@click.pass_context
def get(ctx, name, get_info):
    """Get an existing password from the manager."""
    if name not in ctx.obj:
        ctx.fail(f'A password with the name "{name}" does not exist.')
    info, password = ctx.obj.get(name)
    if get_info:
        pyperclip.copy(info)
        click.echo('Info copied to clipboard.')
    else:
        pyperclip.copy(password)
        click.echo('Password copied to clipboard.')


@cli.command()
@click.option('--name', type=str, prompt=True, help=help_texts['name'])
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
    if name in ctx.obj:
        ctx.fail(f'A password with the name "{name}" already exists.')
    ctx.obj.new(name, info, password)
    click.echo('New password added.')


@cli.command()
@click.option('--name', type=str, prompt=True, help=help_texts['name'])
@click.pass_context
def delete(ctx, name):
    """Delete an existing password from the manager."""
    if name not in ctx.obj:
        ctx.fail(f'A password with the name "{name}" does not exist.')
    ctx.obj.delete(name)
    click.echo('Password deleted.')


@cli.command('list')
@click.pass_context
def list_(ctx):
    """List all passwords in the password manager."""
    for name in ctx.obj:
        click.echo(name)


@cli.command()
@click.pass_context
def reset(ctx):
    """Reset the password manager."""
    if click.confirm('Are you sure?'):
        ctx.obj.reset()
        click.echo('Reset successful.')
    else:
        click.echo('Aborted!')
