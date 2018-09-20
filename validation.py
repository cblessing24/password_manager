import click


def validate_master_password(ctx, _param, value):
    """Validates the master password."""
    if not ctx.obj.user_exists:
        # Confirm master password if we want to create a new user.
        repeated_master_password = click.prompt(
            'Repeat for confirmation', type=str, hide_input=True)
        if repeated_master_password != value:
            ctx.fail('The two passwords do not match.')
    ctx.obj.authenticate(value)
    if not ctx.obj.authenticated:
        ctx.fail('Incorrect password.')


def validate_name(ctx, _param, value):
    """Validates the name for a password."""
    if value not in ctx.obj:
        ctx.fail(f'A password with the name "{value}" does not exist.')
    return value


def validate_new_name(ctx, _param, value):
    """Validates a new name for a new password."""
    if value in ctx.obj:
        ctx.fail(f'A password with the name "{value}" already exists.')
    return value
