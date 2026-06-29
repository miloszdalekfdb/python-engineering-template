"""Tests for clinical note domain model."""

import pytest

from app.clinical_note import ClinicalNote, NoteStatus


class TestClinicalNoteCreation:
    """Tests for creating clinical notes."""

    def test_create_note_with_required_fields(self) -> None:
        """A note can be created with just patient, clinician, and content."""
        note = ClinicalNote(
            patient_id="patient-123",
            clinician_id="clinician-456",
            content="Patient presents with a sore throat.",
        )

        assert note.patient_id == "patient-123"
        assert note.clinician_id == "clinician-456"
        assert note.content == "Patient presents with a sore throat."

    def test_default_status_is_draft(self) -> None:
        """New notes should always start as drafts."""
        note = ClinicalNote(
            patient_id="patient-123",
            clinician_id="clinician-456",
            content="Some content.",
        )

        assert note.status == NoteStatus.DRAFT

    def test_created_at_is_set_automatically(self) -> None:
        """Timestamp should be set without manual input."""
        note = ClinicalNote(
            patient_id="patient-123",
            clinician_id="clinician-456",
            content="Some content.",
        )

        assert note.created_at is not None


class TestClinicalNoteFinalise:
    """Tests for the finalise workflow."""

    def test_finalise_changes_status_to_final(self) -> None:
        """A draft note can be finalised."""
        note = ClinicalNote(
            patient_id="patient-123",
            clinician_id="clinician-456",
            content="Patient is well.",
        )

        note.finalise()

        assert note.status == NoteStatus.FINAL

    def test_finalise_already_final_raises_error(self) -> None:
        """Finalising an already-final note should raise ValueError."""
        note = ClinicalNote(
            patient_id="patient-123",
            clinician_id="clinician-456",
            content="Patient is well.",
        )
        note.finalise()

        with pytest.raises(ValueError, match="already finalised"):
            note.finalise()


class TestClinicalNoteWordCount:
    """Tests for word count functionality."""

    def test_word_count_simple_sentence(self) -> None:
        """Counts words in a normal sentence."""
        note = ClinicalNote(
            patient_id="patient-123",
            clinician_id="clinician-456",
            content="Patient presents with chest pain",
        )

        assert note.word_count() == 5

    def test_word_count_empty_content(self) -> None:
        """Empty content should return zero words."""
        note = ClinicalNote(
            patient_id="patient-123",
            clinician_id="clinician-456",
            content="",
        )

        assert note.word_count() == 0
