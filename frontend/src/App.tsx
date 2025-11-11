import ChatWindow from './components/ChatWindow'
import './App.css'

function App() {
  return (
    <div className="app">
      <header className="app-header">
        <h1>InMind</h1>
        <p>AI-Powered Product Recommendations</p>
      </header>
      
      <main className="app-main">
        <ChatWindow />
      </main>
      
      <footer className="app-footer">
        <p>Powered by Ollama & ChromaDB</p>
      </footer>
    </div>
  )
}

export default App
