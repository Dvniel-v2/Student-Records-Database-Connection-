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

Student create and edit workflows write to the approved normalised tables:

```text
person
student
person_contact
```

The Student Directory continues to read from
`vw_student_directory_masked`. The application does not write to this view.

The approved schema does not include an `Archived` Student status or a Student
delete procedure. The frontend therefore uses a withdrawal lifecycle action:

```text
student.student_status = 'Withdrawn'
student.graduation_status = 'Not eligible'
```

This preserves enrolments, grades and other related academic records.

The schema includes approved procedures for enrolment and grade workflows, but
not for Student create or update. Student writes are implemented in the Flask
repository layer with parameterised SQL and SQLAlchemy transactions.

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

The interface includes read-only pages for Courses, Modules, Enrolments, Grades
and Reports. Future development may add write workflows for those entities once
their transaction rules are defined.
