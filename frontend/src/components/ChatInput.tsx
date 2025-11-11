import { useState, FormEvent, KeyboardEvent } from 'react'
import './ChatInput.css'

interface ChatInputProps {
  onSendMessage: (message: string) => void
  disabled?: boolean
}

function ChatInput({ onSendMessage, disabled = false }: ChatInputProps) {
  const [message, setMessage] = useState('')

  const handleSubmit = (e: FormEvent) => {
    e.preventDefault()
    if (message.trim() && !disabled) {
      onSendMessage(message.trim())
      setMessage('')
    }
  }

  const handleKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSubmit(e)
    }
  }

  return (
    <form className="chat-input" onSubmit={handleSubmit}>
      <textarea
        value={message}
        onChange={(e) => setMessage(e.target.value)}
        onKeyDown={handleKeyDown}
        placeholder="Type your message... (Enter to send, Shift+Enter for new line)"
        disabled={disabled}
        rows={3}
      />
      <button type="submit" disabled={disabled || !message.trim()}>
        Send
      </button>
    </form>
  )
}

export default ChatInput