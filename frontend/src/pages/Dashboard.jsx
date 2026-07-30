import React from 'react';
import RagasDashboard from '../components/RagasDashboard';

export default function Dashboard({ selectedModel }) {
  return (
    <div className="page-dashboard">
      <RagasDashboard selectedModel={selectedModel} />
    </div>
  );
}
