import './ChatMessage.css'

interface ChatMessageProps {
  message: string
  isUser: boolean
  intent?: string
  entities?: Record<string, string>
}

function ChatMessage({ message, isUser, intent, entities }: ChatMessageProps) {
  return (
    <div className={`chat-message ${isUser ? 'user' : 'assistant'}`}>
      <div className="message-content">
        <p>{message}</p>
        {!isUser && intent && (
          <div className="message-metadata">
            <span className="intent-badge">{intent}</span>
            {entities && Object.keys(entities).length > 0 && (
              <div className="entities">
                {Object.entries(entities).map(([key, value]) => (
                  <span key={key} className="entity-tag">
                    {key}: {value}
                  </span>
                ))}
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  )
}

export default ChatMessage