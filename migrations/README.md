# Migrations

This directory contains the Flask-Migrate and Alembic scaffold. Migrations are
available for future tracked schema changes once the Flask model strategy has
been deliberately aligned with the approved database.

No migration revision is currently committed for the Student model.

The approved database baseline is currently created from the SQL scripts in
`sql/postgresql/`, not from Alembic autogeneration.

Common commands:

```bash
flask db migrate -m "describe schema change"
flask db upgrade
flask db downgrade
```

Do not generate migrations from the current simplified Student model against the
approved `use_record_management` schema.
