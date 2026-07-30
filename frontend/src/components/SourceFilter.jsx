import React from 'react';
import { Filter } from 'lucide-react';

export default function SourceFilter({ sources = [], setSources }) {
  const availableSources = [
    'PubMed',
    'ClinicalTrials',
    'openFDA',
    'DailyMed',
    'WHO',
    'CDC',
    'Guidelines'
  ];

  const handleSourceToggle = (sourceName) => {
    if (sources.includes(sourceName)) {
      setSources(sources.filter((s) => s !== sourceName));
    } else {
      setSources([...sources, sourceName]);
    }
  };

  return (
    <div className="filter-row" style={{ marginTop: '0.8rem', paddingTop: '0.8rem', borderTop: '1px solid var(--border-color)', display: 'flex', flexWrap: 'wrap', gap: '0.8rem', alignItems: 'center' }}>
      <span style={{ display: 'flex', alignItems: 'center', gap: '0.3rem', color: '#94a3b8', fontSize: '0.8rem', fontWeight: '600' }}>
        <Filter size={14} color="#06b6d4" /> Target Databases:
      </span>
      {availableSources.map((source) => (
        <label key={source} className="filter-checkbox" style={{ cursor: 'pointer', display: 'flex', alignItems: 'center', gap: '0.3rem', fontSize: '0.78rem', color: sources.includes(source) ? '#fff' : '#64748b' }}>
          <input
            type="checkbox"
            checked={sources.includes(source)}
            onChange={() => handleSourceToggle(source)}
            style={{ accentColor: '#06b6d4' }}
          />
          {source}
        </label>
      ))}
    </div>
  );
}
