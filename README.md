# Student Records Database Connection

This project is a Flask web application for managing student records in a
university database. It uses PostgreSQL for data storage, SQLAlchemy for database
access, and a Bootstrap based interface inspired by the linked Figma design.
It is the first functional stage of a Student Records Management System. The
interface branding uses the name UniRecords.

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

The current app lets an administrator create, view, edit and delete student
records. Each student record stores:

1. Student number
2. First name
3. Last name
4. Email address
5. Course
6. Enrolment date

The interface includes a dashboard layout, student record table, quick action
cards, student forms, detail pages and delete confirmation.

## Current Development Status

The project is currently being developed in stages.

The Student section is the first functional part of the university records
management system. It currently supports creating, viewing, editing and deleting
student records through the Flask application and database connection.

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
scripts/
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

```bash
copy .env.example .env
```

Then update `.env` if your PostgreSQL username, password or port is different.

Example values:

```env
FLASK_APP=run.py
SECRET_KEY=replace-with-a-secure-key
DATABASE_URL=postgresql+psycopg://postgres:password@localhost:5432/student_records
```

## PostgreSQL Setup

Create the development database in PostgreSQL:

```sql
CREATE DATABASE student_records;
```

pgAdmin can be used to inspect tables and records during development. Schema
changes should be handled through migrations.

## Database Migrations

The repository includes a Flask Migrate and Alembic scaffold. Migrations are the
preferred method for tracked schema changes once revision files are created.

Create a migration after changing models:

```bash
flask db migrate -m "describe the change"
```

Apply migrations:

```bash
flask db upgrade
```

For quick local setup, you can create the tables directly:

```bash
flask init-db
```

`flask init-db` is a convenience command for simple local setup. It is not a
replacement for tracked migrations.

## Run The App

For local development, use:

```bash
python run.py
```

Open the app at:

```text
http://127.0.0.1:5000/
```

Deployment servers should import `app` from `wsgi.py`, which uses the production
configuration class.

## Seed Sample Data

After the tables exist, add realistic student records:

```bash
python scripts/seed_database.py
```

The seed script avoids duplicate student numbers and email addresses.

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
do not connect to the development PostgreSQL database.
