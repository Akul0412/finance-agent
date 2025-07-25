import React, { useState } from 'react';
import './App.css';

function App() {
  const [question, setQuestion] = useState('');
  const [loading, setLoading] = useState(false);
  const [response, setResponse] = useState('');
  const [error, setError] = useState('');

  const handleSend = async () => {
    if (!question.trim()) return;
    setLoading(true);
    setError('');
    setResponse('');

    try {
      const res = await fetch('http://localhost:8000/ask', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ question })
      });

      const data = await res.json();
      setResponse(data.output || 'No response.');
    } catch (err) {
      setError('Something went wrong.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="modern-ui">
      <div className="query-card">
        <h1 className="title">Supplier Analytics AI</h1>
        <p className="description">Ask questions about your suppliers, bills, and payments</p>

        <textarea
          className="query-input"
          placeholder="Ask me anything about your database… e.g., 'Show me all customers from California'"
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
        />

        <button className="send-btn" onClick={handleSend} disabled={loading}>
          {loading ? 'Thinking...' : 'Send Query'}
        </button>

        {error && <p className="error">{error}</p>}
        {response && <div className="response">{response}</div>}
      </div>
    </div>
  );
}

export default App;
