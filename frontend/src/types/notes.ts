export interface ClinicalNote {
  note_id: string
  patient_id: string
  clinician_id: string
  content: string
  status: 'draft' | 'final' | 'amended'
  created_at: string
  word_count: number
}

export interface CreateNoteRequest {
  patient_id: string
  clinician_id: string
  content: string
}
