"""Async service layer for clinical note operations with database backend."""

from app.clinical_note import ClinicalNote
from app.db_repository import PostgresNoteRepository


class AsyncNoteService:
    """Handles business logic for clinical note operations (async version).

    This service orchestrates between the domain model and the database repository.
    """

    def __init__(self, repository: PostgresNoteRepository) -> None:
        self._repository = repository

    async def create_note(
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

        note_id = await self._repository.save(note)
        return note_id, note

    async def finalise_note(self, note_id: str) -> ClinicalNote:
        """Finalise a note, locking it from further edits.

        Args:
            note_id: The ID of the note to finalise.

        Returns:
            The finalised note.

        Raises:
            NoteNotFoundError: If the note doesn't exist.
            ValueError: If the note is already finalised.
        """
        note = await self._repository.get_by_id(note_id)
        note.finalise()
        await self._repository.update_status(note_id, note.status)
        return note

    async def get_note(self, note_id: str) -> ClinicalNote:
        """Retrieve a note by ID.

        Args:
            note_id: The ID of the note to retrieve.

        Returns:
            The clinical note.

        Raises:
            NoteNotFoundError: If the note doesn't exist.
        """
        return await self._repository.get_by_id(note_id)

    async def list_notes(self) -> list[tuple[str, ClinicalNote]]:
        """Return all notes with their IDs.

        Returns:
            List of (note_id, note) tuples.
        """
        return await self._repository.list_all()
