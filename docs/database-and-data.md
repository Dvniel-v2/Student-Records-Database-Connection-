# Database And Data

The approved implementation database is the PostgreSQL
`use_record_management` schema in `sql/postgresql/`.

PostgreSQL is the only supported implementation database. The SQL files in
`sql/postgresql` create the database structure and sample data used by
UniRecords.

The active student interface reads from the approved masked view:

```text
use_record_management.vw_student_directory_masked
```

The underlying approved student structure is normalised across tables including
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

## PostgreSQL And pgAdmin

Local development uses PostgreSQL 18 through SQLAlchemy and psycopg. The database
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

## Modules / Course Offerings

The Modules page displays scheduled course offerings by academic term. The page
uses the module wording expected by the interface while reading the approved
`course_offering`, `course` and `academic_term` tables.

## Reports

The application implements eight database-backed report functions:

1. Students registered on a selected course taught by a selected lecturer.
2. Final-year students with an average overall grade above a threshold.
3. Active students with no registration in the current approved term.
4. Academic adviser lookup for a selected student.
5. Lecturers by expertise area.
6. Staff by department or administrative unit.
7. Research project summary.
8. Programme credit summary.

Reports use approved tables and views such as `enrolment`, `course_offering`,
`offering_lecturer`, `advisor_assignment`, `lecturer_expertise`,
`non_academic_staff` and `vw_programme_credit_summary`.

The Research Project Summary report uses parameterised repository SQL with
separate aggregated common table expressions for funding, members, publications
and outcomes. This avoids multiplying totals across one-to-many joins.
