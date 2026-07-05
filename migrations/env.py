"""Alembic environment configured for Flask-Migrate."""

from __future__ import annotations

from logging.config import fileConfig

from alembic import context
from flask import current_app

config = context.config

fileConfig(config.config_file_name)
target_metadata = current_app.extensions["migrate"].db.metadata


def get_engine():
    """Return the SQLAlchemy engine from the current Flask app."""
    try:
        return current_app.extensions["migrate"].db.get_engine()
    except TypeError:
        return current_app.extensions["migrate"].db.engine


def get_engine_url() -> str:
    """Return a URL string with passwords hidden."""
    return str(get_engine().url).replace("%", "%%")


config.set_main_option("sqlalchemy.url", get_engine_url())


def run_migrations_offline() -> None:
    """Run migrations without a live database connection."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        compare_type=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations with a live database connection."""

    def process_revision_directives(context, revision, directives):
        if getattr(config.cmd_opts, "autogenerate", False):
            script = directives[0]
            if script.upgrade_ops.is_empty():
                directives[:] = []

    connectable = get_engine()

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            process_revision_directives=process_revision_directives,
            compare_type=True,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
