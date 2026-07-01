"""PostgreSQL-backed repository for clinical notes."""

import uuid

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.clinical_note import ClinicalNote, NoteStatus
from app.models import NoteModel
from app.repository import NoteNotFoundError


class PostgresNoteRepository:
    """Database-backed storage for clinical notes.

    Uses SQLAlchemy async sessions to interact with PostgreSQL.
    """

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def save(self, note: ClinicalNote) -> str:
        """Persist a note and return its ID."""
        note_id = str(uuid.uuid4())

        db_note = NoteModel(
            id=note_id,
            patient_id=note.patient_id,
            clinician_id=note.clinician_id,
            content=note.content,
            status=note.status.value,
            created_at=note.created_at,
        )

        self._session.add(db_note)
        await self._session.commit()
        return note_id

    async def get_by_id(self, note_id: str) -> ClinicalNote:
        """Retrieve a note by its ID. Raises NoteNotFoundError if missing."""
        stmt = select(NoteModel).where(NoteModel.id == note_id)
        result = await self._session.execute(stmt)
        db_note = result.scalar_one_or_none()

        if db_note is None:
            raise NoteNotFoundError(note_id)

        return self._to_domain(db_note)

    async def update_status(self, note_id: str, status: NoteStatus) -> None:
        """Update the status of a note in the database."""
        stmt = (
            update(NoteModel).where(NoteModel.id == note_id).values(status=status.value)
        )
        await self._session.execute(stmt)
        await self._session.commit()

    async def list_all(self) -> list[tuple[str, ClinicalNote]]:
        """Return all stored notes as (id, note) pairs."""
        stmt = select(NoteModel).order_by(NoteModel.created_at)
        result = await self._session.execute(stmt)
        rows = result.scalars().all()

        return [(row.id, self._to_domain(row)) for row in rows]

    async def count(self) -> int:
        """Return the number of stored notes."""
        stmt = select(NoteModel)
        result = await self._session.execute(stmt)
        return len(result.scalars().all())

    @staticmethod
    def _to_domain(db_note: NoteModel) -> ClinicalNote:
        """Convert a database model to a domain model."""
        return ClinicalNote(
            patient_id=db_note.patient_id,
            clinician_id=db_note.clinician_id,
            content=db_note.content,
            status=NoteStatus(db_note.status),
            created_at=db_note.created_at,
        )
