# UniRecords

UniRecords is the product name for the University Records Management System. It
is a three-layer Flask and PostgreSQL university records application for working
with university record data through a browser.

## What You Can Do

Use UniRecords to:

1. View dashboard metrics and charts.
2. Search, filter and page through student records.
3. View, create, edit and withdraw student records.
4. Read Courses, Modules, Enrolments and Grades.
5. Run eight reports with filters and result tables.
6. Check the local PostgreSQL connection from the browser.

## What Is Already Implemented

| Area | Current status |
| --- | --- |
| Dashboard | Database-backed metrics and distribution charts |
| Students | Search, filtering, pagination, detail, create, edit and withdrawal |
| Courses | Read-only university course catalogue |
| Modules | Read-only scheduled course offerings by academic term |
| Enrolments | Read-only student course registrations |
| Grades | Read-only assessment records |
| Reports | Eight report functions |
| Database health | Read-only PostgreSQL connection and schema check |

Student withdrawal is a lifecycle action, not a hard delete. The application
sets the student status to `Withdrawn` and preserves academic history.

## Start Here

For the complete beginner-friendly setup, use:

```text
docs/start-here.md
```

Short flow:

```text
Download or clone the repository
  -> install PostgreSQL and pgAdmin
  -> create use_records
  -> run the approved SQL scripts in order
  -> create and activate .venv
  -> install requirements
  -> copy .env.example to .env
  -> add local PostgreSQL credentials
  -> run python run.py
  -> open the exact URL printed in the terminal
```

Port `5000` is the default. If it is unavailable, `python run.py` selects the
next available local port and prints the correct URL.

## How UniRecords Works

The application is organised into three layers:

1. Routes receive web requests and render responses.
2. Services handle validation and business rules.
3. Repositories contain direct SQLAlchemy database access.

SQL is kept in repository classes. Routes do not query SQLAlchemy directly.

## Database And Data

The SQL files in `sql/postgresql/` create the database structure and sample data
used by UniRecords:

```text
sql/postgresql/
  01_create_use_full_schema_postgresql.sql
  02_insert_use_master_data_postgresql.sql
  03_insert_use_activity_records_postgresql.sql
  04_use_validation_queries_postgresql.sql
```

Expected local database structure:

```text
PostgreSQL 18
  -> database: use_records
  -> schema: use_record_management
  -> approved tables, views, procedures and sample data
```

The application does not create the database, run the approved SQL scripts or
use Alembic migrations to build the approved schema.

## Project Documentation

| Document | Purpose |
| --- | --- |
| `docs/README.md` | Suggested reading order for new developers and reviewers |
| `docs/start-here.md` | Install PostgreSQL, configure local settings, run UniRecords and verify it works |
| `docs/how-unirecords-works.md` | Browser flow, routes, services, repositories and PostgreSQL |
| `docs/database-and-data.md` | Database name, schema, approved SQL scripts, writes and report logic |
| `docs/assignment-requirements.md` | Assignment requirements mapped to implementation evidence |
| `docs/final-submission-checklist.md` | Testing, screenshots, video, security and final ZIP checks |

Planning references:

- Lucidchart database diagram:
  https://lucid.app/lucidchart/ad06d20a-3336-4adb-add4-77f31ad7f94c/edit?invitationId=inv_6f6bd50f-0f97-40bd-8323-8ab224c53b49&page=page1#
- Figma interface design:
  https://www.figma.com/design/9WqQOoMQ63DJAITQx6WDRU/University-Records-Database-Management-System?node-id=0-1&p=f&t=ZcNWLZ92BzlOmx4i-0

## Known Limitations

- Authentication is not implemented.
- Role-based application authorisation is not implemented.
- Non-student entities are read-only.
- PostgreSQL runs locally and must be recreated on each computer from the
  approved SQL scripts.
- Tests use the Flask testing configuration and an in-memory SQLite database;
  live PostgreSQL behaviour must be verified locally.

## Developer Quality Checks

```bash
ruff check .
black --check .
pytest --cov=app --cov-report=term-missing
```

Use `black .` to format Python files before re-running the checks.

## Project Structure

```text
app/
  repositories/
  routes/
  security/
  services/
  static/
  templates/
docs/
  README.md
  start-here.md
  how-unirecords-works.md
  database-and-data.md
  assignment-requirements.md
  final-submission-checklist.md
sql/
  postgresql/
tests/
.env.example
pyproject.toml
requirements.txt
run.py
wsgi.py
```

Important files:

- `pyproject.toml` contains project metadata, dependencies and tool settings.
- `requirements.txt` installs the project and development dependencies.
- `.env.example` is a safe local configuration template.
- `run.py` starts the local development server.
- `wsgi.py` exposes the deployment entry point.
