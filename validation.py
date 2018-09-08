import click


def new_username(ctx, param, value):
    manager = ctx.obj['manager']
    while True:
        if not manager.check_user_existence_by_name(value):
            break
        click.echo(f'Error: A user with the username "{value}" already exists. Please choose a different name.')
        value = click.prompt(param.prompt, type=str)
    return value


def username(ctx, param, value):
    manager = ctx.obj['manager']
    while True:
        if manager.check_user_existence_by_name(value):
            break
        click.echo(f'Error: A user with the username "{value}" does not exist. Please choose a different name.')
        value = click.prompt(param.prompt , type=str)
    return value


def password(ctx, param, value):
    manager = ctx.obj['manager']
    username = ctx.params['username']
    while True:
        if manager.authenticate_user(username, value):
            break
        click.echo(f'Error: Incorrect password. Please try again.')
        value = click.prompt(param.prompt, type=str, hide_input=True)
    return value


def new_password(ctx, param, value):
    while True:
        if value == ctx.params['old_password']:
            click.echo('Error: Your new password must be different from your old one.')
            value = click.prompt(param.prompt, type=str, hide_input=True)
        else:
            repeated_value = click.prompt('Repeat for confirmation', type=str, hide_input=True)
            if value != repeated_value:
                click.echo('Error: The two entered passwords do not match.')
                value = click.prompt(param.prompt, type=str, hide_input=True)
            else:
                break
    return value


