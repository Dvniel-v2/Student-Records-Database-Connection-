"""Tests for the main routes."""


def test_index_page_renders(client):
    response = client.get("/")

    assert response.status_code == 200
    assert b"Student Records Database" in response.data


def test_create_student_with_valid_data(client, student_data):
    response = client.post(
        "/students",
        data=student_data,
        follow_redirects=True,
    )

    assert response.status_code == 200
    assert b"Student created successfully." in response.data
    assert b"Ada Lovelace" in response.data


def test_create_student_with_invalid_data(client, student_data):
    student_data["email"] = "invalid"
    response = client.post(
        "/students",
        data=student_data,
        follow_redirects=True,
    )

    assert response.status_code == 400
    assert b"Email address is invalid." in response.data


def test_view_student(client, student):
    response = client.get(f"/students/{student.id}")

    assert response.status_code == 200
    assert b"ada@example.com" in response.data


def test_view_missing_student_redirects(client):
    response = client.get("/students/999", follow_redirects=True)

    assert response.status_code == 200
    assert b"Student not found." in response.data


def test_edit_student_success(client, student, student_data):
    response = client.post(
        f"/students/{student.id}/edit",
        data=student_data | {"course": "Software Engineering"},
        follow_redirects=True,
    )

    assert response.status_code == 200
    assert b"Student updated successfully." in response.data
    assert b"Software Engineering" in response.data


def test_edit_student_invalid_data(client, student, student_data):
    response = client.post(
        f"/students/{student.id}/edit",
        data=student_data | {"first_name": "A"},
        follow_redirects=True,
    )

    assert response.status_code == 400
    assert b"First name must be at least 2 characters long." in response.data


def test_edit_missing_student_redirects(client, student_data):
    response = client.post(
        "/students/999/edit",
        data=student_data,
        follow_redirects=True,
    )

    assert response.status_code == 200
    assert b"Student not found." in response.data


def test_delete_confirmation(client, student):
    response = client.get(f"/students/{student.id}/delete")

    assert response.status_code == 200
    assert b"Delete student record" in response.data


def test_delete_student_success(client, student):
    response = client.post(f"/students/{student.id}/delete", follow_redirects=True)

    assert response.status_code == 200
    assert b"Student deleted successfully." in response.data
    assert b"No student records yet." in response.data


def test_delete_missing_student_redirects(client):
    response = client.post("/students/999/delete", follow_redirects=True)

    assert response.status_code == 200
    assert b"Student not found." in response.data
