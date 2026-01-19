import { Loader2, Mic, MicOff } from "lucide-react"
import { useRef } from "react"
import { Button } from "@/components/ui/button"
import { useVoice } from "@/hooks/useVoice"
import { cn } from "@/lib/utils"

interface VoiceButtonProps {
  onTranscript?: (transcript: string) => void
  onListeningChange?: (isListening: boolean) => void
  className?: string
  size?: "default" | "lg" | "sm"
}

export function VoiceButton({
  onTranscript,
  onListeningChange,
  className,
  size = "default",
}: VoiceButtonProps) {
  const { isListening, transcript, error, startListening, stopListening } = useVoice()
  const sessionStartedRef = useRef(false)

  const handleClick = () => {
    if (isListening) {
      stopListening()
      // Only forward transcript if it was captured during this session
      if (transcript && onTranscript && sessionStartedRef.current) {
        onTranscript(transcript)
      }
      sessionStartedRef.current = false
    } else {
      sessionStartedRef.current = true
      startListening()
    }
    onListeningChange?.(!isListening)
  }

  const sizeClasses = {
    sm: "h-12 w-12",
    default: "h-16 w-16",
    lg: "h-20 w-20",
  }

  const iconSizes = {
    sm: "h-5 w-5",
    default: "h-6 w-6",
    lg: "h-8 w-8",
  }

  return (
    <div className="flex flex-col items-center gap-2">
      <Button
        type="button"
        variant={isListening ? "destructive" : "default"}
        size="icon"
        onClick={handleClick}
        className={cn(
          "rounded-full transition-all duration-200",
          sizeClasses[size],
          isListening && "animate-pulse ring-4 ring-destructive/30",
          className,
        )}
      >
        {isListening ? <MicOff className={iconSizes[size]} /> : <Mic className={iconSizes[size]} />}
      </Button>

      {isListening && (
        <div className="flex items-center gap-2 text-sm text-muted-foreground">
          <Loader2 className="h-4 w-4 animate-spin" />
          <span>Listening...</span>
        </div>
      )}

      {transcript && !isListening && (
        <p className="max-w-xs text-center text-sm text-muted-foreground">"{transcript}"</p>
      )}

      {error && <p className="text-sm text-destructive">{error}</p>}
    </div>
  )
}
