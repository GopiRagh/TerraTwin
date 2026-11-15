
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_home():
    response = client.get("/")
    assert response.status_code == 200


def test_health():
    response = client.get("/health")
    assert response.status_code == 200


def test_get_planets():
    response = client.get("/api/planets/")
    assert response.status_code == 200
    assert response.json()["total"] >= 1


def test_get_locations():
    response = client.get("/api/locations/")
    assert response.status_code == 200


def test_create_analysis():
    response = client.post(
        "/api/analyze/",
        json={
            "target_planet": "mars",
            "target_location": "Jezero Crater"
        }
    )

    assert response.status_code == 200
    assert response.json()["status"] == "accepted"


def test_invalid_planet():
    response = client.post(
        "/api/analyze/",
        json={
            "target_planet": "jupiter",
            "target_location": "Great Red Spot"
        }
    )

    assert response.status_code == 422


def test_invalid_location_id():
    response = client.get("/api/locations/invalid_location")
    assert response.status_code == 404


def test_invalid_analysis_id():
    response = client.get(
        "/api/analyze/00000000-0000-0000-0000-000000000000"
    )
    assert response.status_code == 404


def test_get_analysis_by_id():
    create_response = client.post(
        "/api/analyze/",
        json={
            "target_planet": "mars",
            "target_location": "Jezero Crater"
        }
    )

    analysis_id = create_response.json()["data"]["analysis_id"]

    response = client.get(f"/api/analyze/{analysis_id}")

    assert response.status_code == 200
    assert response.json()["data"]["analysis_id"] == analysis_id


def test_moon_comparison_and_result_storage():
    response = client.post(
        "/api/analyze/compare",
        json={
            "target_planet": "moon",
            "target_location": "Shackleton Crater"
        }
    )

    assert response.status_code == 200

    data = response.json()
    analysis_id = data["analysis_id"]

    assert data["status"] == "success"
    assert data["data"]["candidate_count"] >= 2

    status_response = client.get(
        f"/api/analyze/{analysis_id}"
    )

    assert status_response.status_code == 200

    saved_analysis = status_response.json()["data"]

    assert saved_analysis["status"] == "completed"
    assert len(saved_analysis["results"]) >= 2


def test_mars_comparison_and_result_storage():
    response = client.post(
        "/api/analyze/compare",
        json={
            "target_planet": "mars",
            "target_location": "Jezero Crater"
        }
    )

    assert response.status_code == 200

    data = response.json()
    analysis_id = data["analysis_id"]

    assert data["status"] == "success"
    assert data["data"]["candidate_count"] >= 2

    status_response = client.get(
        f"/api/analyze/{analysis_id}"
    )

    assert status_response.status_code == 200

    saved_analysis = status_response.json()["data"]

    assert saved_analysis["status"] == "completed"
    assert len(saved_analysis["results"]) >= 2
