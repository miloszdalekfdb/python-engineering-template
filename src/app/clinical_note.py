"""Clinical note domain model."""

from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum


class NoteStatus(Enum):
    """Possible states of a clinical note."""

    DRAFT = "draft"
    FINAL = "final"
    AMENDED = "amended"


@dataclass
class ClinicalNote:
    """Represents a single clinical consultation note.

    Attributes:
        patient_id: Unique identifier for the patient.
        clinician_id: Unique identifier for the clinician.
        content: The free-text body of the note.
        status: Current lifecycle state of the note.
        created_at: Timestamp when the note was created.
    """

    patient_id: str
    clinician_id: str
    content: str
    status: NoteStatus = NoteStatus.DRAFT
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    def finalise(self) -> None:
        """Mark the note as final. Cannot finalise an already-final note."""
        if self.status == NoteStatus.FINAL:
            raise ValueError("Note is already finalised.")
        self.status = NoteStatus.FINAL

    def word_count(self) -> int:
        """Return the number of words in the note content."""
        return len(self.content.split())
