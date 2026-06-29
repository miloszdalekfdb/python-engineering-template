"""Tests for clinical note service layer."""

import pytest

from app.clinical_note import NoteStatus
from app.repository import InMemoryNoteRepository, NoteNotFoundError
from app.service import NoteService


@pytest.fixture
def service() -> NoteService:
    """Provide a service with a fresh repository."""
    repository = InMemoryNoteRepository()
    return NoteService(repository=repository)


class TestCreateNote:
    """Tests for note creation business logic."""

    def test_create_note_returns_id_and_note(self, service: NoteService) -> None:
        """Creating a note should return both the ID and the note object."""
        note_id, note = service.create_note(
            patient_id="patient-001",
            clinician_id="clinician-001",
            content="Patient reports mild headache.",
        )

        assert note_id.startswith("note-")
        assert note.patient_id == "patient-001"
        assert note.content == "Patient reports mild headache."

    def test_create_note_starts_as_draft(self, service: NoteService) -> None:
        """New notes should always be drafts."""
        _, note = service.create_note(
            patient_id="patient-001",
            clinician_id="clinician-001",
            content="Some content.",
        )

        assert note.status == NoteStatus.DRAFT

    def test_create_note_strips_whitespace(self, service: NoteService) -> None:
        """Input should be trimmed of leading/trailing whitespace."""
        _, note = service.create_note(
            patient_id="  patient-001  ",
            clinician_id="  clinician-001  ",
            content="  Some content.  ",
        )

        assert note.patient_id == "patient-001"
        assert note.clinician_id == "clinician-001"
        assert note.content == "Some content."

    def test_create_note_empty_content_raises(self, service: NoteService) -> None:
        """Empty content should be rejected."""
        with pytest.raises(ValueError, match="content cannot be empty"):
            service.create_note(
                patient_id="patient-001",
                clinician_id="clinician-001",
                content="",
            )

    def test_create_note_whitespace_only_content_raises(
        self, service: NoteService
    ) -> None:
        """Whitespace-only content should be treated as empty."""
        with pytest.raises(ValueError, match="content cannot be empty"):
            service.create_note(
                patient_id="patient-001",
                clinician_id="clinician-001",
                content="   ",
            )

    def test_create_note_empty_patient_id_raises(self, service: NoteService) -> None:
        """Empty patient ID should be rejected."""
        with pytest.raises(ValueError, match="Patient ID cannot be empty"):
            service.create_note(
                patient_id="",
                clinician_id="clinician-001",
                content="Some content.",
            )

    def test_create_note_empty_clinician_id_raises(self, service: NoteService) -> None:
        """Empty clinician ID should be rejected."""
        with pytest.raises(ValueError, match="Clinician ID cannot be empty"):
            service.create_note(
                patient_id="patient-001",
                clinician_id="",
                content="Some content.",
            )


class TestFinaliseNote:
    """Tests for note finalisation."""

    def test_finalise_note_changes_status(self, service: NoteService) -> None:
        """Finalising a note should set its status to FINAL."""
        note_id, _ = service.create_note(
            patient_id="patient-001",
            clinician_id="clinician-001",
            content="Patient is stable.",
        )

        result = service.finalise_note(note_id)

        assert result.status == NoteStatus.FINAL

    def test_finalise_nonexistent_note_raises(self, service: NoteService) -> None:
        """Finalising a non-existent note should raise NoteNotFoundError."""
        with pytest.raises(NoteNotFoundError):
            service.finalise_note("note-9999")

    def test_finalise_already_final_raises(self, service: NoteService) -> None:
        """Finalising an already-final note should raise ValueError."""
        note_id, _ = service.create_note(
            patient_id="patient-001",
            clinician_id="clinician-001",
            content="Patient is stable.",
        )
        service.finalise_note(note_id)

        with pytest.raises(ValueError, match="already finalised"):
            service.finalise_note(note_id)


class TestGetNote:
    """Tests for note retrieval."""

    def test_get_note_returns_correct_note(self, service: NoteService) -> None:
        """A saved note can be retrieved."""
        note_id, _ = service.create_note(
            patient_id="patient-001",
            clinician_id="clinician-001",
            content="Original content.",
        )

        retrieved = service.get_note(note_id)

        assert retrieved.content == "Original content."

    def test_get_nonexistent_note_raises(self, service: NoteService) -> None:
        """Getting a non-existent note should raise NoteNotFoundError."""
        with pytest.raises(NoteNotFoundError):
            service.get_note("note-0000")


class TestListNotes:
    """Tests for listing notes."""

    def test_list_notes_empty(self, service: NoteService) -> None:
        """Empty service should return empty list."""
        assert service.list_notes() == []

    def test_list_notes_returns_id_and_note_pairs(self, service: NoteService) -> None:
        """All created notes should appear with their IDs."""
        service.create_note("patient-001", "clinician-001", "First note.")
        service.create_note("patient-002", "clinician-001", "Second note.")

        results = service.list_notes()

        assert len(results) == 2
        assert results[0][0] == "note-0001"
        assert results[0][1].content == "First note."
        assert results[1][0] == "note-0002"
        assert results[1][1].content == "Second note."
