import React from 'react';
import { Search, Sparkles, Cpu } from 'lucide-react';
import SourceFilter from './SourceFilter';

export default function SearchBar({
  query,
  setQuery,
  selectedModel,
  setSelectedModel,
  sources,
  setSources,
  onSearch,
  loading
}) {
  const quickPrompts = [
    "What is first-line therapy for type 2 diabetes?",
    "SGLT2 inhibitors vs GLP-1RA in diabetic kidney disease",
    "Paxlovid contraindications and CYP3A4 statin interactions",
    "2024 AHA/ACC hypertension guidelines for Stage 2 CKD"
  ];

  return (
    <div className="search-card">
      <div className="search-controls-top">
        <div className="llm-selector-group">
          <Cpu size={16} color="#06b6d4" />
          <span className="llm-label">Selected LLM Model:</span>
          <select
            className="llm-dropdown"
            value={selectedModel}
            onChange={(e) => setSelectedModel(e.target.value)}
          >
            <option value="llama-3.3-70b-versatile">Groq Llama 3.3 70B (Recommended)</option>
            <option value="llama-3.1-8b-instant">Groq Llama 3.1 8B (Fast)</option>
            <option value="mixtral-8x7b-32768">Groq Mixtral 8x7B</option>
            <option value="gemma2-9b-it">Groq Gemma 2 9B</option>
            <option value="gemini-1.5-flash">Google Gemini 2.5/3.6</option>
            <option value="gpt-4o">OpenAI GPT-4o</option>
          </select>
        </div>

        <div style={{ fontSize: '0.8rem', color: '#64748b' }}>
          Hybrid Search Weight: <strong style={{ color: '#06b6d4' }}>0.5 Vector / 0.5 BM25</strong>
        </div>
      </div>

      <form onSubmit={(e) => { e.preventDefault(); onSearch(); }}>
        <div className="search-input-box">
          <Search className="search-icon" size={20} />
          <input
            type="text"
            className="search-input"
            placeholder="Ask evidence-based medical questions, treatment comparisons, contraindications..."
            value={query}
            onChange={(e) => setQuery(e.target.value)}
          />
          <button type="submit" className="search-submit-btn" disabled={loading}>
            <Sparkles size={16} />
            {loading ? 'Searching...' : 'Search Evidence'}
          </button>
        </div>
      </form>

      <div className="quick-prompts">
        <span style={{ fontSize: '0.78rem', color: '#64748b', alignSelf: 'center', marginRight: '0.3rem' }}>
          Quick Queries:
        </span>
        {quickPrompts.map((promptText, idx) => (
          <button
            key={idx}
            type="button"
            className="chip"
            onClick={() => { setQuery(promptText); }}
          >
            {promptText}
          </button>
        ))}
      </div>

      <SourceFilter sources={sources} setSources={setSources} />
    </div>
  );
}
