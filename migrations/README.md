# Migrations

This directory contains the Flask-Migrate and Alembic scaffold. Migrations are
the intended source of truth for tracked schema changes once revision files are
created.

No migration revision is currently committed for the Student model.

Common commands:

```bash
flask db migrate -m "describe schema change"
flask db upgrade
flask db downgrade
```

For simple local setup without a migration history, use the explicit Flask
command:

```bash
flask init-db
```
