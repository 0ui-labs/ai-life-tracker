import { Calendar, Check } from "lucide-react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { cn } from "@/lib/utils"

interface RoutineDay {
  day: string
  name: string
}

interface RoutineCardProps {
  name: string
  schedule?: string
  days?: RoutineDay[]
  isActive?: boolean
  className?: string
}

const DAY_LABELS: Record<string, string> = {
  montag: "Mo",
  dienstag: "Di",
  mittwoch: "Mi",
  donnerstag: "Do",
  freitag: "Fr",
  samstag: "Sa",
  sonntag: "So",
  monday: "Mo",
  tuesday: "Di",
  wednesday: "Mi",
  thursday: "Do",
  friday: "Fr",
  saturday: "Sa",
  sunday: "So",
}

function getShortDay(day: string): string {
  return DAY_LABELS[day.toLowerCase()] || day.slice(0, 2)
}

export function RoutineCard({
  name,
  schedule,
  days,
  isActive = false,
  className,
}: RoutineCardProps) {
  return (
    <Card className={cn("border-primary/30 bg-primary/5", className)}>
      <CardHeader className="pb-2">
        <div className="flex items-center justify-between">
          <CardTitle className="text-base font-medium">{name}</CardTitle>
          {isActive && (
            <span className="flex items-center gap-1 text-xs text-green-500">
              <Check className="h-3 w-3" />
              Aktiv
            </span>
          )}
        </div>
      </CardHeader>
      <CardContent className="space-y-3">
        {schedule && (
          <div className="flex items-center gap-2 text-sm text-muted-foreground">
            <Calendar className="h-4 w-4" />
            <span>{schedule}</span>
          </div>
        )}

        {days && days.length > 0 && (
          <div className="flex flex-wrap gap-2">
            {days.map((day) => (
              <div
                key={`${day.day}-${day.name}`}
                className="flex items-center gap-2 rounded-lg bg-muted px-3 py-1.5"
              >
                <span className="text-xs font-medium text-muted-foreground">
                  {getShortDay(day.day)}
                </span>
                <span className="text-sm font-medium">{day.name}</span>
              </div>
            ))}
          </div>
        )}
      </CardContent>
    </Card>
  )
}
