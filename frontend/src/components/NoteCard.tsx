import type { ClinicalNote } from '../types/notes'

interface NoteCardProps {
  note: ClinicalNote
  onFinalise: (noteId: string) => Promise<ClinicalNote>
}

export function NoteCard({ note, onFinalise }: NoteCardProps) {
  const statusColor = note.status === 'final'
    ? 'bg-green-100 text-green-800'
    : 'bg-yellow-100 text-yellow-800'

  const handleFinalise = async () => {
    try {
      await onFinalise(note.note_id)
    } catch (err) {
      alert(err instanceof Error ? err.message : 'Failed to finalise')
    }
  }

  return (
    <div className="bg-white border border-gray-200 rounded-lg p-4 shadow-sm">
      <div className="flex justify-between items-start mb-2">
        <div className="flex gap-2 items-center">
          <span className={`px-2 py-1 rounded text-xs font-medium ${statusColor}`}>
            {note.status}
          </span>
          <span className="text-xs text-gray-500">
            {note.word_count} words
          </span>
        </div>
        {note.status === 'draft' && (
          <button
            onClick={handleFinalise}
            className="text-sm bg-blue-600 text-white px-3 py-1 rounded hover:bg-blue-700"
          >
            Finalise
          </button>
        )}
      </div>
      <p className="text-gray-800 mb-2">{note.content}</p>
      <div className="text-xs text-gray-400 flex gap-4">
        <span>Patient: {note.patient_id}</span>
        <span>Clinician: {note.clinician_id}</span>
        <span>{new Date(note.created_at).toLocaleString()}</span>
      </div>
    </div>
  )
}
