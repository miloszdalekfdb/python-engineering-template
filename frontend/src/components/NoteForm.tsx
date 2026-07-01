import { useState } from 'react'
import type { ClinicalNote, CreateNoteRequest } from '../types/notes'

interface NoteFormProps {
  onSubmit: (request: CreateNoteRequest) => Promise<ClinicalNote>
}

export function NoteForm({ onSubmit }: NoteFormProps) {
  const [patientId, setPatientId] = useState('')
  const [clinicianId, setClinicianId] = useState('')
  const [content, setContent] = useState('')
  const [submitting, setSubmitting] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError(null)
    setSubmitting(true)

    try {
      await onSubmit({
        patient_id: patientId,
        clinician_id: clinicianId,
        content,
      })
      setPatientId('')
      setClinicianId('')
      setContent('')
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to create note')
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <form onSubmit={handleSubmit} className="bg-white border border-gray-200 rounded-lg p-6 mb-8 shadow-sm">
      <h2 className="text-lg font-semibold text-gray-800 mb-4">New Note</h2>

      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 px-3 py-2 rounded mb-4 text-sm">
          {error}
        </div>
      )}

      <div className="grid grid-cols-2 gap-4 mb-4">
        <div>
          <label htmlFor="patient-id" className="block text-sm font-medium text-gray-700 mb-1">
            Patient ID
          </label>
          <input
            id="patient-id"
            type="text"
            value={patientId}
            onChange={(e) => setPatientId(e.target.value)}
            className="w-full border border-gray-300 rounded px-3 py-2 text-sm"
            placeholder="patient-001"
            required
          />
        </div>
        <div>
          <label htmlFor="clinician-id" className="block text-sm font-medium text-gray-700 mb-1">
            Clinician ID
          </label>
          <input
            id="clinician-id"
            type="text"
            value={clinicianId}
            onChange={(e) => setClinicianId(e.target.value)}
            className="w-full border border-gray-300 rounded px-3 py-2 text-sm"
            placeholder="clinician-001"
            required
          />
        </div>
      </div>

      <div className="mb-4">
        <label htmlFor="content" className="block text-sm font-medium text-gray-700 mb-1">
          Clinical Note
        </label>
        <textarea
          id="content"
          value={content}
          onChange={(e) => setContent(e.target.value)}
          className="w-full border border-gray-300 rounded px-3 py-2 text-sm h-24 resize-none"
          placeholder="Patient presents with..."
          required
        />
      </div>

      <button
        type="submit"
        disabled={submitting}
        className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed text-sm font-medium"
      >
        {submitting ? 'Creating...' : 'Create Note'}
      </button>
    </form>
  )
}
