import React from 'react';
import { Stethoscope, Search, BarChart3, History } from 'lucide-react';

export default function Navbar({ activeTab, setActiveTab }) {
  return (
    <header className="navbar">
      <div className="nav-brand">
        <div className="brand-icon">
          <Stethoscope size={22} />
        </div>
        <div>
          <div className="brand-title">Medical Research Assistant</div>
          <div className="brand-subtitle">Evidence-Based RAG • Hybrid Search • DeepEval & Hallucination Guardrails</div>
        </div>
      </div>

      <nav className="nav-tabs">
        <button
          className={`tab-btn ${activeTab === 'search' ? 'active' : ''}`}
          onClick={() => setActiveTab('search')}
        >
          <Search size={16} />
          Evidence Search
        </button>

        <button
          className={`tab-btn ${activeTab === 'history' ? 'active' : ''}`}
          onClick={() => setActiveTab('history')}
        >
          <History size={16} />
          Search History
        </button>

        <button
          className={`tab-btn ${activeTab === 'dashboard' ? 'active' : ''}`}
          onClick={() => setActiveTab('dashboard')}
        >
          <BarChart3 size={16} />
          RAGAS & DeepEval Dashboard
        </button>
      </nav>
    </header>
  );
}
