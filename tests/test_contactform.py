import pytest


@pytest.fixture
def valid_form_data():
    return {
        "name": "PEKIM",
        "email": "pekimsender@example.com",
        "subject": "Test Inquiry",
        "message": "This is a test message.",
    }


def test_contact_form_submission(client, mocker, valid_form_data):
    mocker.patch("app.routes.log_submission")
    mocker.patch("app.routes.db.session.add")
    mocker.patch("app.routes.db.session.commit")
    mock_smtp = mocker.patch("app.routes.smtplib.SMTP_SSL")
    mock_smtp.return_value.__enter__.return_value.send_message = mocker.Mock()

    response = client.post("/contact", data=valid_form_data, follow_redirects=True)
    assert response.status_code == 200
    assert b"Thank you for reaching out!" in response.data


def test_contact_form_missing_fields(client):
    response = client.post("/contact", data={}, follow_redirects=True)
    assert response.status_code == 200
    assert b"Please fill all fields correctly." in response.data


def test_contact_form_invalid_email(client, valid_form_data):
    valid_form_data["email"] = "not-an-email"
    response = client.post("/contact", data=valid_form_data, follow_redirects=True)
    assert response.status_code == 200
    assert b"Please fill all fields correctly." in response.data
