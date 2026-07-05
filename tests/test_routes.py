"""Tests for the main routes."""


def test_index_page_renders(client):
    response = client.get("/")

    assert response.status_code == 200
    assert b"Student Records Database" in response.data


def test_create_record_with_valid_data(client):
    response = client.post(
        "/records",
        data={"name": "Ada", "description": "A student record"},
        follow_redirects=True,
    )

    assert response.status_code == 200
    assert b"Record created successfully." in response.data


def test_create_record_with_invalid_data(client):
    response = client.post(
        "/records",
        data={"name": "A", "description": ""},
        follow_redirects=True,
    )

    assert response.status_code == 400
    assert (
        b"Name must be at least 2 characters long." in response.data
        or b"Description is required." in response.data
    )
