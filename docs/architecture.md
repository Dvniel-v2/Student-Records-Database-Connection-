# Architecture

The application follows a three-layer structure for the Student Records domain.

## Presentation Layer

Flask routes in `app/routes/main.py` receive HTTP requests and render templates.
Templates display student fields, create and edit forms, detail pages, and delete
confirmation screens. Static CSS and JavaScript stay in `app/static`.

Routes do not query SQLAlchemy directly and do not contain business validation.
They collect form data, call `StudentService`, and translate validation or
database errors into user-friendly flash messages.

## Service Layer

`app/services/student_service.py` owns business rules for students:

- required fields
- email format
- unique student number
- unique email address
- sensible first and last name lengths
- valid enrolment dates

The service commits successful changes and rolls back failed database writes.

## Repository Layer

`app/repositories/student_repository.py` is the only layer that performs direct
database access. It supports student creation, listing, lookup by ID, lookup by
student number, update, delete, and email lookup for validation.

## Data Flow

1. A user submits a form or opens a student page.
2. The route calls `StudentService`.
3. The service validates data and calls `StudentRepository`.
4. The repository reads or writes SQLAlchemy models.
5. The route renders a response with success or error messaging.

PostgreSQL is the development and production database target. Tests use SQLite
in memory through the testing configuration so unit test runs stay isolated.

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

The legacy simplified `Student` model supports the current CRUD slice only. It
must not be used to create a second standalone `students` table in the approved
PostgreSQL schema.

The `/health/database` endpoint checks database connectivity, schema presence
and whether the approved `student` table can be queried. It does not create or
change database objects.
