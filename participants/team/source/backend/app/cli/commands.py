import click
from flask import Flask

from app.extensions import db
from app.modules.auth.models import User
from app.modules.auth.services import create_user, ensure_default_roles, normalize_email


def register_commands(app: Flask) -> None:
    @app.cli.command("ensure-roles")
    def ensure_roles_command():
        ensure_default_roles()
        db.session.commit()
        click.echo("Default roles are ready.")

    @app.cli.command("create-admin")
    @click.option("--email", prompt=True)
    @click.option("--username", prompt=True)
    @click.option("--password", prompt=True, hide_input=True, confirmation_prompt=True)
    def create_admin_command(email: str, username: str, password: str):
        create_user(email=email, username=username, password=password, is_admin=True)
        click.echo(f"Admin user created: {email}")

    @app.cli.command("ensure-admin")
    @click.option("--email", envvar="ADMIN_EMAIL", prompt=True)
    @click.option("--username", envvar="ADMIN_USERNAME", default="admin", show_default=True)
    @click.option("--password", envvar="ADMIN_PASSWORD", prompt=True, hide_input=True)
    def ensure_admin_command(email: str, username: str, password: str):
        normalized_email = normalize_email(email)
        roles = ensure_default_roles()
        user = User.query.filter_by(email=normalized_email).first()

        if user is None:
            create_user(email=normalized_email, username=username, password=password, is_admin=True)
            click.echo(f"Admin user created: {normalized_email}")
            return

        user.active = True
        user.add_role(roles["admin"])
        db.session.commit()
        click.echo(f"Admin user is ready: {normalized_email}")
