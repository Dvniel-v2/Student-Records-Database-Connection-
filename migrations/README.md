# Migrations

This directory is configured for Flask-Migrate and Alembic.

Common commands:

```bash
flask db migrate -m "describe schema change"
flask db upgrade
flask db downgrade
```

For simple local setup without a migration history, use the explicit Flask command:

```bash
flask init-db
```
