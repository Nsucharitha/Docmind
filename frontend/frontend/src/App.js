import React, { useState, useRef, useEffect } from 'react';
import axios from 'axios';
import ReactMarkdown from 'react-markdown';

const API = 'http://localhost:8000';

export default function App() {
  const [docs, setDocs] = useState([]);
  const [activeDoc, setActiveDoc] = useState(null);
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [uploading, setUploading] = useState(false);
  const [loading, setLoading] = useState(false);
  const fileInputRef = useRef();
  const messagesEndRef = useRef();

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleFile = async (file) => {
    if (!file || !file.name.endsWith('.pdf')) {
      alert('Only PDF files supported!');
      return;
    }
    setUploading(true);
    const form = new FormData();
    form.append('file', file);
    try {
      const { data } = await axios.post(`${API}/upload`, form);
      const doc = { id: data.doc_id, name: data.filename };
      setDocs(prev => [...prev, doc]);
      setActiveDoc(doc);
      setMessages([{ role: 'assistant', text: `✅ **"${data.filename}"** indexed! Ask me anything about it.`, sources: [] }]);
    } catch (e) {
      alert('Upload failed: ' + e.message);
    } finally {
      setUploading(false);
    }
  };

  const sendMessage = async () => {
    const q = input.trim();
    if (!q || !activeDoc || loading) return;
    setInput('');
    setMessages(prev => [...prev, { role: 'user', text: q, sources: [] }]);
    setLoading(true);
    try {
      const { data } = await axios.post(`${API}/query`, {
        question: q,
        doc_id: activeDoc.id
      });
      setMessages(prev => [...prev, { role: 'assistant', text: data.answer, sources: data.sources }]);
    } catch (e) {
      setMessages(prev => [...prev, { role: 'assistant', text: '❌ Error: ' + e.message, sources: [] }]);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); sendMessage(); }
  };

  return (
    <div style={{ display: 'flex', height: '100vh', fontFamily: 'sans-serif', background: '#0f172a', color: '#e2e8f0' }}>
      
      {/* Sidebar */}
      <div style={{ width: 260, background: '#1e293b', padding: 20, display: 'flex', flexDirection: 'column', gap: 16 }}>
        <div style={{ fontSize: 22, fontWeight: 700, color: '#60a5fa' }}>🧠 DocMind</div>
        <div style={{ fontSize: 12, color: '#64748b' }}>AI document assistant</div>

        <button
          onClick={() => fileInputRef.current.click()}
          disabled={uploading}
          style={{ background: '#2563eb', color: '#fff', border: 'none', borderRadius: 8, padding: '10px 16px', cursor: 'pointer', fontSize: 14 }}
        >
          {uploading ? '⏳ Indexing...' : '📄 Upload PDF'}
        </button>
        <input ref={fileInputRef} type="file" accept=".pdf" style={{ display: 'none' }}
          onChange={e => handleFile(e.target.files[0])} />

        {/* Doc list */}
        {docs.map(doc => (
          <div key={doc.id}
            onClick={() => setActiveDoc(doc)}
            style={{ padding: '8px 12px', borderRadius: 8, cursor: 'pointer', fontSize: 13,
              background: activeDoc?.id === doc.id ? '#1e3a5f' : 'transparent' }}>
            📑 {doc.name}
          </div>
        ))}
      </div>

      {/* Chat area */}
      <div style={{ flex: 1, display: 'flex', flexDirection: 'column' }}>
        
        {/* Header */}
        <div style={{ padding: '16px 24px', borderBottom: '1px solid #1e293b', fontSize: 15, fontWeight: 600 }}>
          {activeDoc ? activeDoc.name : '👋 Upload a PDF to get started'}
        </div>

        {/* Messages */}
        <div style={{ flex: 1, overflowY: 'auto', padding: 24, display: 'flex', flexDirection: 'column', gap: 16 }}>
          {messages.map((msg, i) => (
            <div key={i} style={{ display: 'flex', justifyContent: msg.role === 'user' ? 'flex-end' : 'flex-start' }}>
              <div style={{
                maxWidth: '70%', padding: '12px 16px', borderRadius: 12, fontSize: 14, lineHeight: 1.6,
                background: msg.role === 'user' ? '#2563eb' : '#1e293b'
              }}>
                <ReactMarkdown>{msg.text}</ReactMarkdown>
                {msg.sources?.length > 0 && (
                  <div style={{ marginTop: 8, fontSize: 11, color: '#64748b', borderTop: '1px solid #334155', paddingTop: 8 }}>
                    📌 {msg.sources.join(' · ')}
                  </div>
                )}
              </div>
            </div>
          ))}
          {loading && (
            <div style={{ display: 'flex', justifyContent: 'flex-start' }}>
              <div style={{ background: '#1e293b', padding: '12px 16px', borderRadius: 12, fontSize: 14 }}>⏳ Thinking...</div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        {/* Input */}
        <div style={{ padding: '16px 24px', borderTop: '1px solid #1e293b', display: 'flex', gap: 12 }}>
          <textarea
            rows={2}
            value={input}
            onChange={e => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            disabled={!activeDoc || loading}
            placeholder={activeDoc ? 'Ask a question...' : 'Upload a PDF first...'}
            style={{ flex: 1, background: '#1e293b', border: '1px solid #334155', borderRadius: 8, padding: '10px 14px', color: '#e2e8f0', fontSize: 14, resize: 'none', outline: 'none' }}
          />
          <button onClick={sendMessage} disabled={!activeDoc || loading || !input.trim()}
            style={{ background: '#2563eb', border: 'none', borderRadius: 8, padding: '0 20px', color: '#fff', fontSize: 18, cursor: 'pointer' }}>
            ➤
          </button>
        </div>
      </div>
    </div>
  );
}