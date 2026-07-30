import React, { useState } from 'react';
import { Layers, Award, BookOpen, BarChart2 } from 'lucide-react';
import CitationCard from './CitationCard';

export default function EvidencePanel({ evidenceList = [], citations = [] }) {
  const [activeView, setActiveView] = useState('citations'); // 'citations' | 'ranking'

  return (
    <div className="evidence-sidebar">
      <div className="sidebar-card">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem', flexWrap: 'wrap', gap: '0.5rem' }}>
          <h3 style={{ fontSize: '1rem', color: '#fff', display: 'flex', alignItems: 'center', gap: '0.4rem', margin: 0 }}>
            <Layers size={18} color="#06b6d4" /> Retrieved Evidence ({citations.length})
          </h3>

          <div style={{ display: 'flex', gap: '0.3rem', background: 'rgba(15,23,42,0.8)', padding: '0.2rem', borderRadius: '6px' }}>
            <button
              style={{
                fontSize: '0.72rem',
                padding: '0.3rem 0.6rem',
                borderRadius: '4px',
                border: 'none',
                background: activeView === 'citations' ? 'var(--accent-cyan)' : 'transparent',
                color: activeView === 'citations' ? '#000' : '#94a3b8',
                fontWeight: '600',
                cursor: 'pointer',
                display: 'flex',
                alignItems: 'center',
                gap: '0.3rem'
              }}
              onClick={() => setActiveView('citations')}
            >
              <BookOpen size={12} /> Citations
            </button>
            <button
              style={{
                fontSize: '0.72rem',
                padding: '0.3rem 0.6rem',
                borderRadius: '4px',
                border: 'none',
                background: activeView === 'ranking' ? 'var(--accent-cyan)' : 'transparent',
                color: activeView === 'ranking' ? '#000' : '#94a3b8',
                fontWeight: '600',
                cursor: 'pointer',
                display: 'flex',
                alignItems: 'center',
                gap: '0.3rem'
              }}
              onClick={() => setActiveView('ranking')}
            >
              <BarChart2 size={12} /> Rank Inspector
            </button>
          </div>
        </div>

        {activeView === 'citations' ? (
          <div>
            {citations.length === 0 ? (
              <div style={{ textAlign: 'center', padding: '2rem 1rem', color: '#64748b', fontSize: '0.85rem' }}>
                No citations retrieved yet. Submit a clinical query to search literature.
              </div>
            ) : (
              citations.map((citation) => (
                <CitationCard key={citation.id} citation={citation} />
              ))
            )}
          </div>
        ) : (
          <div>
            <div style={{ fontSize: '0.75rem', color: '#94a3b8', marginBottom: '0.8rem', background: 'rgba(255,255,255,0.02)', padding: '0.6rem', borderRadius: '6px', borderLeft: '3px solid #06b6d4' }}>
              Multi-Factor Reranking Formula: <br />
              <strong style={{ color: '#06b6d4' }}>0.5 Sim + 0.2 Recency + 0.2 Quality + 0.1 Citation</strong>
            </div>

            {evidenceList.map((item, idx) => (
              <div
                key={idx}
                style={{
                  background: 'rgba(15,23,42,0.8)',
                  border: '1px solid var(--border-color)',
                  borderRadius: '8px',
                  padding: '0.75rem',
                  marginBottom: '0.6rem'
                }}
              >
                <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.78rem', fontWeight: '700', color: '#fff', marginBottom: '0.4rem' }}>
                  <span>#{item.rank} {item.title ? item.title.substring(0, 38) + '...' : 'Evidence Chunk'}</span>
                  <span style={{ color: '#10b981', background: 'rgba(16,185,129,0.15)', padding: '0.1rem 0.4rem', borderRadius: '4px' }}>
                    {Math.round((item.overall_score || 0) * 100)}%
                  </span>
                </div>

                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.4rem', fontSize: '0.7rem', color: '#94a3b8', marginTop: '0.5rem' }}>
                  <div>Vector Score: <strong style={{ color: '#06b6d4' }}>{item.vector_score || 0}</strong></div>
                  <div>BM25 Score: <strong style={{ color: '#06b6d4' }}>{item.bm25_score || 0}</strong></div>
                  <div>Cross-Encoder: <strong style={{ color: '#8b5cf6' }}>{item.cross_encoder_score || 0}</strong></div>
                  <div>Study Quality: <strong style={{ color: '#f59e0b' }}>{item.study_quality_score || 0}</strong></div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
