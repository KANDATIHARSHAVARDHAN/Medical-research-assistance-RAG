import React from 'react';
import { ExternalLink, ShieldCheck, Award } from 'lucide-react';

export default function CitationCard({ citation }) {
  if (!citation) return null;

  const scorePct = Math.round((citation.similarity_score || 0.85) * 100);
  const confidence = citation.confidence_level || (scorePct >= 80 ? 'High' : scorePct >= 65 ? 'Medium' : 'Low');

  return (
    <div className="citation-card-item">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '0.4rem' }}>
        <span style={{
          background: 'rgba(6, 182, 212, 0.15)',
          color: '#06b6d4',
          fontSize: '0.75rem',
          fontWeight: '700',
          padding: '0.15rem 0.5rem',
          borderRadius: '4px',
          display: 'flex',
          alignItems: 'center',
          gap: '0.3rem'
        }}>
          <Award size={12} /> [{citation.id}] {citation.source}
        </span>
        <span style={{
          fontSize: '0.72rem',
          color: confidence === 'High' ? '#10b981' : confidence === 'Medium' ? '#f59e0b' : '#ef4444',
          fontWeight: '700',
          display: 'flex',
          alignItems: 'center',
          gap: '0.2rem'
        }}>
          <ShieldCheck size={12} /> Score: {scorePct}% ({confidence})
        </span>
      </div>

      <div className="citation-title">{citation.title}</div>

      <div style={{ fontSize: '0.78rem', color: '#94a3b8', marginBottom: '0.5rem' }}>
        {citation.authors} • <em>{citation.journal}</em> ({citation.year})
      </div>

      <div className="citation-meta">
        <span style={{
          background: 'rgba(255, 255, 255, 0.05)',
          padding: '0.15rem 0.4rem',
          borderRadius: '4px',
          fontSize: '0.7rem',
          color: '#cbd5e1'
        }}>
          {citation.study_type}
        </span>

        {citation.url ? (
          <a
            href={citation.url}
            target="_blank"
            rel="noopener noreferrer"
            className="citation-link"
          >
            PMID / External Link <ExternalLink size={12} />
          </a>
        ) : (
          <span style={{ fontSize: '0.7rem', color: '#64748b' }}>Verified Medical Source</span>
        )}
      </div>
    </div>
  );
}
