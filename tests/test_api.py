"""Tests for the API endpoints."""

import pytest
from fastapi.testclient import TestClient

from app.api import app


@pytest.fixture
def client() -> TestClient:
    """Provide a test client for the API."""
    return TestClient(app)


class TestHealthCheck:
    """Tests for the health endpoint."""

    def test_health_returns_200(self, client: TestClient) -> None:
        """Health check should return 200 with status healthy."""
        response = client.get("/health")

        assert response.status_code == 200
        assert response.json() == {"status": "healthy"}


class TestCreateNote:
    """Tests for POST /notes."""

    def test_create_note_returns_201(self, client: TestClient) -> None:
        """Valid note creation should return 201."""
        response = client.post(
            "/notes",
            json={
                "patient_id": "patient-001",
                "clinician_id": "clinician-001",
                "content": "Patient presents with headache.",
            },
        )

        assert response.status_code == 201
        data = response.json()
        assert data["patient_id"] == "patient-001"
        assert data["status"] == "draft"
        assert "note_id" in data
        assert "created_at" in data
        assert data["word_count"] == 4

    def test_create_note_empty_content_returns_422(self, client: TestClient) -> None:
        """Empty content should be rejected with 422."""
        response = client.post(
            "/notes",
            json={
                "patient_id": "patient-001",
                "clinician_id": "clinician-001",
                "content": "",
            },
        )

        assert response.status_code == 422

    def test_create_note_missing_field_returns_422(self, client: TestClient) -> None:
        """Missing required fields should return 422."""
        response = client.post(
            "/notes",
            json={
                "patient_id": "patient-001",
                "content": "Some content.",
            },
        )

        assert response.status_code == 422


class TestGetNote:
    """Tests for GET /notes/{note_id}."""

    def test_get_existing_note(self, client: TestClient) -> None:
        """A created note can be retrieved."""
        create_response = client.post(
            "/notes",
            json={
                "patient_id": "patient-001",
                "clinician_id": "clinician-001",
                "content": "Original content.",
            },
        )
        note_id = create_response.json()["note_id"]

        response = client.get(f"/notes/{note_id}")

        assert response.status_code == 200
        assert response.json()["content"] == "Original content."

    def test_get_nonexistent_note_returns_404(self, client: TestClient) -> None:
        """Requesting a non-existent note should return 404."""
        response = client.get("/notes/note-9999")

        assert response.status_code == 404


class TestFinaliseNote:
    """Tests for POST /notes/{note_id}/finalise."""

    def test_finalise_note_returns_final_status(self, client: TestClient) -> None:
        """Finalising a note should return it with status final."""
        create_response = client.post(
            "/notes",
            json={
                "patient_id": "patient-001",
                "clinician_id": "clinician-001",
                "content": "Patient is stable.",
            },
        )
        note_id = create_response.json()["note_id"]

        response = client.post(f"/notes/{note_id}/finalise")

        assert response.status_code == 200
        assert response.json()["status"] == "final"

    def test_finalise_nonexistent_returns_404(self, client: TestClient) -> None:
        """Finalising a non-existent note should return 404."""
        response = client.post("/notes/note-9999/finalise")

        assert response.status_code == 404

    def test_finalise_already_final_returns_422(self, client: TestClient) -> None:
        """Finalising an already-final note should return 422."""
        create_response = client.post(
            "/notes",
            json={
                "patient_id": "patient-001",
                "clinician_id": "clinician-001",
                "content": "Patient is stable.",
            },
        )
        note_id = create_response.json()["note_id"]

        client.post(f"/notes/{note_id}/finalise")
        response = client.post(f"/notes/{note_id}/finalise")

        assert response.status_code == 422
