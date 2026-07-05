# Student Records Database Connection

A Flask application for managing student enrolment records with a clear
presentation, service, and repository architecture backed by PostgreSQL.

## Stack

- Flask and Jinja templates
- Flask-SQLAlchemy
- Flask-Migrate and Alembic
- PostgreSQL with psycopg
- Faker seed data
- pytest, pytest-cov, Ruff, and Black

## Project Structure

```text
app/
  models/student.py
  repositories/student_repository.py
  routes/main.py
  services/student_service.py
  static/css/style.css
  static/js/main.js
  templates/
docs/
migrations/
scripts/seed_database.py
tests/
```

## Setup

Create and activate a virtual environment:

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Install dependencies:

```bash
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

Create `.env` from `.env.example` and update credentials if needed:

```env
FLASK_APP=run.py
FLASK_ENV=development
SECRET_KEY=replace-with-a-secure-key
DATABASE_URL=postgresql+psycopg://postgres:password@localhost:5432/student_records
```

## PostgreSQL

Create the development database:

```sql
CREATE DATABASE student_records;
```

pgAdmin can be used to inspect the `students` table and run local
administration tasks, but schema changes should go through migrations.

## Migrations

Create and apply migrations with Flask-Migrate:

```bash
flask db migrate -m "create students table"
flask db upgrade
```

For quick local setup without a migration history, create tables explicitly:

```bash
flask init-db
```

## Run

```bash
python run.py
```

The app runs at `http://127.0.0.1:5000/`.

## Seed Data

After tables exist, seed realistic student records:

```bash
python scripts/seed_database.py
```

The script avoids duplicate student numbers and email addresses.

## Quality Checks

```bash
ruff check .
black --check .
pytest --cov=app --cov-report=term-missing
```

Format code with:

```bash
black .
```

## Testing

Tests use the Flask testing configuration and an in-memory SQLite database.
They do not connect to the development PostgreSQL database.
