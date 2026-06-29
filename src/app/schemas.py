"""Request and response schemas for the API."""

from datetime import datetime

from pydantic import BaseModel, Field


class CreateNoteRequest(BaseModel):
    """Schema for creating a new clinical note."""

    patient_id: str = Field(min_length=1, description="Unique patient identifier")
    clinician_id: str = Field(min_length=1, description="Unique clinician identifier")
    content: str = Field(min_length=1, description="The clinical note body text")


class NoteResponse(BaseModel):
    """Schema for returning a clinical note."""

    note_id: str
    patient_id: str
    clinician_id: str
    content: str
    status: str
    created_at: datetime
    word_count: int


class ErrorResponse(BaseModel):
    """Schema for error responses."""

    detail: str
