import { Edit2, Trash2 } from "lucide-react"
import type { Tracker } from "@/api/trackers"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"

interface TrackerCardProps {
  tracker: Tracker
  onEdit: (tracker: Tracker) => void
  onDelete: (tracker: Tracker) => void
}

const CATEGORY_COLORS: Record<string, string> = {
  fitness: "bg-blue-500/20 text-blue-500",
  health: "bg-green-500/20 text-green-500",
  habit: "bg-purple-500/20 text-purple-500",
  productivity: "bg-orange-500/20 text-orange-500",
  general: "bg-gray-500/20 text-gray-500",
}

export function TrackerCard({ tracker, onEdit, onDelete }: TrackerCardProps) {
  const categoryColor = CATEGORY_COLORS[tracker.category] || CATEGORY_COLORS.general

  return (
    <Card className="group relative transition-shadow hover:shadow-md">
      <CardHeader className="pb-2">
        <div className="flex items-start justify-between">
          <div className="flex items-center gap-2">
            {tracker.icon && <span className="text-xl">{tracker.icon}</span>}
            <CardTitle className="text-lg">{tracker.name}</CardTitle>
          </div>
          <div className="flex gap-1 opacity-0 transition-opacity group-hover:opacity-100">
            <Button
              variant="ghost"
              size="icon"
              className="h-8 w-8"
              onClick={() => onEdit(tracker)}
              title="Bearbeiten"
            >
              <Edit2 className="h-4 w-4" />
            </Button>
            <Button
              variant="ghost"
              size="icon"
              className="h-8 w-8 text-destructive hover:text-destructive"
              onClick={() => onDelete(tracker)}
              title="Löschen"
            >
              <Trash2 className="h-4 w-4" />
            </Button>
          </div>
        </div>
      </CardHeader>
      <CardContent>
        <span
          className={`inline-block rounded-full px-2 py-0.5 text-xs font-medium ${categoryColor}`}
        >
          {tracker.category}
        </span>
        {tracker.color && (
          <div
            className="mt-2 h-1 w-full rounded-full"
            style={{ backgroundColor: tracker.color }}
          />
        )}
      </CardContent>
    </Card>
  )
}
