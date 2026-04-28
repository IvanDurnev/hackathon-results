from logging.config import fileConfig

from alembic import context
from flask import current_app

from app import create_app
from app.extensions import db

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

try:
    flask_app = current_app._get_current_object()
except RuntimeError:
    flask_app = create_app()

with flask_app.app_context():
    target_metadata = db.metadata

    def get_url():
        return str(flask_app.config["SQLALCHEMY_DATABASE_URI"]).replace("%", "%%")

    def run_migrations_offline():
        context.configure(
            url=get_url(),
            target_metadata=target_metadata,
            literal_binds=True,
            dialect_opts={"paramstyle": "named"},
        )

        with context.begin_transaction():
            context.run_migrations()

    def run_migrations_online():
        connectable = db.engine

        with connectable.connect() as connection:
            context.configure(connection=connection, target_metadata=target_metadata)

            with context.begin_transaction():
                context.run_migrations()

    if context.is_offline_mode():
        run_migrations_offline()
    else:
        run_migrations_online()
