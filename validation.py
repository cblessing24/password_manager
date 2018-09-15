import click


def validate_master_password(ctx, _param, value):
    if not ctx.obj.user_exists:
        repeated_master_password = click.prompt(
            'Repeat for confirmation', type=str, hide_input=True)
        if repeated_master_password != value:
            ctx.fail('The two passwords do not match.')
    if not ctx.obj.authenticate(value):
        ctx.fail('Incorrect password.')
