"""FastAPI application and route handlers."""

from fastapi import Depends, FastAPI, HTTPException, status

from app.clinical_note import ClinicalNote
from app.repository import InMemoryNoteRepository, NoteNotFoundError
from app.schemas import CreateNoteRequest, ErrorResponse, NoteResponse
from app.service import NoteService

app = FastAPI(
    title="Clinical Notes API",
    description="API for managing clinical consultation notes.",
    version="0.1.0",
)


def get_repository() -> InMemoryNoteRepository:
    """Dependency provider for the note repository."""
    return _default_repository


def get_service(
    repository: InMemoryNoteRepository = Depends(get_repository),
) -> NoteService:
    """Dependency provider for the note service."""
    return NoteService(repository=repository)


# Default repository for production use
_default_repository = InMemoryNoteRepository()


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
def health_check() -> dict[str, str]:
    """Health check endpoint for monitoring."""
    return {"status": "healthy"}


@app.post(
    "/notes",
    response_model=NoteResponse,
    status_code=status.HTTP_201_CREATED,
    responses={422: {"model": ErrorResponse}},
)
def create_note(
    request: CreateNoteRequest,
    service: NoteService = Depends(get_service),
) -> NoteResponse:
    """Create a new clinical note."""
    try:
        note_id, note = service.create_note(
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
def get_note(
    note_id: str,
    service: NoteService = Depends(get_service),
) -> NoteResponse:
    """Retrieve a clinical note by ID."""
    try:
        note = service.get_note(note_id)
    except NoteNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        ) from e

    return _note_to_response(note_id, note)


@app.get("/notes", response_model=list[NoteResponse])
def list_notes(
    service: NoteService = Depends(get_service),
) -> list[NoteResponse]:
    """List all clinical notes."""
    notes = service.list_notes()
    return [_note_to_response(note_id, note) for note_id, note in notes]


@app.post(
    "/notes/{note_id}/finalise",
    response_model=NoteResponse,
    responses={404: {"model": ErrorResponse}, 422: {"model": ErrorResponse}},
)
def finalise_note(
    note_id: str,
    service: NoteService = Depends(get_service),
) -> NoteResponse:
    """Finalise a clinical note, locking it from further edits."""
    try:
        note = service.finalise_note(note_id)
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
