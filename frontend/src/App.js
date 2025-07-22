import React, { useState } from 'react';
import './App.css';
import logo from './centime.png';

function App() {
  const [question, setQuestion] = useState('');
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async () => {
    if (!question.trim()) return;

    const userMessage = { type: 'user', text: question };
    setMessages((prev) => [...prev, userMessage]);
    setLoading(true);
    setError('');
    setQuestion('');

    try {
      const res = await fetch('http://localhost:8000/ask', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ question: userMessage.text })
      });
      const data = await res.json();
      const botMessage = { type: 'bot', text: typeof data.output === 'object' ? data.output.content : data.output };
      setMessages((prev) => [...prev, botMessage]);
    } catch (err) {
      setError('Something went wrong.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="app">
      <header className="header">
        <img src={logo} alt="Centime Logo" className="logo" />
        <h1>Centime Supplier AI</h1>
      </header>

      <main className="main">
        <div className="chat-container">
          <div className="chat-box">
            {messages.map((msg, idx) => (
              <div key={idx} className={`chat-message ${msg.type}`}>
                {msg.text}
              </div>
            ))}
            {loading && <div className="chat-message bot loading">...</div>}
          </div>

          <div className="input-area">
            <textarea
              className="question-input"
              value={question}
              onChange={(e) => setQuestion(e.target.value)}
              placeholder="Ask me about your suppliers, spend, or payments..."
            />
            <button className="submit-btn" onClick={handleSubmit} disabled={loading}>
              {loading ? 'Thinking...' : 'Ask'}
            </button>
          </div>
          {error && <div className="error-text">{error}</div>}
        </div>
      </main>

      <footer className="footer">
        © 2025 Centime AI • Powered by LangChain + React
      </footer>
    </div>
  );
}

export default App;