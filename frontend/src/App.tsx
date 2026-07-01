import { useNotes } from './hooks/useNotes'
import { NoteForm } from './components/NoteForm'
import { NoteCard } from './components/NoteCard'

function App() {
  const { notes, loading, error, createNote, finaliseNote } = useNotes()

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-3xl font-bold text-gray-900 mb-8">
          Clinical Notes
        </h1>

        <NoteForm onSubmit={createNote} />

        {error && (
          <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded mb-4">
            {error}
          </div>
        )}

        {loading ? (
          <p className="text-gray-500">Loading notes...</p>
        ) : notes.length === 0 ? (
          <p className="text-gray-500">No notes yet. Create one above.</p>
        ) : (
          <div className="space-y-4">
            {notes.map((note) => (
              <NoteCard
                key={note.note_id}
                note={note}
                onFinalise={finaliseNote}
              />
            ))}
          </div>
        )}
      </div>
    </div>
  )
}

export default App
