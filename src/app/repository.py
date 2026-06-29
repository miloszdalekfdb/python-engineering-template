"""Repository for clinical note persistence."""

from app.clinical_note import ClinicalNote


class NoteNotFoundError(Exception):
    """Raised when a requested note does not exist."""

    def __init__(self, note_id: str) -> None:
        super().__init__(f"Note '{note_id}' not found.")
        self.note_id = note_id


class InMemoryNoteRepository:
    """In-memory storage for clinical notes.

    This is a simple implementation useful for testing and prototyping.
    In production, this would be replaced with a database-backed repository.
    """

    def __init__(self) -> None:
        self._notes: dict[str, ClinicalNote] = {}
        self._next_id: int = 1

    def save(self, note: ClinicalNote) -> str:
        """Persist a note and return its ID."""
        note_id = f"note-{self._next_id:04d}"
        self._next_id += 1
        self._notes[note_id] = note
        return note_id

    def get_by_id(self, note_id: str) -> ClinicalNote:
        """Retrieve a note by its ID. Raises NoteNotFoundError if missing."""
        if note_id not in self._notes:
            raise NoteNotFoundError(note_id)
        return self._notes[note_id]

    def list_all(self) -> list[ClinicalNote]:
        """Return all stored notes."""
        return list(self._notes.values())

    def count(self) -> int:
        """Return the number of stored notes."""
        return len(self._notes)
