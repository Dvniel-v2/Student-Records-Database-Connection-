# PostgreSQL Migration

These files are the approved PostgreSQL implementation scripts for the
University Record Management System.

The earlier MySQL database was converted into a PostgreSQL schema named
`use_record_management`. The schema is created inside the PostgreSQL database
that you are already connected to. The local database name can vary, but the
application and validation queries expect the `use_record_management` schema.

## Execution Order

Run the files in this order from pgAdmin Query Tool or `psql`:

1. `01_create_use_full_schema_postgresql.sql`
2. `02_insert_use_master_data_postgresql.sql`
3. `03_insert_use_activity_records_postgresql.sql`
4. `04_use_validation_queries_postgresql.sql`

## Notes

File 01 drops and recreates the `use_record_management` schema. Do not run it
against a database that contains work you need to keep.

The schema file uses PostgreSQL features including identity columns, check
constraints, views, trigger functions, stored procedures, roles and grants. It
also creates `pgcrypto` if the connected user has permission.

If your PostgreSQL user cannot create extensions, roles or grants, run the
remaining schema statements after commenting out the permission-specific section.

These SQL files are the source of truth for the approved database baseline.
Flask `db.create_all()` and Alembic autogeneration are not currently used to
create this 46-table schema.
