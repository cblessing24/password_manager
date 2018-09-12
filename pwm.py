import click
import pyperclip

from classes import PasswordManager


@click.group()
@click.option('--master_password', type=str, prompt=True, hide_input=True)
@click.pass_context
def cli(ctx, master_password):
    ctx.obj = PasswordManager()
    if not ctx.obj.user_exists:
        repeated_master_password = click.prompt(
            'Repeat for confirmation', type=str, hide_input=True)
        if repeated_master_password != master_password:
            ctx.fail('The two passwords do not match.')
    if not ctx.obj.authenticate(master_password):
        ctx.fail('Incorrect password.')


@cli.command()
@click.option('--name', type=str, prompt=True)
@click.pass_context
def get(ctx, name):
    if name not in ctx.obj:
        ctx.fail(f'A password with the name "{name}" does not exist.')
    info, password = ctx.obj.get(name)
    pyperclip.copy(password)
    click.echo('Password copied to clipboard.')


@cli.command()
@click.option('--name', type=str, prompt=True)
@click.option('--info', type=str, prompt=True)
@click.option('--password', type=str, prompt=True)
@click.pass_context
def new(ctx, name, info, password):
    ctx.obj.new(name, info, password)


@cli.command()
@click.option('--name', type=str, prompt=True)
@click.pass_context
def delete(ctx, name):
    ctx.obj.delete(name)
