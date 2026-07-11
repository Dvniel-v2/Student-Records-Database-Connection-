-- USE Full University Record Management System
-- PostgreSQL conversion of 04_use_validation_queries.sql
SET search_path TO use_record_management, public;

-- 1. Table counts
SELECT 'college' AS table_name, COUNT(*) AS total_rows FROM college
UNION ALL
SELECT 'department' AS table_name, COUNT(*) AS total_rows FROM department
UNION ALL
SELECT 'administrative_unit' AS table_name, COUNT(*) AS total_rows FROM administrative_unit
UNION ALL
SELECT 'programme' AS table_name, COUNT(*) AS total_rows FROM programme
UNION ALL
SELECT 'person' AS table_name, COUNT(*) AS total_rows FROM person
UNION ALL
SELECT 'student' AS table_name, COUNT(*) AS total_rows FROM student
UNION ALL
SELECT 'lecturer' AS table_name, COUNT(*) AS total_rows FROM lecturer
UNION ALL
SELECT 'administrator' AS table_name, COUNT(*) AS total_rows FROM administrator
UNION ALL
SELECT 'non_academic_staff' AS table_name, COUNT(*) AS total_rows FROM non_academic_staff
UNION ALL
SELECT 'course' AS table_name, COUNT(*) AS total_rows FROM course
UNION ALL
SELECT 'academic_term' AS table_name, COUNT(*) AS total_rows FROM academic_term
UNION ALL
SELECT 'course_offering' AS table_name, COUNT(*) AS total_rows FROM course_offering
UNION ALL
SELECT 'offering_lecturer' AS table_name, COUNT(*) AS total_rows FROM offering_lecturer
UNION ALL
SELECT 'enrolment' AS table_name, COUNT(*) AS total_rows FROM enrolment
UNION ALL
SELECT 'grade' AS table_name, COUNT(*) AS total_rows FROM grade
UNION ALL
SELECT 'advisor_assignment' AS table_name, COUNT(*) AS total_rows FROM advisor_assignment
UNION ALL
SELECT 'course_prerequisite' AS table_name, COUNT(*) AS total_rows FROM course_prerequisite
UNION ALL
SELECT 'programme_course_requirement' AS table_name, COUNT(*) AS total_rows FROM programme_course_requirement
UNION ALL
SELECT 'elective_group' AS table_name, COUNT(*) AS total_rows FROM elective_group
UNION ALL
SELECT 'elective_group_course' AS table_name, COUNT(*) AS total_rows FROM elective_group_course
UNION ALL
SELECT 'research_centre' AS table_name, COUNT(*) AS total_rows FROM research_centre
UNION ALL
SELECT 'research_group' AS table_name, COUNT(*) AS total_rows FROM research_group
UNION ALL
SELECT 'research_project' AS table_name, COUNT(*) AS total_rows FROM research_project
UNION ALL
SELECT 'research_project_member' AS table_name, COUNT(*) AS total_rows FROM research_project_member
UNION ALL
SELECT 'funding_source' AS table_name, COUNT(*) AS total_rows FROM funding_source
UNION ALL
SELECT 'publication' AS table_name, COUNT(*) AS total_rows FROM publication
UNION ALL
SELECT 'committee' AS table_name, COUNT(*) AS total_rows FROM committee
UNION ALL
SELECT 'student_organisation' AS table_name, COUNT(*) AS total_rows FROM student_organisation
UNION ALL
SELECT 'student_employment' AS table_name, COUNT(*) AS total_rows FROM student_employment;

-- 2. Duplicate visible IDs should return zero rows
SELECT 'student' AS table_name, student_number, COUNT(*) AS duplicate_count FROM student GROUP BY student_number HAVING COUNT(*) > 1;
SELECT 'lecturer' AS table_name, lecturer_number, COUNT(*) AS duplicate_count FROM lecturer GROUP BY lecturer_number HAVING COUNT(*) > 1;
SELECT 'administrator' AS table_name, admin_number, COUNT(*) AS duplicate_count FROM administrator GROUP BY admin_number HAVING COUNT(*) > 1;
SELECT 'non_academic_staff' AS table_name, staff_number, COUNT(*) AS duplicate_count FROM non_academic_staff GROUP BY staff_number HAVING COUNT(*) > 1;
SELECT 'programme' AS table_name, programme_code, COUNT(*) AS duplicate_count FROM programme GROUP BY programme_code HAVING COUNT(*) > 1;
SELECT 'course' AS table_name, course_code, COUNT(*) AS duplicate_count FROM course GROUP BY course_code HAVING COUNT(*) > 1;

-- 3. Orphan and completeness checks should return zero rows
-- students_without_programme
SELECT s.student_number FROM student s LEFT JOIN programme p ON p.programme_id = s.programme_id WHERE p.programme_id IS NULL;
-- students_without_current_advisor
SELECT s.student_number FROM student s LEFT JOIN advisor_assignment aa ON aa.student_id = s.student_id AND aa.is_current = TRUE WHERE aa.advisor_assignment_id IS NULL;
-- course_offerings_without_lecturer
SELECT co.offering_id FROM course_offering co LEFT JOIN offering_lecturer ol ON ol.offering_id = co.offering_id WHERE ol.offering_id IS NULL;
-- course_offerings_exceeding_capacity
SELECT co.offering_id, co.capacity, COUNT(e.enrolment_id) AS enrolments FROM course_offering co LEFT JOIN enrolment e ON e.offering_id = co.offering_id AND e.enrolment_status <> 'Withdrawn' GROUP BY co.offering_id, co.capacity HAVING COUNT(e.enrolment_id) > co.capacity;
-- programmes_without_elective_group
SELECT p.programme_code FROM programme p LEFT JOIN elective_group eg ON eg.programme_id = p.programme_id WHERE eg.elective_group_id IS NULL;

-- 4. Required assignment query examples
-- 4.1 Students enrolled in a specific course taught by a particular lecturer
SELECT s.student_number, CONCAT(p.first_name, ' ', p.last_name) AS student_name, c.course_code, c.course_name, l.lecturer_number, CONCAT(lp.first_name, ' ', lp.last_name) AS lecturer_name
FROM enrolment e
JOIN student s ON s.student_id = e.student_id
JOIN person p ON p.person_id = s.person_id
JOIN course_offering co ON co.offering_id = e.offering_id
JOIN course c ON c.course_id = co.course_id
JOIN offering_lecturer ol ON ol.offering_id = co.offering_id
JOIN lecturer l ON l.lecturer_id = ol.lecturer_id
JOIN person lp ON lp.person_id = l.person_id
WHERE c.course_code = 'UUSE101'
ORDER BY student_name
LIMIT 50;
-- 4.2 Final-SMALLINT students with average grade above 70%
SELECT * FROM vw_student_result_summary WHERE year_of_study IN (2,4) AND average_overall_grade > 70 ORDER BY average_overall_grade DESC LIMIT 100;
-- 4.3 Students not registered in current term Fall 2026/27
SELECT s.student_number, CONCAT(p.first_name, ' ', p.last_name) AS student_name, pr.programme_code
FROM student s
JOIN person p ON p.person_id = s.person_id
JOIN programme pr ON pr.programme_id = s.programme_id
WHERE NOT EXISTS (
    SELECT 1 FROM enrolment e
    JOIN course_offering co ON co.offering_id = e.offering_id
    JOIN academic_term at ON at.term_id = co.term_id
    WHERE e.student_id = s.student_id AND at.academic_year = '2026/27' AND at.term_name = 'Fall'
)
ORDER BY pr.programme_code, s.student_number
LIMIT 100;
-- 4.4 Advisor contact details for a selected student
SELECT s.student_number, CONCAT(sp.first_name, ' ', sp.last_name) AS student_name, l.lecturer_number AS advisor_number, CONCAT(lp.first_name, ' ', lp.last_name) AS advisor_name, lp.email AS advisor_email, lp.phone AS advisor_phone
FROM advisor_assignment aa
JOIN student s ON s.student_id = aa.student_id
JOIN person sp ON sp.person_id = s.person_id
JOIN lecturer l ON l.lecturer_id = aa.lecturer_id
JOIN person lp ON lp.person_id = l.person_id
WHERE aa.is_current = TRUE
ORDER BY s.student_number
LIMIT 25;
-- 4.5 Lecturers with expertise in a selected research area
SELECT l.lecturer_number, CONCAT(p.first_name, ' ', p.last_name) AS lecturer_name, d.department_code, le.expertise_area
FROM lecturer_expertise le
JOIN lecturer l ON l.lecturer_id = le.lecturer_id
JOIN person p ON p.person_id = l.person_id
JOIN department d ON d.department_id = l.department_id
WHERE le.expertise_area LIKE '%Research%'
ORDER BY d.department_code, lecturer_name;
-- 4.6 Staff by department or administrative unit
SELECT staff_number, first_name, last_name, unit_or_department_code, job_title FROM vw_staff_directory_masked ORDER BY unit_or_department_code, last_name LIMIT 100;
-- 4.7 Research project summary
SELECT * FROM vw_research_project_summary ORDER BY project_code;
-- 4.8 Programme credit summary
SELECT *, (required_course_credit_hours + required_elective_credit_hours) AS designed_credit_hours FROM vw_programme_credit_summary ORDER BY programme_code;