import React from 'react';
import SearchBar from '../components/SearchBar';
import LoadingSpinner from '../components/LoadingSpinner';
import ChatWindow from '../components/ChatWindow';
import EvidencePanel from '../components/EvidencePanel';

export default function Home({
  query,
  setQuery,
  selectedModel,
  setSelectedModel,
  sources,
  setSources,
  onSearch,
  loading,
  statusMessage,
  answerData
}) {
  return (
    <div className="page-workspace">
      <SearchBar
        query={query}
        setQuery={setQuery}
        selectedModel={selectedModel}
        setSelectedModel={setSelectedModel}
        sources={sources}
        setSources={setSources}
        onSearch={onSearch}
        loading={loading}
      />

      {loading && <LoadingSpinner statusMessage={statusMessage} />}

      {answerData && !loading && (
        <div className="results-grid" style={{ marginTop: '1.8rem', display: 'grid', gridTemplateColumns: '1fr 380px', gap: '1.5rem', alignItems: 'start' }}>
          <ChatWindow answerData={answerData} />
          <EvidencePanel
            evidenceList={answerData.evidence_list || []}
            citations={answerData.citations || []}
          />
        </div>
      )}

      {!answerData && !loading && (
        <div style={{ textAlign: 'center', padding: '4rem 1rem', color: '#64748b' }}>
          <h3 style={{ fontSize: '1.1rem', color: '#94a3b8', marginBottom: '0.4rem' }}>
            Ready for Evidence-Based Medical Inquiry
          </h3>
          <p style={{ fontSize: '0.85rem', maxWidth: '520px', margin: '0 auto' }}>
            Select your LLM model, toggle target medical databases (PubMed, ClinicalTrials, openFDA, DailyMed), and enter your clinical question above.
          </p>
        </div>
      )}
    </div>
  );
}
