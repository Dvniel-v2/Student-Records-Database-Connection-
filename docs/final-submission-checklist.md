# Final Submission Checklist

Use this checklist before creating the final repository ZIP or submitting the
GitHub link. Do not commit screenshots unless the team intentionally adds image
evidence to the repository.

## Application Verification

- [ ] Dashboard
- [ ] Students
- [ ] Student details
- [ ] Create Student
- [ ] Edit Student
- [ ] Withdraw Student
- [ ] Courses
- [ ] Modules
- [ ] Enrolments
- [ ] Grades
- [ ] Reports
- [ ] Database health endpoint

## Assignment Reports

- [ ] Students by course and lecturer
- [ ] Final-year students above 70%
- [ ] Students without current registration
- [ ] Academic adviser lookup
- [ ] Lecturers by expertise
- [ ] Staff by department or unit
- [ ] Research project summary
- [ ] Programme credit summary

## Quality Checks

- [ ] `ruff check .`
- [ ] `black --check .`
- [ ] `pytest --cov=app --cov-report=term-missing`
- [ ] Coverage percentage recorded
- [ ] Live PostgreSQL verification completed when local PostgreSQL is available

## Security

- [ ] `.env` excluded
- [ ] Passwords excluded
- [ ] `DATABASE_URL` not exposed
- [ ] Parameterised SQL used
- [ ] CSRF enabled for write forms
- [ ] Personal data is masked where the approved views require masking

## Evidence

- [ ] Dashboard screenshot
- [ ] Student Directory screenshot
- [ ] Create screenshot
- [ ] Edit screenshot
- [ ] Withdrawal screenshot
- [ ] Courses screenshot
- [ ] Modules screenshot
- [ ] Enrolments screenshot
- [ ] Grades screenshot
- [ ] Reports catalogue screenshot
- [ ] Eight report screenshots
- [ ] Database health screenshot
- [ ] PostgreSQL schema screenshot
- [ ] Test output
- [ ] Coverage output
- [ ] Demonstration video

## Submission Package

- [ ] README checked
- [ ] Start Here guide checked
- [ ] SQL scripts included
- [ ] `requirements.txt` included
- [ ] `.env.example` included
- [ ] Final ZIP tested
- [ ] Temporary data removed
