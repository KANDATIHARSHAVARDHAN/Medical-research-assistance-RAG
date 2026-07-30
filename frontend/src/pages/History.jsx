import React from 'react';
import { History as HistoryIcon, Clock, ShieldCheck, Cpu, ArrowRight, Trash2 } from 'lucide-react';

export default function History({ history = [], onSelectHistory, onClearHistory }) {
  if (!history || history.length === 0) {
    return (
      <div style={{ textAlign: 'center', padding: '5rem 1rem', background: 'rgba(15, 23, 42, 0.4)', borderRadius: '12px', border: '1px solid var(--border-color)', margin: '2rem auto', maxWidth: '700px' }}>
        <HistoryIcon size={40} color="#64748b" style={{ marginBottom: '1rem', opacity: 0.6 }} />
        <h3 style={{ fontSize: '1.2rem', color: '#fff', marginBottom: '0.4rem' }}>No Search History Yet</h3>
        <p style={{ fontSize: '0.85rem', color: '#94a3b8' }}>
          Your completed clinical inquiries and synthesized evidence reports will appear here for quick reference and comparison.
        </p>
      </div>
    );
  }

  return (
    <div className="history-page" style={{ maxWidth: '900px', margin: '1.5rem auto' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem', paddingBottom: '0.8rem', borderBottom: '1px solid var(--border-color)' }}>
        <div>
          <h2 style={{ fontSize: '1.3rem', color: '#fff', display: 'flex', alignItems: 'center', gap: '0.5rem', margin: 0 }}>
            <HistoryIcon color="#06b6d4" /> Clinical Search History
          </h2>
          <div style={{ fontSize: '0.82rem', color: '#94a3b8' }}>
            Review past evidence syntheses, model parameters, and verification scores ({history.length} records)
          </div>
        </div>

        <button
          onClick={onClearHistory}
          style={{ background: 'rgba(239, 68, 68, 0.15)', border: '1px solid rgba(239, 68, 68, 0.4)', color: '#f87171', padding: '0.45rem 0.9rem', borderRadius: '8px', cursor: 'pointer', display: 'flex', alignItems: 'center', gap: '0.4rem', fontSize: '0.78rem', fontWeight: '600' }}
        >
          <Trash2 size={14} /> Clear History
        </button>
      </div>

      <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
        {history.map((item, idx) => {
          const confPct = Math.round(item.retrieval_confidence || 85);
          const risk = item.hallucination_report?.risk_level || 'Low';

          return (
            <div
              key={idx}
              onClick={() => onSelectHistory(item)}
              style={{
                background: 'rgba(15, 23, 42, 0.75)',
                border: '1px solid var(--border-color)',
                borderRadius: '10px',
                padding: '1.2rem',
                cursor: 'pointer',
                transition: 'all 0.2s ease',
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center',
                gap: '1rem'
              }}
              onMouseEnter={(e) => { e.currentTarget.style.borderColor = '#06b6d4'; e.currentTarget.style.background = 'rgba(15, 23, 42, 0.95)'; }}
              onMouseLeave={(e) => { e.currentTarget.style.borderColor = 'var(--border-color)'; e.currentTarget.style.background = 'rgba(15, 23, 42, 0.75)'; }}
            >
              <div style={{ flex: 1 }}>
                <div style={{ display: 'flex', gap: '0.8rem', alignItems: 'center', marginBottom: '0.5rem', flexWrap: 'wrap' }}>
                  <span style={{ fontSize: '0.72rem', background: 'rgba(6, 182, 212, 0.15)', color: '#06b6d4', padding: '0.15rem 0.5rem', borderRadius: '4px', fontWeight: '700', display: 'flex', alignItems: 'center', gap: '0.3rem' }}>
                    <Cpu size={12} /> {item.llm_model_used}
                  </span>
                  <span style={{ fontSize: '0.72rem', color: confPct >= 80 ? '#10b981' : '#f59e0b', fontWeight: '700', display: 'flex', alignItems: 'center', gap: '0.2rem' }}>
                    <ShieldCheck size={12} /> Confidence: {confPct}%
                  </span>
                  <span style={{ fontSize: '0.72rem', color: risk === 'Low' ? '#10b981' : risk === 'Medium' ? '#f59e0b' : '#ef4444', fontWeight: '600' }}>
                    Risk: {risk}
                  </span>
                  <span style={{ fontSize: '0.7rem', color: '#64748b', display: 'flex', alignItems: 'center', gap: '0.2rem' }}>
                    <Clock size={12} /> {item.latency_ms} ms
                  </span>
                </div>

                <h4 style={{ fontSize: '1.05rem', color: '#fff', margin: '0 0 0.4rem 0', fontWeight: '600' }}>
                  {item.query}
                </h4>

                <p style={{ fontSize: '0.82rem', color: '#94a3b8', margin: 0, display: '-webkit-box', WebkitLineClamp: 2, WebkitBoxOrient: 'vertical', overflow: 'hidden' }}>
                  {item.clinical_summary || item.raw_answer}
                </p>
              </div>

              <div style={{ color: '#06b6d4', display: 'flex', alignItems: 'center', gap: '0.3rem', fontSize: '0.82rem', fontWeight: '700', whiteSpace: 'nowrap' }}>
                View Report <ArrowRight size={16} />
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
