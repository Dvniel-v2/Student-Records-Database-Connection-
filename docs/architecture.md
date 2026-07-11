# Architecture

The application follows a three-layer structure for the Student Records domain.

## Presentation Layer

Flask routes in `app/routes/main.py` receive HTTP requests and render templates.
Templates display the Student Directory and Student Detail pages. Static CSS and
JavaScript stay in `app/static`.

Routes do not query SQLAlchemy directly. They call `ApprovedStudentService` and
translate unavailable database reads into safe user-facing messages.

## Service Layer

`app/services/approved_student_service.py` owns the approved read-only Student
application boundary. It validates route input where needed and returns clean
Student records from the repository.

## Repository Layer

`app/repositories/approved_student_repository.py` performs direct approved
Student database reads. It queries the schema-qualified
`use_record_management.vw_student_directory_masked` view through SQLAlchemy and
psycopg.

## Data Flow

1. A user opens the Student Directory or a Student Detail page.
2. The route calls `ApprovedStudentService`.
3. The service calls `ApprovedStudentRepository`.
4. The repository reads from `use_record_management.vw_student_directory_masked`.
5. The route renders the read-only Student interface.

PostgreSQL is the sole supported implementation database. Unit tests do not
perform formal live PostgreSQL validation.

## Entry Points And Configuration

`run.py` is the local development entry point and creates the app with the
development configuration.

`wsgi.py` is the deployment entry point and creates the app with the production
configuration.

The production configuration currently sets `DEBUG = False`. Further production
hardening should be added before a real deployment.

## Schema Management

The approved database baseline is the PostgreSQL `use_record_management` schema
in `sql/postgresql/`. Flask Migrate and Alembic remain as scaffolded tooling,
but they are not currently the source of truth for the approved 46-table schema.

The simplified Student prototype model, repository, service, write templates and
seed script have been removed from the supported application path.

The `/health/database` endpoint checks database connectivity, schema presence
and whether the approved `student` table can be queried. It does not create or
change database objects.
