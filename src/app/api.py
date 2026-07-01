"""FastAPI application and route handlers."""

from fastapi import Depends, FastAPI, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.async_service import AsyncNoteService
from app.clinical_note import ClinicalNote
from app.database import get_db_session
from app.db_repository import PostgresNoteRepository
from app.repository import NoteNotFoundError
from app.schemas import CreateNoteRequest, ErrorResponse, NoteResponse

app = FastAPI(
    title="Clinical Notes API",
    description="API for managing clinical consultation notes.",
    version="0.1.0",
)


def get_repository(
    session: AsyncSession = Depends(get_db_session),
) -> PostgresNoteRepository:
    """Dependency provider for the note repository."""
    return PostgresNoteRepository(session=session)


def get_service(
    repository: PostgresNoteRepository = Depends(get_repository),
) -> AsyncNoteService:
    """Dependency provider for the note service."""
    return AsyncNoteService(repository=repository)


def _note_to_response(note_id: str, note: ClinicalNote) -> NoteResponse:
    """Convert a domain note to an API response."""
    return NoteResponse(
        note_id=note_id,
        patient_id=note.patient_id,
        clinician_id=note.clinician_id,
        content=note.content,
        status=note.status.value,
        created_at=note.created_at,
        word_count=note.word_count(),
    )


@app.get("/health", status_code=status.HTTP_200_OK)
async def health_check() -> dict[str, str]:
    """Health check endpoint for monitoring."""
    return {"status": "healthy"}


@app.post(
    "/notes",
    response_model=NoteResponse,
    status_code=status.HTTP_201_CREATED,
    responses={422: {"model": ErrorResponse}},
)
async def create_note(
    request: CreateNoteRequest,
    service: AsyncNoteService = Depends(get_service),
) -> NoteResponse:
    """Create a new clinical note."""
    try:
        note_id, note = await service.create_note(
            patient_id=request.patient_id,
            clinician_id=request.clinician_id,
            content=request.content,
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=str(e),
        ) from e

    return _note_to_response(note_id, note)


@app.get(
    "/notes/{note_id}",
    response_model=NoteResponse,
    responses={404: {"model": ErrorResponse}},
)
async def get_note(
    note_id: str,
    service: AsyncNoteService = Depends(get_service),
) -> NoteResponse:
    """Retrieve a clinical note by ID."""
    try:
        note = await service.get_note(note_id)
    except NoteNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        ) from e

    return _note_to_response(note_id, note)


@app.get("/notes", response_model=list[NoteResponse])
async def list_notes(
    service: AsyncNoteService = Depends(get_service),
) -> list[NoteResponse]:
    """List all clinical notes."""
    notes = await service.list_notes()
    return [_note_to_response(note_id, note) for note_id, note in notes]


@app.post(
    "/notes/{note_id}/finalise",
    response_model=NoteResponse,
    responses={404: {"model": ErrorResponse}, 422: {"model": ErrorResponse}},
)
async def finalise_note(
    note_id: str,
    service: AsyncNoteService = Depends(get_service),
) -> NoteResponse:
    """Finalise a clinical note, locking it from further edits."""
    try:
        note = await service.finalise_note(note_id)
    except NoteNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        ) from e
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=str(e),
        ) from e

    return _note_to_response(note_id, note)
