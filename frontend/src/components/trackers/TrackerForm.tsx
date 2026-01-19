import { X } from "lucide-react"
import { useState } from "react"
import type { Tracker, TrackerCreate, TrackerUpdate } from "@/api/trackers"
import { Button } from "@/components/ui/button"

interface TrackerFormProps {
  tracker?: Tracker
  onSubmit: (data: TrackerCreate | TrackerUpdate) => Promise<void>
  onCancel: () => void
  isLoading?: boolean
}

const CATEGORIES = [
  { value: "fitness", label: "Fitness" },
  { value: "health", label: "Gesundheit" },
  { value: "habit", label: "Gewohnheit" },
  { value: "productivity", label: "Produktivität" },
  { value: "general", label: "Allgemein" },
]

const ICONS = ["💪", "🏃", "🧘", "💊", "💧", "😴", "📚", "🎯", "✅", "⭐"]

export function TrackerForm({ tracker, onSubmit, onCancel, isLoading }: TrackerFormProps) {
  const [name, setName] = useState(tracker?.name || "")
  const [category, setCategory] = useState(tracker?.category || "general")
  const [icon, setIcon] = useState(tracker?.icon || "")
  const [color, setColor] = useState(tracker?.color || "#3b82f6")

  const isEdit = !!tracker

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!name.trim()) return

    const data = {
      name: name.trim(),
      category,
      icon: icon || null,
      color: color || null,
    }

    await onSubmit(data)
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4">
      <div className="w-full max-w-md rounded-lg bg-card p-6 shadow-lg">
        <div className="mb-4 flex items-center justify-between">
          <h2 className="text-lg font-semibold">
            {isEdit ? "Tracker bearbeiten" : "Neuer Tracker"}
          </h2>
          <Button variant="ghost" size="icon" onClick={onCancel}>
            <X className="h-4 w-4" />
          </Button>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          {/* Name */}
          <div>
            <label htmlFor="name" className="mb-1 block text-sm font-medium">
              Name
            </label>
            <input
              id="name"
              type="text"
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="z.B. Bankdrücken, Wasser, Meditation..."
              className="w-full rounded-lg border border-input bg-background px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-ring"
              required
            />
          </div>

          {/* Category */}
          <div>
            <label htmlFor="category" className="mb-1 block text-sm font-medium">
              Kategorie
            </label>
            <select
              id="category"
              value={category}
              onChange={(e) => setCategory(e.target.value)}
              className="w-full rounded-lg border border-input bg-background px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-ring"
            >
              {CATEGORIES.map((cat) => (
                <option key={cat.value} value={cat.value}>
                  {cat.label}
                </option>
              ))}
            </select>
          </div>

          {/* Icon */}
          <fieldset>
            <legend className="mb-1 block text-sm font-medium">Icon</legend>
            <div className="flex flex-wrap gap-2">
              {ICONS.map((emoji) => (
                <button
                  key={emoji}
                  type="button"
                  onClick={() => setIcon(emoji)}
                  className={`rounded-lg border p-2 text-xl transition-colors ${
                    icon === emoji ? "border-primary bg-primary/10" : "border-input hover:bg-muted"
                  }`}
                >
                  {emoji}
                </button>
              ))}
              {icon && !ICONS.includes(icon) && (
                <button
                  type="button"
                  onClick={() => setIcon(icon)}
                  className="rounded-lg border border-primary bg-primary/10 p-2 text-xl"
                >
                  {icon}
                </button>
              )}
              <button
                type="button"
                onClick={() => setIcon("")}
                className={`rounded-lg border p-2 text-sm text-muted-foreground transition-colors ${
                  icon === "" ? "border-primary bg-primary/10" : "border-input hover:bg-muted"
                }`}
              >
                Kein Icon
              </button>
            </div>
          </fieldset>

          {/* Color */}
          <div>
            <label htmlFor="color" className="mb-1 block text-sm font-medium">
              Farbe
            </label>
            <div className="flex items-center gap-2">
              <input
                id="color"
                type="color"
                value={color}
                onChange={(e) => setColor(e.target.value)}
                className="h-10 w-10 cursor-pointer rounded-lg border border-input"
              />
              <input
                type="text"
                value={color}
                onChange={(e) => setColor(e.target.value)}
                placeholder="#3b82f6"
                className="flex-1 rounded-lg border border-input bg-background px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-ring"
              />
            </div>
          </div>

          {/* Actions */}
          <div className="flex gap-2 pt-2">
            <Button type="button" variant="outline" onClick={onCancel} className="flex-1">
              Abbrechen
            </Button>
            <Button type="submit" className="flex-1" disabled={!name.trim() || isLoading}>
              {isLoading ? "Speichern..." : isEdit ? "Speichern" : "Erstellen"}
            </Button>
          </div>
        </form>
      </div>
    </div>
  )
}
