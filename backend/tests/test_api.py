from datetime import timedelta

from app.core.config import get_settings
from app.core.security import create_access_token
from app.models.diagnostic_centre import DiagnosticCentre
from tests.conftest import auth_headers, future_date


def test_health_check(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_signup(client):
    response = client.post(
        "/auth/signup",
        json={"name": "Mehul Kumar", "email": "mehul@example.com", "password": "secret123"},
    )
    assert response.status_code == 201
    body = response.json()
    assert body["email"] == "mehul@example.com"
    assert "password" not in body
    assert "password_hash" not in body


def test_signup_validation_error(client):
    invalid_email = client.post(
        "/auth/signup",
        json={"name": "Invalid Email", "email": "not-an-email", "password": "secret123"},
    )
    assert invalid_email.status_code == 422

    short_pass = client.post(
        "/auth/signup",
        json={"name": "Short Pass", "email": "short@example.com", "password": "123"},
    )
    assert short_pass.status_code == 422


def test_signup_duplicate_email(client):
    payload = {"name": "Mehul Kumar", "email": "dup@example.com", "password": "secret123"}
    assert client.post("/auth/signup", json=payload).status_code == 201
    response = client.post("/auth/signup", json=payload)
    assert response.status_code == 409


def test_login(client):
    client.post(
        "/auth/signup",
        json={"name": "Mehul Kumar", "email": "login@example.com", "password": "secret123"},
    )
    response = client.post(
        "/auth/login",
        json={"email": "login@example.com", "password": "secret123"},
    )
    assert response.status_code == 200
    assert response.json()["access_token"]
    assert response.json()["token_type"] == "bearer"


def test_invalid_login(client):
    response = client.post(
        "/auth/login",
        json={"email": "missing@example.com", "password": "wrongpass"},
    )
    assert response.status_code == 401


def test_invalid_and_expired_jwt(client, seed_centre):
    response = client.get("/bookings/", headers={"Authorization": "Bearer not-a-token"})
    assert response.status_code == 401

    expired = create_access_token("1", expires_delta=timedelta(minutes=-5))
    response = client.get("/bookings/", headers={"Authorization": f"Bearer {expired}"})
    assert response.status_code == 401


def test_centre_listing(client, seed_centre):
    response = client.get("/centres/")
    assert response.status_code == 200
    body = response.json()
    assert body["total"] >= 1
    assert body["items"][0]["name"] == "Apollo Diagnostics"
    assert body["items"][0]["available_tests"] == 2


def test_centre_search(client, seed_centre):
    assert client.get("/centres/", params={"q": "Bokaro"}).json()["total"] == 1
    assert client.get("/centres/", params={"q": "UnknownCity"}).json()["total"] == 0
    assert client.get("/centres/9999").status_code == 404


def test_test_listing(client, seed_centre):
    centre, test = seed_centre
    response = client.get(f"/centres/{centre.id}/tests")
    assert response.status_code == 200
    names = [item["name"] for item in response.json()]
    assert "Lipid Profile" in names
    assert client.get(f"/tests/{test.id}").status_code == 200
    assert client.get("/tests/9999").status_code == 404


def _create_booking(client, headers, seed_centre):
    centre, test = seed_centre
    response = client.post(
        "/bookings/",
        headers=headers,
        json={
            "test_id": test.id,
            "centre_id": centre.id,
            "appointment_date": future_date(),
            "appointment_time": "10:00:00",
        },
    )
    assert response.status_code == 201
    return response.json()


def test_booking_creation(client, seed_centre):
    headers = auth_headers(client, "book")
    body = _create_booking(client, headers, seed_centre)
    assert body["status"] == "PENDING"
    assert body["amount"] == 500
    assert body["booking_code"].startswith("BK")


def test_booking_creation_edge_cases(client, seed_centre, db):
    headers = auth_headers(client, "book_edge")
    centre, test = seed_centre

    # Non-existent centre
    res = client.post(
        "/bookings/",
        headers=headers,
        json={
            "test_id": test.id,
            "centre_id": 9999,
            "appointment_date": future_date(),
            "appointment_time": "10:00:00",
        },
    )
    assert res.status_code == 404

    # Non-existent test
    res = client.post(
        "/bookings/",
        headers=headers,
        json={
            "test_id": 9999,
            "centre_id": centre.id,
            "appointment_date": future_date(),
            "appointment_time": "10:00:00",
        },
    )
    assert res.status_code == 404

    # Mismatched test and centre
    other_centre = DiagnosticCentre(name="Other Centre", location="City", description="Desc")
    db.add(other_centre)
    db.commit()
    res = client.post(
        "/bookings/",
        headers=headers,
        json={
            "test_id": test.id,
            "centre_id": other_centre.id,
            "appointment_date": future_date(),
            "appointment_time": "10:00:00",
        },
    )
    assert res.status_code == 400
    assert "does not belong" in res.json()["detail"]

    # Appointment date in the past
    res = client.post(
        "/bookings/",
        headers=headers,
        json={
            "test_id": test.id,
            "centre_id": centre.id,
            "appointment_date": "2020-01-01",
            "appointment_time": "10:00:00",
        },
    )
    assert res.status_code == 422

    # Appointment time outside 07:00 - 20:00 window
    res = client.post(
        "/bookings/",
        headers=headers,
        json={
            "test_id": test.id,
            "centre_id": centre.id,
            "appointment_date": future_date(),
            "appointment_time": "05:00:00",
        },
    )
    assert res.status_code == 400
    assert "between 07:00 and 20:00" in res.json()["detail"]


def test_unauthorized_booking_access(client, seed_centre):
    owner = auth_headers(client, "owner")
    other = auth_headers(client, "other")
    booking = _create_booking(client, owner, seed_centre)
    response = client.get(f"/bookings/{booking['id']}", headers=other)
    assert response.status_code == 403
    assert client.post("/bookings/", json={}).status_code == 401


def test_successful_payment_and_status_update(client, seed_centre):
    headers = auth_headers(client, "payok")
    booking = _create_booking(client, headers, seed_centre)
    response = client.post(
        "/payments/",
        headers=headers,
        json={"booking_id": booking["id"], "simulate_status": "SUCCESS"},
    )
    assert response.status_code == 201
    body = response.json()
    assert body["status"] == "SUCCESS"
    assert body["booking"]["status"] == "CONFIRMED"
    listed = client.get("/bookings/", headers=headers)
    assert listed.json()["items"][0]["status"] == "CONFIRMED"


def test_failed_payment(client, seed_centre):
    headers = auth_headers(client, "payfail")
    booking = _create_booking(client, headers, seed_centre)
    response = client.post(
        "/payments/",
        headers=headers,
        json={"booking_id": booking["id"], "simulate_status": "FAILED"},
    )
    assert response.status_code == 201
    assert response.json()["status"] == "FAILED"
    assert response.json()["booking"]["status"] == "FAILED"


def test_payment_retry_after_failure(client, seed_centre):
    headers = auth_headers(client, "payretry")
    booking = _create_booking(client, headers, seed_centre)

    # First attempt fails
    fail_res = client.post(
        "/payments/",
        headers=headers,
        json={"booking_id": booking["id"], "simulate_status": "FAILED"},
    )
    assert fail_res.status_code == 201
    assert fail_res.json()["booking"]["status"] == "FAILED"

    # Retry attempt succeeds
    retry_res = client.post(
        "/payments/",
        headers=headers,
        json={"booking_id": booking["id"], "simulate_status": "SUCCESS"},
    )
    assert retry_res.status_code == 201
    assert retry_res.json()["status"] == "SUCCESS"
    assert retry_res.json()["booking"]["status"] == "CONFIRMED"


def test_payment_validation_and_authorization(client, seed_centre):
    user1 = auth_headers(client, "pay_u1")
    user2 = auth_headers(client, "pay_u2")
    booking = _create_booking(client, user1, seed_centre)

    # Paying for another user's booking -> 403
    res_other = client.post(
        "/payments/",
        headers=user2,
        json={"booking_id": booking["id"], "simulate_status": "SUCCESS"},
    )
    assert res_other.status_code == 403

    # Paying for non-existent booking -> 404
    res_404 = client.post(
        "/payments/",
        headers=user1,
        json={"booking_id": 9999, "simulate_status": "SUCCESS"},
    )
    assert res_404.status_code == 404

    # Pay successfully once
    client.post(
        "/payments/",
        headers=user1,
        json={"booking_id": booking["id"], "simulate_status": "SUCCESS"},
    )

    # Paying for already confirmed booking -> 400
    res_again = client.post(
        "/payments/",
        headers=user1,
        json={"booking_id": booking["id"], "simulate_status": "SUCCESS"},
    )
    assert res_again.status_code == 400
    assert "already confirmed" in res_again.json()["detail"]


def test_successful_webhook(client, seed_centre):
    headers = auth_headers(client, "hook")
    booking = _create_booking(client, headers, seed_centre)
    payment = client.post(
        "/payments/",
        headers=headers,
        json={"booking_id": booking["id"], "simulate_status": "FAILED"},
    ).json()

    webhook = client.post(
        "/payments/webhook/",
        json={
            "event_id": "evt_success_1",
            "payment_id": payment["id"],
            "booking_id": booking["id"],
            "status": "SUCCESS",
        },
    )
    assert webhook.status_code == 200
    body = webhook.json()
    assert body["processed"] is True
    assert body["idempotent"] is False
    assert body["payment"]["booking"]["status"] == "CONFIRMED"


def test_duplicate_webhook(client, seed_centre):
    headers = auth_headers(client, "duphook")
    booking = _create_booking(client, headers, seed_centre)
    payment = client.post(
        "/payments/",
        headers=headers,
        json={"booking_id": booking["id"], "simulate_status": "SUCCESS"},
    ).json()
    payload = {
        "event_id": "evt_12345",
        "payment_id": payment["id"],
        "booking_id": booking["id"],
        "status": "SUCCESS",
    }
    first = client.post("/payments/webhook/", json=payload)
    second = client.post("/payments/webhook/", json=payload)
    assert first.status_code == 200
    assert second.status_code == 200
    assert second.json()["idempotent"] is True
    assert second.json()["processed"] is False


def test_invalid_webhook(client, seed_centre):
    headers = auth_headers(client, "invhook")
    booking = _create_booking(client, headers, seed_centre)
    payment = client.post(
        "/payments/",
        headers=headers,
        json={"booking_id": booking["id"], "simulate_status": "SUCCESS"},
    ).json()

    # Missing fields
    missing = client.post("/payments/webhook/", json={"event_id": "evt"})
    assert missing.status_code == 422

    # Unknown payment/booking
    unknown = client.post(
        "/payments/webhook/",
        json={
            "event_id": "evt_missing",
            "payment_id": 9999,
            "booking_id": 9999,
            "status": "SUCCESS",
        },
    )
    assert unknown.status_code == 404

    # Mismatched payment and booking
    booking2 = _create_booking(client, headers, seed_centre)
    mismatched = client.post(
        "/payments/webhook/",
        json={
            "event_id": "evt_mismatched",
            "payment_id": payment["id"],
            "booking_id": booking2["id"],
            "status": "SUCCESS",
        },
    )
    assert mismatched.status_code == 400
    assert "does not belong" in mismatched.json()["detail"]


def test_webhook_on_cancelled_booking(client, seed_centre):
    headers = auth_headers(client, "hook_cancel")
    booking = _create_booking(client, headers, seed_centre)
    payment = client.post(
        "/payments/",
        headers=headers,
        json={"booking_id": booking["id"], "simulate_status": "SUCCESS"},
    ).json()

    # Cancel the confirmed booking
    cancel_res = client.patch(f"/bookings/{booking['id']}/cancel", headers=headers)
    assert cancel_res.status_code == 200
    assert cancel_res.json()["status"] == "CANCELLED"

    # Webhook arrives for payment
    webhook = client.post(
        "/payments/webhook/",
        json={
            "event_id": "evt_cancel_hook",
            "payment_id": payment["id"],
            "booking_id": booking["id"],
            "status": "SUCCESS",
        },
    )
    assert webhook.status_code == 200
    assert webhook.json()["payment"]["booking"]["status"] == "CANCELLED"



def test_webhook_secret_header(client, seed_centre, monkeypatch):
    settings = get_settings()
    monkeypatch.setattr(settings, "WEBHOOK_SECRET", "super-secret-key")

    headers = auth_headers(client, "hook_sec")
    booking = _create_booking(client, headers, seed_centre)
    payment = client.post(
        "/payments/",
        headers=headers,
        json={"booking_id": booking["id"], "simulate_status": "SUCCESS"},
    ).json()

    payload = {
        "event_id": "evt_sec_100",
        "payment_id": payment["id"],
        "booking_id": booking["id"],
        "status": "SUCCESS",
    }

    # Missing or wrong secret -> 401
    bad_res = client.post("/payments/webhook/", json=payload)
    assert bad_res.status_code == 401

    wrong_res = client.post(
        "/payments/webhook/",
        json=payload,
        headers={"X-Webhook-Secret": "wrong"},
    )
    assert wrong_res.status_code == 401

    # Correct secret -> 200
    good_res = client.post(
        "/payments/webhook/",
        json=payload,
        headers={"X-Webhook-Secret": "super-secret-key"},
    )
    assert good_res.status_code == 200


def test_cancel_booking(client, seed_centre):
    headers = auth_headers(client, "cancel")
    booking = _create_booking(client, headers, seed_centre)
    response = client.patch(f"/bookings/{booking['id']}/cancel", headers=headers)
    assert response.status_code == 200
    assert response.json()["status"] == "CANCELLED"


def test_cancel_booking_edge_cases(client, seed_centre):
    owner = auth_headers(client, "cancel_owner")
    other = auth_headers(client, "cancel_other")
    booking = _create_booking(client, owner, seed_centre)

    # Cancel non-existent booking -> 404
    assert client.patch("/bookings/9999/cancel", headers=owner).status_code == 404

    # Cancel another user's booking -> 403
    assert client.patch(f"/bookings/{booking['id']}/cancel", headers=other).status_code == 403

    # Cancel already cancelled booking -> 400
    client.patch(f"/bookings/{booking['id']}/cancel", headers=owner)
    again = client.patch(f"/bookings/{booking['id']}/cancel", headers=owner)
    assert again.status_code == 400
    assert "Cannot cancel a booking with status CANCELLED" in again.json()["detail"]
