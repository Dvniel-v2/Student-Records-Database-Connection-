# How UniRecords Works

UniRecords follows a three-layer structure for University Records.

## Browser And Presentation Layer

Flask routes in `app/routes/main.py` receive HTTP requests and render templates.
Templates display the dashboard, Student Directory, Student Detail, student
write pages, read-only academic records and reports. Static CSS and JavaScript
stay in `app/static`.

Routes do not query SQLAlchemy directly. They call `ApprovedStudentService` and
`StudentWriteService`, then translate unavailable database operations into safe
user-facing messages.

## Service Layer

`app/services/approved_student_service.py` validates requests and prepares
student data for the interface.

`app/services/student_write_service.py` validates student creation, editing and
withdrawal. It normalises form values, checks duplicate student numbers and
email addresses, validates schema-limited status values and translates database
errors into safe messages.

## Repository Layer

`app/repositories/approved_student_repository.py` reads student records from the
schema-qualified `use_record_management.vw_student_directory_masked` view
through SQLAlchemy and psycopg.

`app/repositories/student_write_repository.py` writes student records with
parameterised SQL. It writes to `person`, `student` and primary
`person_contact` records. Multi-table create and update operations commit only
after all related records succeed and roll back on failure.

`app/services/assignment_report_service.py` and
`app/repositories/assignment_report_repository.py` implement the report pages.
The service validates report filters and the repository keeps all SQL in the
data layer.

## Data Flow

1. A user opens the Student Directory or a Student Detail page.
2. The route calls `ApprovedStudentService`.
3. The service calls `ApprovedStudentRepository`.
4. The repository reads from `use_record_management.vw_student_directory_masked`.
5. The route renders the student interface.

## Student Write Flow

1. A user opens the Add, Edit or Withdraw Student page.
2. The route validates the CSRF token for POST requests.
3. The route passes form data to `StudentWriteService`.
4. The service validates and normalises the submitted values.
5. The repository writes to `person`, `student` and primary `person_contact`
   records using parameterised SQL.
6. The repository commits the transaction or rolls it back on failure.
7. The route redirects to the Student Detail page or re-renders the form with
   field-level errors.

The approved schema does not define an `Archived` student status or a student
delete procedure. The frontend therefore uses Withdraw Student, which sets
`student.student_status` to `Withdrawn` and preserves academic history.

## Report Query Flow

1. A user opens `/reports`.
2. The route displays the report catalogue from `AssignmentReportService`.
3. A user opens a report and submits filters.
4. The service validates the filters.
5. The repository runs parameterised SQL against approved tables or views.
6. The template displays result counts, empty states and responsive tables.

The current reporting term for the no-registration report is determined from
the academic-term data.

PostgreSQL is the sole supported implementation database. Unit tests do not
perform formal live PostgreSQL validation.

## Entry Points And Configuration

`run.py` is the local entry point and creates the app with the development
configuration.

`wsgi.py` is the deployment entry point and creates the app with the production
configuration.

The production configuration currently sets `DEBUG = False`. Further production
hardening should be added before a real deployment.

## Schema Management

The SQL files in `sql/postgresql/` create the PostgreSQL
`use_record_management` schema. Flask connects to that schema through SQLAlchemy
and repositories read or update its objects.

Alembic migrations are not used in this project because the approved SQL package
is the source of truth.

The `/health/database` endpoint checks database connectivity, schema presence
and whether the approved `student` table can be queried. It does not create or
change database objects.

## Where To Make Changes

Use the layer that owns the behaviour being changed.

| Change needed | Work mainly in | Rule |
| --- | --- | --- |
| Page wording or layout | `app/templates/` | Keep database logic out of templates. |
| Styling or browser behaviour | `app/static/css/`, `app/static/js/` | Keep JavaScript focused on interface behaviour. |
| URL handling or redirects | `app/routes/` | Routes should call services, not SQL directly. |
| Validation or business rules | `app/services/` | Keep reusable rules out of templates and repositories. |
| Queries or transactions | `app/repositories/` | Use parameterised SQL and preserve transaction safety. |
| Database baseline or sample data | `sql/postgresql/` | Change only with team agreement and regression testing. |
| Automated checks | `tests/` | Update expected behaviour without weakening coverage. |
| Setup or handover text | `docs/` | Avoid duplicating information already held in another guide. |

## Rules For Future Changes

1. Keep routes, services and repositories separated.
2. Keep direct SQL out of routes and templates.
3. Use parameterised SQL for user-controlled values.
4. Do not commit `.env`, passwords or local credentials.
5. Do not reintroduce MySQL or a live SQLite fallback.
6. Do not hard-delete students; use the withdrawal lifecycle.
7. Do not modify the approved SQL package without team agreement and regression
   testing.
8. Treat authentication, role-based authorisation and public deployment as
   separate future scope.
