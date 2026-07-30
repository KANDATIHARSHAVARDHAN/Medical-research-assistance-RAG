import React, { useState, useEffect } from 'react';
import Navbar from './components/Navbar';
import Home from './pages/Home';
import History from './pages/History';
import Dashboard from './pages/Dashboard';
import { searchMedicalEvidence } from './services/api';
import './index.css';

export default function App() {
  const [activeTab, setActiveTab] = useState('search'); // 'search' | 'history' | 'dashboard'
  const [query, setQuery] = useState('');
  const [selectedModel, setSelectedModel] = useState('llama-3.3-70b-versatile');
  const [sources, setSources] = useState(['PubMed', 'ClinicalTrials', 'openFDA', 'DailyMed', 'WHO', 'CDC', 'Guidelines']);
  const [loading, setLoading] = useState(false);
  const [statusMessage, setStatusMessage] = useState('');
  const [answerData, setAnswerData] = useState(null);
  const [history, setHistory] = useState([]);

  // Load search history from localStorage on initial mount
  useEffect(() => {
    try {
      const saved = localStorage.getItem('medical_rag_history');
      if (saved) {
        setHistory(JSON.parse(saved));
      }
    } catch (err) {
      console.error("Failed to load search history:", err);
    }
  }, []);

  const saveToHistory = (newAnswer) => {
    try {
      const updated = [newAnswer, ...history.filter(item => item.query !== newAnswer.query)].slice(0, 30);
      setHistory(updated);
      localStorage.setItem('medical_rag_history', JSON.stringify(updated));
    } catch (err) {
      console.error("Failed to save search history:", err);
    }
  };

  const handleClearHistory = () => {
    if (window.confirm("Are you sure you want to clear your clinical search history?")) {
      setHistory([]);
      localStorage.removeItem('medical_rag_history');
    }
  };

  const handleSelectHistory = (item) => {
    setQuery(item.query || '');
    setAnswerData(item);
    setActiveTab('search');
  };

  const handleSearch = async () => {
    if (!query.trim()) return;
    setLoading(true);
    setStatusMessage('Executing 0.5 Vector / 0.5 BM25 Hybrid Retrieval...');

    try {
      const data = await searchMedicalEvidence({
        query: query.trim(),
        model_name: selectedModel,
        llm_provider: selectedModel.includes('gemini') ? 'gemini' : selectedModel.includes('gpt') ? 'openai' : 'groq',
        sources: sources,
        top_k: 5
      });
      setAnswerData(data);
      saveToHistory(data);
    } catch (err) {
      alert("Medical Search failed: " + err.message);
    } finally {
      setLoading(false);
      setStatusMessage('');
    }
  };

  return (
    <div className="app-container">
      <Navbar activeTab={activeTab} setActiveTab={setActiveTab} />

      <main className="main-content" style={{ padding: '2rem 1.5rem', maxWidth: '1400px', margin: '0 auto' }}>
        {activeTab === 'search' && (
          <Home
            query={query}
            setQuery={setQuery}
            selectedModel={selectedModel}
            setSelectedModel={setSelectedModel}
            sources={sources}
            setSources={setSources}
            onSearch={handleSearch}
            loading={loading}
            statusMessage={statusMessage}
            answerData={answerData}
          />
        )}

        {activeTab === 'history' && (
          <History
            history={history}
            onSelectHistory={handleSelectHistory}
            onClearHistory={handleClearHistory}
          />
        )}

        {activeTab === 'dashboard' && (
          <Dashboard selectedModel={selectedModel} />
        )}
      </main>
    </div>
  );
}
