"""Tests for the API endpoints."""

from collections.abc import AsyncGenerator

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool

from app.api import app
from app.config import get_settings
from app.database import get_db_session

settings = get_settings()

# NullPool = new connection per operation, no sharing conflicts
_test_engine = create_async_engine(
    settings.database_url, echo=False, poolclass=NullPool
)
_test_session_factory = async_sessionmaker(
    _test_engine, class_=AsyncSession, expire_on_commit=False
)


@pytest.fixture
async def client() -> AsyncGenerator[AsyncClient, None]:
    """Provide an async test client with a fresh database state."""

    # Clean table before test
    async with _test_engine.begin() as conn:
        await conn.execute(text("DELETE FROM clinical_notes"))

    async def _override_get_db_session() -> AsyncGenerator[AsyncSession, None]:
        async with _test_session_factory() as session:
            yield session

    app.dependency_overrides[get_db_session] = _override_get_db_session

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()


class TestHealthCheck:
    """Tests for the health endpoint."""

    async def test_health_returns_200(self, client: AsyncClient) -> None:
        """Health check should return 200 with status healthy."""
        response = await client.get("/health")

        assert response.status_code == 200
        assert response.json() == {"status": "healthy"}


class TestCreateNote:
    """Tests for POST /notes."""

    async def test_create_note_returns_201(self, client: AsyncClient) -> None:
        """Valid note creation should return 201."""
        response = await client.post(
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
        assert data["word_count"] == 4

    async def test_create_note_empty_content_returns_422(
        self, client: AsyncClient
    ) -> None:
        """Empty content should be rejected with 422."""
        response = await client.post(
            "/notes",
            json={
                "patient_id": "patient-001",
                "clinician_id": "clinician-001",
                "content": "",
            },
        )

        assert response.status_code == 422

    async def test_create_note_missing_field_returns_422(
        self, client: AsyncClient
    ) -> None:
        """Missing required fields should return 422."""
        response = await client.post(
            "/notes",
            json={
                "patient_id": "patient-001",
                "content": "Some content.",
            },
        )

        assert response.status_code == 422


class TestGetNote:
    """Tests for GET /notes/{note_id}."""

    async def test_get_existing_note(self, client: AsyncClient) -> None:
        """A created note can be retrieved."""
        create_response = await client.post(
            "/notes",
            json={
                "patient_id": "patient-001",
                "clinician_id": "clinician-001",
                "content": "Original content.",
            },
        )
        note_id = create_response.json()["note_id"]

        response = await client.get(f"/notes/{note_id}")

        assert response.status_code == 200
        assert response.json()["content"] == "Original content."

    async def test_get_nonexistent_note_returns_404(self, client: AsyncClient) -> None:
        """Requesting a non-existent note should return 404."""
        response = await client.get("/notes/nonexistent-id")

        assert response.status_code == 404


class TestListNotes:
    """Tests for GET /notes."""

    async def test_list_notes_returns_created(self, client: AsyncClient) -> None:
        """Created notes should appear in the list."""
        await client.post(
            "/notes",
            json={
                "patient_id": "patient-001",
                "clinician_id": "clinician-001",
                "content": "First note.",
            },
        )

        response = await client.get("/notes")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1


class TestFinaliseNote:
    """Tests for POST /notes/{note_id}/finalise."""

    async def test_finalise_note_returns_final_status(
        self, client: AsyncClient
    ) -> None:
        """Finalising a note should return it with status final."""
        create_response = await client.post(
            "/notes",
            json={
                "patient_id": "patient-001",
                "clinician_id": "clinician-001",
                "content": "Patient is stable.",
            },
        )
        note_id = create_response.json()["note_id"]

        response = await client.post(f"/notes/{note_id}/finalise")

        assert response.status_code == 200
        assert response.json()["status"] == "final"

    async def test_finalise_persists_status(self, client: AsyncClient) -> None:
        """Finalised status should persist when reading the note back."""
        create_response = await client.post(
            "/notes",
            json={
                "patient_id": "patient-001",
                "clinician_id": "clinician-001",
                "content": "Patient is stable.",
            },
        )
        note_id = create_response.json()["note_id"]

        await client.post(f"/notes/{note_id}/finalise")
        response = await client.get(f"/notes/{note_id}")

        assert response.json()["status"] == "final"

    async def test_finalise_nonexistent_returns_404(self, client: AsyncClient) -> None:
        """Finalising a non-existent note should return 404."""
        response = await client.post("/notes/nonexistent-id/finalise")

        assert response.status_code == 404

    async def test_finalise_already_final_returns_422(
        self, client: AsyncClient
    ) -> None:
        """Finalising an already-final note should return 422."""
        create_response = await client.post(
            "/notes",
            json={
                "patient_id": "patient-001",
                "clinician_id": "clinician-001",
                "content": "Patient is stable.",
            },
        )
        note_id = create_response.json()["note_id"]

        await client.post(f"/notes/{note_id}/finalise")
        response = await client.post(f"/notes/{note_id}/finalise")

        assert response.status_code == 422
