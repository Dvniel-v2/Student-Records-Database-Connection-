# Requirement Coverage

This matrix maps the implemented application to the assignment requirements and
the approved PostgreSQL database package.

| Assignment requirement | Application feature | Route | Repository or service | Database object | Status | Evidence |
| --- | --- | --- | --- | --- | --- | --- |
| PostgreSQL connection | Database health check | `/health/database` | `DatabaseHealthService`, `DatabaseHealthRepository` | `use_record_management.student` | Complete | Health endpoint returns schema and table status |
| Dashboard | Overview metrics and charts | `/` | `DashboardService`, `DashboardRepository` | `student`, `programme`, `enrolment` | Complete | Dashboard cards and bar charts use PostgreSQL counts |
| Student directory | Searchable, filtered, paginated directory | `/students` | `ApprovedStudentService`, `ApprovedStudentRepository` | `vw_student_directory_masked` | Complete | Student list, search, programme and status filters |
| Student detail | Single Student profile | `/students/<student_id>` | `ApprovedStudentService`, `ApprovedStudentRepository` | `vw_student_directory_masked` | Complete | Detail page shows masked Student data |
| Student create | Transactional create workflow | `/students/new`, `POST /students` | `StudentWriteService`, `StudentWriteRepository` | `person`, `student`, `person_contact` | Complete | Form validation, CSRF and PostgreSQL transaction |
| Student edit | Transactional update workflow | `/students/<student_id>/edit` | `StudentWriteService`, `StudentWriteRepository` | `person`, `student`, `person_contact` | Complete | Form validation, duplicate checks and transaction rollback |
| Student delete or archive | Safe lifecycle action | `/students/<student_id>/delete` | `StudentWriteService`, `StudentWriteRepository` | `student.student_status` | Complete | Uses `Withdrawn` status because schema has no archive status |
| Courses page | Course catalogue | `/courses` | `AcademicRecordService`, `AcademicRecordRepository` | `course`, `department`, `course_offering` | Complete | Read-only table from approved tables |
| Modules page | Course offerings as modules | `/modules` | `AcademicRecordService`, `AcademicRecordRepository` | `course_offering`, `course`, `academic_term` | Complete | Read-only module offering table |
| Enrolments page | Approved enrolment records | `/enrolments` | `AcademicRecordService`, `AcademicRecordRepository` | `enrolment`, `student`, `course_offering` | Complete | Read-only enrolment table |
| Grades page | Approved grade records | `/grades` | `AcademicRecordService`, `AcademicRecordRepository` | `grade`, `enrolment`, `student` | Complete | Read-only grade table |
| Reports catalogue | Assignment query centre | `/reports` | `AssignmentReportService` | Multiple approved tables and views | Complete | Catalogue lists eight report functions |
| Students on course taught by lecturer | Filtered report | `/reports/students-by-course-lecturer` | `AssignmentReportService`, `AssignmentReportRepository` | `enrolment`, `course_offering`, `offering_lecturer` | Complete | Course and lecturer dropdowns |
| Final-year Students above 70 percent | Calculated report | `/reports/final-year-high-achievers` | `AssignmentReportService`, `AssignmentReportRepository` | `student`, `programme`, `grade` | Complete | PostgreSQL average calculation |
| Students with no current registration | Current-term exception report | `/reports/students-without-current-registration` | `AssignmentReportService`, `AssignmentReportRepository` | `academic_term`, `enrolment`, `student` | Complete | Current term is derived from approved term dates |
| Academic adviser details | Adviser lookup | `/reports/academic-adviser` | `AssignmentReportService`, `AssignmentReportRepository` | `advisor_assignment`, `lecturer`, `department` | Complete | Student dropdown and adviser result table |
| Lecturers by expertise | Expertise search | `/reports/lecturer-expertise` | `AssignmentReportService`, `AssignmentReportRepository` | `lecturer_expertise`, `lecturer` | Complete | Partial expertise search |
| Staff by department or unit | Staff lookup | `/reports/staff-by-location` | `AssignmentReportService`, `AssignmentReportRepository` | `non_academic_staff`, `department`, `administrative_unit` | Complete | Combined department and unit dropdown |
| Research project summary | Research summary report | `/reports/research-project-summary` | `AssignmentReportService`, `AssignmentReportRepository` | `research_project`, `research_group`, funding and publication tables | Complete | Optional project and group filters |
| Programme credit summary | Credit comparison report | `/reports/programme-credit-summary` | `AssignmentReportService`, `AssignmentReportRepository` | `vw_programme_credit_summary` | Complete | Programme dropdown and credit difference |
| Three-layer architecture | Routes, services and repositories | All routes | Route, service and repository modules | N/A | Complete | SQL remains in repository classes |
| Security basics | CSRF and parameterised SQL | Student POST routes | `csrf.py`, write service and repositories | N/A | Complete | POST routes validate CSRF and repository SQL uses parameters |
| Reproducible local setup | Assessor guide | N/A | Documentation | SQL scripts in `sql/postgresql` | Complete | `docs/assessor-setup.md` documents local PostgreSQL workflow |

## Known Limitations

The application runs locally and does not include authentication or role-based
authorisation. The approved database contains role examples, but the Flask
application does not yet implement user login or permission checks.
