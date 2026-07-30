import React from 'react';
import { Sparkles, Cpu, Layers } from 'lucide-react';

export default function LoadingSpinner({ statusMessage = '' }) {
  return (
    <div style={{ textAlign: 'center', margin: '3.5rem 0', padding: '2rem', background: 'rgba(15, 23, 42, 0.6)', borderRadius: '12px', border: '1px dashed var(--border-color)', maxWidth: '600px', marginLeft: 'auto', marginRight: 'auto' }}>
      <div className="pulse-loader" style={{ marginBottom: '1.2rem', marginLeft: 'auto', marginRight: 'auto' }}></div>
      <h3 style={{ fontSize: '1.05rem', fontWeight: '700', color: '#fff', marginBottom: '0.4rem', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '0.4rem' }}>
        <Sparkles size={18} color="#06b6d4" /> Evidence-Aware RAG Pipeline Active
      </h3>
      <div style={{ fontSize: '0.88rem', color: '#06b6d4', fontWeight: '600', marginBottom: '1rem' }}>
        {statusMessage || 'Executing 0.5 Vector / 0.5 BM25 Hybrid Retrieval & Cross-Encoder Reranking...'}
      </div>

      <div style={{ display: 'flex', justifyContent: 'center', gap: '1.5rem', fontSize: '0.75rem', color: '#64748b' }}>
        <span style={{ display: 'flex', alignItems: 'center', gap: '0.3rem' }}><Layers size={14} /> BGE-M3 / PubMedBERT</span>
        <span style={{ display: 'flex', alignItems: 'center', gap: '0.3rem' }}><Cpu size={14} /> Cross-Encoder MiniLM</span>
      </div>
    </div>
  );
}
