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
@click.option('--get_info', is_flag=True)
@click.pass_context
def get(ctx, name, get_info):
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
@click.option('--name', type=str, prompt=True)
@click.option('--info', type=str, prompt=True)
@click.option('--password', type=str, prompt=True, hide_input=True)
@click.pass_context
def new(ctx, name, info, password):
    if name in ctx.obj:
        ctx.fail(f'A password with the name "{name}" already exists.')
    ctx.obj.new(name, info, password)
    click.echo('New password added.')


@cli.command()
@click.option('--name', type=str, prompt=True)
@click.pass_context
def delete(ctx, name):
    if name not in ctx.obj:
        ctx.fail(f'A password with the name "{name}" does not exist.')
    ctx.obj.delete(name)
    click.echo('Password deleted.')
