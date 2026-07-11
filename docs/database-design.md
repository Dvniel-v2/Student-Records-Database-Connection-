# Database Design

The approved implementation database is the PostgreSQL
`use_record_management` schema in `sql/postgresql/`.

PostgreSQL is the only supported implementation database. The SQL scripts in
`sql/postgresql` are the approved database source of truth.

The active Student interface reads from the approved masked view:

```text
use_record_management.vw_student_directory_masked
```

The underlying approved Student structure is normalised across tables including
`person`, `student` and `programme`.

## Write Responsibilities

Student create, edit and delete workflows are future work. They should only be
implemented after transaction-safe workflows are designed for the normalised
PostgreSQL schema.

## PostgreSQL and pgAdmin

Local development uses PostgreSQL through SQLAlchemy and psycopg. The database
name can vary locally, but the application expects the approved
`use_record_management` schema.

Run the approved scripts in this order:

1. `01_create_use_full_schema_postgresql.sql`
2. `02_insert_use_master_data_postgresql.sql`
3. `03_insert_use_activity_records_postgresql.sql`
4. `04_use_validation_queries_postgresql.sql`

pgAdmin is useful for inspecting tables, views, trigger functions, procedures
and validation query results.

Do not run Flask `db.create_all()` against the approved PostgreSQL database.
The SQL scripts are the current database baseline.

## Planned Entities

The interface includes placeholders for Courses, Modules, Enrolments, Grades and
Reports. The approved PostgreSQL database already contains normalised tables for
these areas, but the Flask application has not yet connected those screens to
dedicated repositories, services, routes and tests.
