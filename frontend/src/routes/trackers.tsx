import { createFileRoute, Link } from "@tanstack/react-router"
import { ArrowLeft, Loader2, Plus } from "lucide-react"
import { useCallback, useEffect, useState } from "react"
import {
  createTracker,
  deleteTracker,
  getTrackers,
  type Tracker,
  type TrackerCreate,
  type TrackerUpdate,
  updateTracker,
} from "@/api/trackers"
import { AuthUserButton } from "@/components/auth/AuthGuard"
import { TrackerCard } from "@/components/trackers/TrackerCard"
import { TrackerForm } from "@/components/trackers/TrackerForm"
import { Button } from "@/components/ui/button"

export const Route = createFileRoute("/trackers")({
  component: TrackersPage,
})

function TrackersPage() {
  const [trackers, setTrackers] = useState<Tracker[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  // Form state
  const [showForm, setShowForm] = useState(false)
  const [editingTracker, setEditingTracker] = useState<Tracker | undefined>()
  const [isSubmitting, setIsSubmitting] = useState(false)

  // Delete confirmation state
  const [deletingTracker, setDeletingTracker] = useState<Tracker | null>(null)

  const loadTrackers = useCallback(async () => {
    setIsLoading(true)
    setError(null)
    try {
      const data = await getTrackers()
      setTrackers(data)
    } catch (err) {
      setError(err instanceof Error ? err.message : "Fehler beim Laden der Tracker")
    } finally {
      setIsLoading(false)
    }
  }, [])

  useEffect(() => {
    loadTrackers()
  }, [loadTrackers])

  const handleCreate = () => {
    setEditingTracker(undefined)
    setShowForm(true)
  }

  const handleEdit = (tracker: Tracker) => {
    setEditingTracker(tracker)
    setShowForm(true)
  }

  const handleDeleteClick = (tracker: Tracker) => {
    setDeletingTracker(tracker)
  }

  const handleDeleteConfirm = async () => {
    if (!deletingTracker) return

    try {
      await deleteTracker(deletingTracker.id)
      setTrackers((prev) => prev.filter((t) => t.id !== deletingTracker.id))
      setDeletingTracker(null)
    } catch (err) {
      setError(err instanceof Error ? err.message : "Fehler beim Löschen")
    }
  }

  const handleSubmit = async (data: TrackerCreate | TrackerUpdate) => {
    setIsSubmitting(true)
    try {
      if (editingTracker) {
        // Update
        const updated = await updateTracker(editingTracker.id, data as TrackerUpdate)
        setTrackers((prev) => prev.map((t) => (t.id === updated.id ? updated : t)))
      } else {
        // Create
        const created = await createTracker(data as TrackerCreate)
        setTrackers((prev) => [...prev, created])
      }
      setShowForm(false)
      setEditingTracker(undefined)
    } catch (err) {
      setError(err instanceof Error ? err.message : "Fehler beim Speichern")
    } finally {
      setIsSubmitting(false)
    }
  }

  const handleCancel = () => {
    setShowForm(false)
    setEditingTracker(undefined)
  }

  return (
    <div className="flex min-h-screen flex-col bg-background">
      {/* Header */}
      <header className="flex items-center justify-between border-b border-border px-4 py-3">
        <div className="flex items-center gap-3">
          <Link to="/">
            <Button variant="ghost" size="icon">
              <ArrowLeft className="h-4 w-4" />
            </Button>
          </Link>
          <h1 className="text-lg font-semibold">Meine Tracker</h1>
        </div>
        <div className="flex items-center gap-3">
          <Button onClick={handleCreate} size="sm">
            <Plus className="mr-1 h-4 w-4" />
            Neu
          </Button>
          <AuthUserButton />
        </div>
      </header>

      {/* Content */}
      <main className="flex-1 p-4">
        <div className="mx-auto max-w-4xl">
          {/* Error */}
          {error && (
            <div className="mb-4 rounded-lg bg-destructive/10 p-3 text-sm text-destructive">
              {error}
              <button type="button" onClick={() => setError(null)} className="ml-2 underline">
                Schließen
              </button>
            </div>
          )}

          {/* Loading */}
          {isLoading ? (
            <div className="flex items-center justify-center py-12">
              <Loader2 className="h-6 w-6 animate-spin text-muted-foreground" />
            </div>
          ) : trackers.length === 0 ? (
            // Empty State
            <div className="py-12 text-center">
              <p className="mb-4 text-muted-foreground">Du hast noch keine Tracker erstellt.</p>
              <Button onClick={handleCreate}>
                <Plus className="mr-1 h-4 w-4" />
                Ersten Tracker erstellen
              </Button>
            </div>
          ) : (
            // Tracker Grid
            <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
              {trackers.map((tracker) => (
                <TrackerCard
                  key={tracker.id}
                  tracker={tracker}
                  onEdit={handleEdit}
                  onDelete={handleDeleteClick}
                />
              ))}
            </div>
          )}
        </div>
      </main>

      {/* Form Modal */}
      {showForm && (
        <TrackerForm
          tracker={editingTracker}
          onSubmit={handleSubmit}
          onCancel={handleCancel}
          isLoading={isSubmitting}
        />
      )}

      {/* Delete Confirmation Modal */}
      {deletingTracker && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4">
          <div className="w-full max-w-sm rounded-lg bg-card p-6 shadow-lg">
            <h3 className="mb-2 text-lg font-semibold">Tracker löschen?</h3>
            <p className="mb-4 text-sm text-muted-foreground">
              Bist du sicher, dass du "{deletingTracker.name}" löschen möchtest? Alle Einträge
              werden ebenfalls gelöscht.
            </p>
            <div className="flex gap-2">
              <Button variant="outline" className="flex-1" onClick={() => setDeletingTracker(null)}>
                Abbrechen
              </Button>
              <Button variant="destructive" className="flex-1" onClick={handleDeleteConfirm}>
                Löschen
              </Button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
