import { Bot, User } from "lucide-react"
import { cn } from "@/lib/utils"
import { Confirmation } from "./Confirmation"
import { List } from "./List"
import { StatCard } from "./StatCard"

function mapListItems(
  items: unknown,
): Array<{ id?: string; title: string; subtitle?: string; value?: string }> {
  if (!Array.isArray(items)) return []
  return items.map((item: unknown) => {
    const obj = item as Record<string, unknown>
    return {
      id: obj.id != null ? String(obj.id) : undefined,
      title: String(obj.title ?? ""),
      subtitle: obj.subtitle != null ? String(obj.subtitle) : undefined,
      value: obj.value != null ? String(obj.value) : undefined,
    }
  })
}

export interface ChatMessageData {
  role: "user" | "assistant"
  content: string
  component?: "confirmation" | "stat-card" | "list" | null
  data?: Record<string, unknown>
}

interface ChatMessageProps {
  message: ChatMessageData
  className?: string
}

export function ChatMessage({ message, className }: ChatMessageProps) {
  const isUser = message.role === "user"

  return (
    <div className={cn("flex gap-3", isUser && "flex-row-reverse", className)}>
      <div
        className={cn(
          "flex h-8 w-8 shrink-0 items-center justify-center rounded-full",
          isUser ? "bg-primary text-primary-foreground" : "bg-muted",
        )}
      >
        {isUser ? <User className="h-4 w-4" /> : <Bot className="h-4 w-4" />}
      </div>

      <div className={cn("flex max-w-[80%] flex-col gap-2", isUser && "items-end")}>
        {/* Text message */}
        {message.content && (
          <div
            className={cn(
              "rounded-2xl px-4 py-2",
              isUser ? "bg-primary text-primary-foreground" : "bg-muted text-foreground",
            )}
          >
            <p className="text-sm">{message.content}</p>
          </div>
        )}

        {/* Generative UI Component */}
        {!isUser && message.component && (
          <div className="w-full">
            {message.component === "confirmation" && (
              <Confirmation message={message.content} data={message.data} />
            )}
            {message.component === "stat-card" && message.data && (
              <StatCard
                title={String(message.data.title ?? "")}
                value={String(message.data.value ?? "")}
                subtitle={message.data.subtitle ? String(message.data.subtitle) : undefined}
              />
            )}
            {message.component === "list" && Array.isArray(message.data?.items) ? (
              <List
                title={message.data?.title ? String(message.data.title) : undefined}
                items={mapListItems(message.data?.items)}
              />
            ) : null}
          </div>
        )}
      </div>
    </div>
  )
}
