import React, { useState } from 'react';
import { Copy, Download, Check, Clock, Cpu, FileText, Activity, ShieldAlert, GitCompare } from 'lucide-react';
import ConfidenceBar from './ConfidenceBar';

export default function ChatWindow({ answerData }) {
  const [copied, setCopied] = useState(false);

  if (!answerData) return null;

  const handleCopy = () => {
    const textToCopy = `QUESTION: ${answerData.query}\n\nCLINICAL SUMMARY:\n${answerData.clinical_summary}\n\nEVIDENCE SYNTHESIS:\n${answerData.evidence_synthesis}\n\nTREATMENT COMPARISON:\n${answerData.treatment_comparison || 'N/A'}\n\nCONTRAINDICATIONS:\n${answerData.contraindications || 'N/A'}`;
    navigator.clipboard.writeText(textToCopy);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleDownload = () => {
    const textToDownload = `# Medical Research Synthesis\n\n**Query:** ${answerData.query}\n**LLM Model:** ${answerData.llm_model_used}\n**Retrieval Confidence:** ${answerData.retrieval_confidence}%\n**Hallucination Risk:** ${answerData.hallucination_report?.risk_level}\n**DeepEval G-Eval Score:** ${answerData.deepeval_report?.g_eval_clinical_correctness || 'N/A'}%\n\n## Clinical Summary\n${answerData.clinical_summary}\n\n## Evidence Synthesis\n${answerData.evidence_synthesis}\n\n## Treatment Comparison\n${answerData.treatment_comparison || 'N/A'}\n\n## Contraindications & Precautions\n${answerData.contraindications || 'N/A'}\n`;
    
    const blob = new Blob([textToDownload], { type: 'text/markdown' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `medical_synthesis_${Date.now()}.md`;
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div className="answer-card">
      <div className="answer-header" style={{ marginBottom: '1.2rem', paddingBottom: '1rem', borderBottom: '1px solid var(--border-color)' }}>
        <div>
          <h2 style={{ fontSize: '1.25rem', color: '#fff', marginBottom: '0.5rem', display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
            <FileText size={20} color="#06b6d4" /> Evidence-Based Clinical Answer
          </h2>
          <div style={{ fontSize: '0.8rem', color: '#94a3b8', display: 'flex', gap: '1rem', alignItems: 'center', flexWrap: 'wrap' }}>
            <span style={{ display: 'flex', alignItems: 'center', gap: '0.3rem' }}>
              <Cpu size={14} color="#06b6d4" /> Model: <strong style={{ color: '#06b6d4' }}>{answerData.llm_model_used}</strong>
            </span>
            <span style={{ display: 'flex', alignItems: 'center', gap: '0.3rem' }}>
              <Clock size={14} /> Latency: <strong>{answerData.latency_ms} ms</strong>
            </span>
          </div>
        </div>

        <div style={{ display: 'flex', gap: '0.5rem', alignItems: 'center' }}>
          <button
            onClick={handleCopy}
            style={{ background: 'rgba(255,255,255,0.05)', border: '1px solid var(--border-color)', color: '#94a3b8', padding: '0.45rem 0.8rem', borderRadius: '6px', cursor: 'pointer', display: 'flex', alignItems: 'center', gap: '0.3rem', fontSize: '0.78rem', fontWeight: '600' }}
          >
            {copied ? <Check size={14} color="#10b981" /> : <Copy size={14} />}
            {copied ? 'Copied' : 'Copy Text'}
          </button>

          <button
            onClick={handleDownload}
            style={{ background: 'rgba(6,182,212,0.15)', border: '1px solid var(--border-active)', color: '#06b6d4', padding: '0.45rem 0.8rem', borderRadius: '6px', cursor: 'pointer', display: 'flex', alignItems: 'center', gap: '0.3rem', fontSize: '0.78rem', fontWeight: '600' }}
          >
            <Download size={14} /> Export MD
          </button>
        </div>
      </div>

      <div style={{ marginBottom: '1.5rem' }}>
        <ConfidenceBar
          confidence={answerData.retrieval_confidence}
          hallucinationReport={answerData.hallucination_report}
          deepevalReport={answerData.deepeval_report}
        />
      </div>

      {answerData.clinical_summary && (
        <div className="section-block">
          <div className="section-title" style={{ display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
            <Activity size={16} color="#06b6d4" /> Clinical Summary
          </div>
          <div className="section-text">{answerData.clinical_summary}</div>
        </div>
      )}

      {answerData.evidence_synthesis && (
        <div className="section-block">
          <div className="section-title" style={{ display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
            <FileText size={16} color="#3b82f6" /> Evidence Synthesis
          </div>
          <div className="section-text">{answerData.evidence_synthesis}</div>
        </div>
      )}

      {answerData.treatment_comparison && (
        <div className="section-block comparison">
          <div className="section-title" style={{ display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
            <GitCompare size={16} color="#8b5cf6" /> Treatment Comparison
          </div>
          <div className="section-text">{answerData.treatment_comparison}</div>
        </div>
      )}

      {answerData.contraindications && (
        <div className="section-block contraindications">
          <div className="section-title" style={{ display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
            <ShieldAlert size={16} color="#ef4444" /> Contraindications & Precautions
          </div>
          <div className="section-text">{answerData.contraindications}</div>
        </div>
      )}
    </div>
  );
}
