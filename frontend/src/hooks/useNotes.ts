import { useState, useEffect, useCallback } from 'react'
import type { ClinicalNote, CreateNoteRequest } from '../types/notes'

const API_BASE = '/api'

export function useNotes() {
  const [notes, setNotes] = useState<ClinicalNote[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const fetchNotes = useCallback(async () => {
    try {
      setLoading(true)
      setError(null)
      const response = await fetch(`${API_BASE}/notes`)
      if (!response.ok) throw new Error('Failed to fetch notes')
      const data: ClinicalNote[] = await response.json()
      setNotes(data)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error')
    } finally {
      setLoading(false)
    }
  }, [])

  const createNote = useCallback(async (request: CreateNoteRequest) => {
    const response = await fetch(`${API_BASE}/notes`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(request),
    })
    if (!response.ok) {
      const err = await response.json()
      throw new Error(err.detail || 'Failed to create note')
    }
    const note: ClinicalNote = await response.json()
    setNotes((prev) => [...prev, note])
    return note
  }, [])

  const finaliseNote = useCallback(async (noteId: string) => {
    const response = await fetch(`${API_BASE}/notes/${noteId}/finalise`, {
      method: 'POST',
    })
    if (!response.ok) {
      const err = await response.json()
      throw new Error(err.detail || 'Failed to finalise note')
    }
    const updated: ClinicalNote = await response.json()
    setNotes((prev) =>
      prev.map((n) => (n.note_id === noteId ? updated : n))
    )
    return updated
  }, [])

  useEffect(() => {
    fetchNotes()
  }, [fetchNotes])

  return { notes, loading, error, createNote, finaliseNote, refresh: fetchNotes }
}
