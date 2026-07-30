import React from 'react';
import { ShieldCheck, AlertTriangle, CheckCircle, Info, Award } from 'lucide-react';

export default function ConfidenceBar({ confidence, hallucinationReport, deepevalReport }) {
  const percentage = Math.round(confidence || 85);
  const risk = hallucinationReport?.risk_level || 'Low';
  const faithfulness = hallucinationReport?.faithfulness_score || 95.0;

  let riskClass = 'badge-risk-low';
  let Icon = CheckCircle;
  if (risk === 'Medium') {
    riskClass = 'badge-risk-medium';
    Icon = Info;
  } else if (risk === 'High') {
    riskClass = 'badge-risk-high';
    Icon = AlertTriangle;
  }

  return (
    <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.6rem', alignItems: 'center' }}>
      <div className="badge badge-confidence">
        <ShieldCheck size={14} />
        <span>Retrieval Confidence: {percentage}%</span>
      </div>

      {hallucinationReport && (
        <div
          className={`badge ${riskClass}`}
          title={`Faithfulness: ${faithfulness}% (${hallucinationReport.grounded_sentences}/${hallucinationReport.total_sentences} sentences grounded in literature)`}
        >
          <Icon size={14} />
          <span>Hallucination Risk: {risk} ({faithfulness}%)</span>
        </div>
      )}

      {deepevalReport && (
        <div
          className="badge"
          style={{
            background: 'rgba(139, 92, 246, 0.15)',
            border: '1px solid rgba(139, 92, 246, 0.4)',
            color: '#c4b5fd',
            display: 'flex',
            alignItems: 'center',
            gap: '0.4rem',
            padding: '0.35rem 0.75rem',
            borderRadius: '20px',
            fontSize: '0.78rem',
            fontWeight: '600'
          }}
          title={`DeepEval G-Eval Clinical Correctness: ${deepevalReport.g_eval_clinical_correctness}%`}
        >
          <Award size={14} color="#a78bfa" />
          <span>DeepEval: {deepevalReport.g_eval_clinical_correctness}% ({deepevalReport.status})</span>
        </div>
      )}
    </div>
  );
}
