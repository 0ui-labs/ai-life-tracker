import { createFileRoute } from "@tanstack/react-router"
import { Loader2, Send } from "lucide-react"
import { useCallback, useEffect, useRef, useState } from "react"
import { apiClient } from "@/api/client"
import { AuthUserButton } from "@/components/auth/AuthGuard"
import { ChatMessage, type ChatMessageData } from "@/components/generative"
import { Button } from "@/components/ui/button"
import { VoiceButton } from "@/components/voice/VoiceButton"

export const Route = createFileRoute("/")({
  component: HomePage,
})

interface ChatResponse {
  action: string
  message: string
  data?: Record<string, unknown>
  component?: "confirmation" | "stat-card" | "list" | null
  tracker?: string
}

type Message = ChatMessageData & {
  id: string
}

let messageIdCounter = 0
const generateId = () => `msg-${++messageIdCounter}`

function HomePage() {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: generateId(),
      role: "assistant",
      content:
        "Hey! Ich bin dein AI Life Tracker. Sag mir was du tracken willst oder starte ein Workout.",
    },
  ])
  const [inputValue, setInputValue] = useState("")
  const [isLoading, setIsLoading] = useState(false)
  const messagesEndRef = useRef<HTMLDivElement>(null)

  const scrollToBottom = useCallback(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" })
  }, [])

  useEffect(() => {
    scrollToBottom()
  }, [messages, scrollToBottom])

  const sendMessage = async (text: string) => {
    if (!text.trim() || isLoading) return

    const userMessage: Message = {
      id: generateId(),
      role: "user",
      content: text.trim(),
    }

    setMessages((prev) => [...prev, userMessage])
    setInputValue("")
    setIsLoading(true)

    try {
      const response = await apiClient<ChatResponse>("/chat", {
        method: "POST",
        body: JSON.stringify({ message: text.trim() }),
      })

      const assistantMessage: Message = {
        id: generateId(),
        role: "assistant",
        content: response.message,
        component: response.component,
        data: response.data,
      }

      setMessages((prev) => [...prev, assistantMessage])
    } catch {
      setMessages((prev) => [
        ...prev,
        {
          id: generateId(),
          role: "assistant" as const,
          content: "Sorry, da ist etwas schiefgelaufen. Bitte versuche es nochmal.",
        },
      ])
    } finally {
      setIsLoading(false)
    }
  }

  const handleVoiceTranscript = (transcript: string) => {
    if (transcript) {
      sendMessage(transcript)
    }
  }

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    sendMessage(inputValue)
  }

  return (
    <div className="flex h-screen flex-col bg-background">
      {/* Header */}
      <header className="flex items-center justify-between border-b border-border px-4 py-3">
        <h1 className="text-lg font-semibold">AI Life Tracker</h1>
        <div className="flex items-center gap-3">
          <span className="rounded-full bg-green-500/20 px-2 py-0.5 text-xs text-green-500">
            Online
          </span>
          <AuthUserButton />
        </div>
      </header>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4">
        <div className="mx-auto max-w-2xl space-y-4">
          {messages.map((message) => (
            <ChatMessage key={message.id} message={message} />
          ))}

          {isLoading && (
            <div className="flex items-center gap-2 text-muted-foreground">
              <Loader2 className="h-4 w-4 animate-spin" />
              <span className="text-sm">Denke nach...</span>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>
      </div>

      {/* Input Area */}
      <div className="border-t border-border p-4">
        <div className="mx-auto max-w-2xl">
          <div className="flex items-center gap-4">
            {/* Voice Button */}
            <VoiceButton onTranscript={handleVoiceTranscript} size="sm" />

            {/* Text Input */}
            <form onSubmit={handleSubmit} className="flex flex-1 gap-2">
              <input
                type="text"
                value={inputValue}
                onChange={(e) => setInputValue(e.target.value)}
                placeholder="Schreib etwas oder nutze Voice..."
                className="flex-1 rounded-lg border border-input bg-background px-4 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-ring"
                disabled={isLoading}
              />
              <Button type="submit" size="icon" disabled={!inputValue.trim() || isLoading}>
                <Send className="h-4 w-4" />
              </Button>
            </form>
          </div>
        </div>
      </div>
    </div>
  )
}
