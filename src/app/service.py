"""Service layer for clinical note operations."""

from app.clinical_note import ClinicalNote
from app.repository import InMemoryNoteRepository


class NoteService:
    """Handles business logic for clinical note operations.

    This service orchestrates between the domain model and the repository,
    enforcing business rules that don't belong in either.
    """

    def __init__(self, repository: InMemoryNoteRepository) -> None:
        self._repository = repository

    def create_note(
        self,
        patient_id: str,
        clinician_id: str,
        content: str,
    ) -> tuple[str, ClinicalNote]:
        """Create and persist a new clinical note.

        Args:
            patient_id: The patient this note belongs to.
            clinician_id: The clinician authoring the note.
            content: The note body text.

        Returns:
            A tuple of (note_id, note).

        Raises:
            ValueError: If content is empty or patient/clinician IDs are blank.
        """
        if not patient_id.strip():
            raise ValueError("Patient ID cannot be empty.")
        if not clinician_id.strip():
            raise ValueError("Clinician ID cannot be empty.")
        if not content.strip():
            raise ValueError("Note content cannot be empty.")

        note = ClinicalNote(
            patient_id=patient_id.strip(),
            clinician_id=clinician_id.strip(),
            content=content.strip(),
        )

        note_id = self._repository.save(note)
        return note_id, note

    def finalise_note(self, note_id: str) -> ClinicalNote:
        """Finalise a note, locking it from further edits.

        Args:
            note_id: The ID of the note to finalise.

        Returns:
            The finalised note.

        Raises:
            NoteNotFoundError: If the note doesn't exist.
            ValueError: If the note is already finalised.
        """
        note = self._repository.get_by_id(note_id)
        note.finalise()
        return note

    def get_note(self, note_id: str) -> ClinicalNote:
        """Retrieve a note by ID.

        Args:
            note_id: The ID of the note to retrieve.

        Returns:
            The clinical note.

        Raises:
            NoteNotFoundError: If the note doesn't exist.
        """
        return self._repository.get_by_id(note_id)

    def list_notes(self) -> list[ClinicalNote]:
        """Return all notes.

        Returns:
            List of all clinical notes.
        """
        return self._repository.list_all()
