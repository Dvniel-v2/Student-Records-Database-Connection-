# Student Records Database Connection

This project is a Flask web application for managing student records in a
university database. It uses PostgreSQL for data storage, SQLAlchemy for database
access, and a Bootstrap based interface inspired by the linked Figma design.
It is the first functional stage of a Student Records Management System. The
interface branding uses the name UniRecords.

The approved implementation database is the PostgreSQL
`use_record_management` schema supplied in `sql/postgresql/`.

PostgreSQL is the only supported implementation database. The SQL scripts in
`sql/postgresql` are the approved database source of truth.

The code is organised into three clear layers:

1. Routes handle web requests and render pages.
2. Services hold validation and business rules.
3. Repositories handle direct database access.

## Design And Planning Links

Lucidchart database diagram:
https://lucid.app/lucidchart/ad06d20a-3336-4adb-add4-77f31ad7f94c/edit?invitationId=inv_6f6bd50f-0f97-40bd-8323-8ab224c53b49&page=page1#

Figma interface design:
https://www.figma.com/design/9WqQOoMQ63DJAITQx6WDRU/University-Records-Database-Management-System?node-id=0-1&p=f&t=ZcNWLZ92BzlOmx4i-0

## What The App Does

The current app lets an administrator view approved Student directory records
from PostgreSQL.

The active Student read path is:

```text
use_records
  -> use_record_management
  -> vw_student_directory_masked
  -> ApprovedStudentRepository
  -> ApprovedStudentService
  -> Flask routes
  -> Student Directory and Student Detail pages
```

Student create, edit and delete operations are not yet available for the
normalised PostgreSQL schema.

## Current Development Status

The project is currently being developed in stages.

The Student section is the first functional part of the university records
management system. It currently supports read-only Student list and detail pages
through the approved PostgreSQL Student directory view.

Some interface elements are included as design placeholders to demonstrate the
intended direction of the complete system. These currently include:

1. Courses
2. Modules
3. Enrolments
4. Grades
5. Reports
6. Dashboard statistics
7. Global search
8. Notifications
9. Help controls

These placeholder elements are not intended to represent completed
functionality. They provide a visual structure for future development and show
how additional university record entities may be incorporated into the
interface.

As development continues, these areas will be connected to their own database
models, service logic, repository functions, routes and tests.

The approved PostgreSQL database separates Student data across normalised tables
including `person`, `student` and `programme`. The interface should not be read
as evidence that every planned feature is already functional.

## Main Technologies

1. Flask
2. Jinja templates
3. Bootstrap
4. Flask SQLAlchemy
5. Flask Migrate and Alembic
6. PostgreSQL
7. psycopg
8. pytest
9. Ruff
10. Black

## Project Structure

```text
app/
  models/
  repositories/
  routes/
  services/
  static/
  templates/
docs/
logs/
migrations/
sql/
  postgresql/
tests/
.env.example
pyproject.toml
requirements.txt
run.py
wsgi.py
```

## Important Files

`pyproject.toml` contains the project metadata, dependencies and tool settings
for Black, Ruff and pytest.

`requirements.txt` is the single install file. It points to the dependencies in
`pyproject.toml`.

`.env.example` shows the environment variables needed to run the app. Keep real
passwords and secrets in a local `.env` file. The local `.env` file is ignored by
Git.

`run.py` is the local development entry point. `wsgi.py` is the deployment
server entry point.

`logs/` is reserved for local runtime logs if file logging is added later. The
application does not currently configure file logging. Log files are ignored by
Git.

## Setup

For complete local installation and assessor setup instructions, see:

```text
docs/assessor-setup.md
```

Create a virtual environment:

```powershell
py -3.11 -m venv .venv
```

Activate it in Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

Install the project dependencies:

```bash
pip install -r requirements.txt
```

Create your local environment file:

```powershell
Copy-Item .env.example .env
```

Then update `.env` if your PostgreSQL username, password or port is different.
The `.env` file is local only and excluded from Git. Real passwords must never
be committed.

Example values:

```env
FLASK_APP=run.py
SECRET_KEY=replace-with-a-secure-local-key
DATABASE_URL=postgresql+psycopg://postgres:YOUR_LOCAL_PASSWORD@localhost:5432/use_records
```

## PostgreSQL Setup

Create a local PostgreSQL database. The database name may be local to your
machine, but the supplied SQL creates and uses the `use_record_management`
schema inside that database.

```sql
CREATE DATABASE use_records;
```

Run the approved SQL scripts in this order from pgAdmin Query Tool or `psql`:

1. `sql/postgresql/01_create_use_full_schema_postgresql.sql`
2. `sql/postgresql/02_insert_use_master_data_postgresql.sql`
3. `sql/postgresql/03_insert_use_activity_records_postgresql.sql`
4. `sql/postgresql/04_use_validation_queries_postgresql.sql`

File 01 drops and recreates the `use_record_management` schema. Do not run it
against a database that contains work you need to keep.

The PostgreSQL scripts are the current source of truth for the approved
database. The application must not be configured to use MySQL.

After the scripts have been run, Flask reads Student records from:

```text
use_records -> use_record_management -> vw_student_directory_masked
```

The application does not create the database, create the approved schema or run
the SQL scripts automatically.

## Database Migrations

The repository includes a Flask Migrate and Alembic scaffold, but it is not the
source of truth for the approved 46-table PostgreSQL schema. The approved schema
is created by the SQL files in `sql/postgresql/`.

Do not run `db.create_all()` or generate Alembic revisions to create the
approved PostgreSQL database.

Migration commands may be used later after the model strategy has been updated
deliberately:

```bash
flask db migrate -m "describe the change"
flask db upgrade
```

## Database Health Check

The application includes a read-only database health endpoint:

```text
/health/database
```

It checks that SQLAlchemy can connect, that the `use_record_management` schema
exists, and that the approved `student` table can be queried. It does not create
or modify database objects.

## Run The App

For local development, use:

```powershell
.\.venv\Scripts\Activate.ps1
python run.py
```

Open the app at:

```text
http://127.0.0.1:5000/
```

Deployment servers should import `app` from `wsgi.py`, which uses the production
configuration class.

## Quality Checks

Run linting:

```bash
ruff check .
```

Check formatting:

```bash
black --check .
```

Run tests with coverage:

```bash
pytest --cov=app --cov-report=term-missing
```

Format the code:

```bash
black .
```

## Testing Notes

Tests use the Flask testing configuration and an in memory SQLite database. They
do not prove PostgreSQL views, triggers, stored procedures or schema-specific
constraints.

Formal PostgreSQL validation belongs to the database/testing responsibility.
Before expecting live Student records in the app, confirm locally that
PostgreSQL is running, `.env` contains the correct `DATABASE_URL`, `use_records`
exists, `use_record_management` exists, and
`vw_student_directory_masked` can be queried.
