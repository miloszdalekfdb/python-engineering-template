"""Tests for clinical note repository."""

import pytest

from app.clinical_note import ClinicalNote, NoteStatus
from app.repository import InMemoryNoteRepository, NoteNotFoundError


@pytest.fixture
def repository() -> InMemoryNoteRepository:
    """Provide a fresh repository for each test."""
    return InMemoryNoteRepository()


@pytest.fixture
def sample_note() -> ClinicalNote:
    """Provide a sample clinical note."""
    return ClinicalNote(
        patient_id="patient-001",
        clinician_id="clinician-001",
        content="Patient presents with headache and nausea.",
    )


class TestRepositorySave:
    """Tests for saving notes."""

    def test_save_returns_id(
        self, repository: InMemoryNoteRepository, sample_note: ClinicalNote
    ) -> None:
        """Saving a note should return a string ID."""
        note_id = repository.save(sample_note)

        assert isinstance(note_id, str)
        assert note_id.startswith("note-")

    def test_save_increments_id(
        self, repository: InMemoryNoteRepository, sample_note: ClinicalNote
    ) -> None:
        """Each save should produce a unique, incrementing ID."""
        id_1 = repository.save(sample_note)
        id_2 = repository.save(sample_note)

        assert id_1 == "note-0001"
        assert id_2 == "note-0002"

    def test_save_increases_count(
        self, repository: InMemoryNoteRepository, sample_note: ClinicalNote
    ) -> None:
        """Count should reflect number of saved notes."""
        assert repository.count() == 0

        repository.save(sample_note)

        assert repository.count() == 1


class TestRepositoryGetById:
    """Tests for retrieving notes."""

    def test_get_by_id_returns_saved_note(
        self, repository: InMemoryNoteRepository, sample_note: ClinicalNote
    ) -> None:
        """A saved note can be retrieved by its ID."""
        note_id = repository.save(sample_note)

        retrieved = repository.get_by_id(note_id)

        assert retrieved.patient_id == "patient-001"
        assert retrieved.content == "Patient presents with headache and nausea."

    def test_get_by_id_not_found_raises_error(
        self, repository: InMemoryNoteRepository
    ) -> None:
        """Requesting a non-existent note should raise NoteNotFoundError."""
        with pytest.raises(NoteNotFoundError, match="note-9999"):
            repository.get_by_id("note-9999")

    def test_not_found_error_contains_note_id(
        self, repository: InMemoryNoteRepository
    ) -> None:
        """The exception should carry the missing note ID."""
        with pytest.raises(NoteNotFoundError) as exc_info:
            repository.get_by_id("note-missing")

        assert exc_info.value.note_id == "note-missing"


class TestRepositoryListAll:
    """Tests for listing notes."""

    def test_list_all_empty_repository(
        self, repository: InMemoryNoteRepository
    ) -> None:
        """An empty repository should return an empty list."""
        assert repository.list_all() == []

    def test_list_all_returns_saved_notes(
        self, repository: InMemoryNoteRepository
    ) -> None:
        """All saved notes should appear in the list."""
        note_1 = ClinicalNote(
            patient_id="patient-001",
            clinician_id="clinician-001",
            content="First note.",
        )
        note_2 = ClinicalNote(
            patient_id="patient-002",
            clinician_id="clinician-001",
            content="Second note.",
        )

        repository.save(note_1)
        repository.save(note_2)

        notes = repository.list_all()

        assert len(notes) == 2
