import { Check } from "lucide-react"
import { Card, CardContent } from "@/components/ui/card"
import { cn } from "@/lib/utils"

interface ConfirmationProps {
  message: string
  data?: Record<string, unknown>
  className?: string
}

export function Confirmation({ message, data, className }: ConfirmationProps) {
  return (
    <Card className={cn("border-green-500/50 bg-green-500/10", className)}>
      <CardContent className="flex items-center gap-3 p-4">
        <div className="flex h-8 w-8 items-center justify-center rounded-full bg-green-500/20">
          <Check className="h-5 w-5 text-green-500" />
        </div>
        <div className="flex-1">
          <p className="font-medium text-foreground">{message}</p>
          {data && (
            <div className="mt-1 flex flex-wrap gap-2">
              {Object.entries(data).map(([key, value]) => (
                <span
                  key={key}
                  className="rounded bg-muted px-2 py-0.5 text-xs text-muted-foreground"
                >
                  {key}: {String(value)}
                </span>
              ))}
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  )
}
