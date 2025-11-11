🔷 Phase 9: Frontend Development with React
Step 1m: Create ChatWindow Component
📝 What we're doing:
Creating the main chat container component that manages messages and integrates ChatMessage and ChatInput.

📝 Create ONE File: frontend/src/components/ChatWindow.tsx (NEW)
typescriptimport { useState, useEffect, useRef } from 'react'
import ChatMessage from './ChatMessage'
import ChatInput from './ChatInput'
import { apiService } from '../services/api.service'
import './ChatWindow.css'

interface Message {
  id: string
  text: string
  isUser: boolean
  intent?: string
  entities?: Record<string, string>
}

function ChatWindow() {
  const [messages, setMessages] = useState<Message[]>([])
  const [conversationId, setConversationId] = useState<string | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const messagesEndRef = useRef<HTMLDivElement>(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  useEffect(() => {
    startNewConversation()
  }, [])

  const startNewConversation = async () => {
    try {
      setLoading(true)
      setError(null)
      const response = await apiService.startConversation('user-001')
      setConversationId(response.conversation_id)
      setMessages([
        {
          id: '0',
          text: response.message,
          isUser: false,
        },
      ])
    } catch (err) {
      setError('Failed to start conversation. Please refresh the page.')
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  const handleSendMessage = async (messageText: string) => {
    if (!conversationId) return

    const userMessage: Message = {
      id: Date.now().toString(),
      text: messageText,
      isUser: true,
    }

    setMessages((prev) => [...prev, userMessage])
    setLoading(true)
    setError(null)

    try {
      const response = await apiService.sendMessage(conversationId, messageText)
      
      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        text: response.response,
        isUser: false,
        intent: response.intent,
        entities: response.entities,
      }

      setMessages((prev) => [...prev, assistantMessage])
    } catch (err) {
      setError('Failed to send message. Please try again.')
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="chat-window">
      <div className="messages-container">
        {messages.map((msg) => (
          <ChatMessage
            key={msg.id}
            message={msg.text}
            isUser={msg.isUser}
            intent={msg.intent}
            entities={msg.entities}
          />
        ))}
        {loading && (
          <div className="loading-indicator">
            <span>Thinking...</span>
          </div>
        )}
        {error && <div className="error-message">{error}</div>}
        <div ref={messagesEndRef} />
      </div>
      <ChatInput onSendMessage={handleSendMessage} disabled={loading || !conversationId} />
    </div>
  )
}

export default ChatWindow