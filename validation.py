import click


def new_username(ctx, _param, value):
    user_db = ctx.obj['user_db']
    while True:
        if not user_db.check_user_existence_by_name(value):
            break
        click.echo(f'Error: A user with the username "{value}" already exists. Please choose a different name.')
        value = click.prompt('Username', type=str)
    return value
