import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { cn } from "@/lib/utils"

interface ListItem {
  id?: string
  title: string
  subtitle?: string
  value?: string | number
}

interface ListProps {
  title?: string
  items: ListItem[]
  className?: string
}

export function List({ title, items, className }: ListProps) {
  return (
    <Card className={cn("", className)}>
      {title && (
        <CardHeader className="pb-3">
          <CardTitle className="text-base">{title}</CardTitle>
        </CardHeader>
      )}
      <CardContent className={cn(!title && "pt-6")}>
        <ul className="space-y-3">
          {items.map((item, index) => (
            <li
              key={item.id ?? index}
              className="flex items-center justify-between border-b border-border pb-3 last:border-0 last:pb-0"
            >
              <div className="flex items-center gap-3">
                <div>
                  <p className="font-medium">{item.title}</p>
                  {item.subtitle && (
                    <p className="text-sm text-muted-foreground">{item.subtitle}</p>
                  )}
                </div>
              </div>
              {item.value !== undefined && <span className="font-semibold">{item.value}</span>}
            </li>
          ))}
        </ul>
      </CardContent>
    </Card>
  )
}
