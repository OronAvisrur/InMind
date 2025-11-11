import { useState } from 'react'
import './App.css'

function App() {
  const [conversationId, setConversationId] = useState<string | null>(null)

  return (
    <div className="app">
      <header className="app-header">
        <h1>InMind</h1>
        <p>AI-Powered Product Recommendations</p>
      </header>
      
      <main className="app-main">
        <div className="chat-container">
          <p>Chat interface coming soon...</p>
        </div>
      </main>
      
      <footer className="app-footer">
        <p>Powered by Ollama & ChromaDB</p>
      </footer>
    </div>
  )
}

export default App