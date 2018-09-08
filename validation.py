import click


def validate_new_username(ctx, param, value):
    manager = ctx.obj['manager']
    while True:
        if not manager.check_user_existence_by_name(value):
            break
        click.echo(f'Error: A user with the username "{value}" already exists. Please choose a different name.')
        value = click.prompt(param.prompt, type=str)
    return value


def validate_new_password(ctx, param, value):
    while True:
        if value == ctx.obj['password']:
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


def validate_username(ctx, param, value):
    while True:
        if ctx.obj['manager'].check_user_existence_by_name(value):
            break
        click.echo(f'Error: A user with the username "{value}" does not exist.')
        value = click.prompt(param.prompt, type=str)
    ctx.obj['username'] = value


def validate_password(ctx, param, value):
    username = ctx.obj['username']
    while True:
        if ctx.obj['manager'].authenticate_user(username, value):
            break
        click.echo(f'Error: Invalid password for user "{username}".')
        value = click.prompt(param.prompt, type=str, hide_input=True)
    ctx.obj['password'] = value