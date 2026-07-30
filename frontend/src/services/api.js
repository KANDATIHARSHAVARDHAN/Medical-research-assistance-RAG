const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

export async function searchMedicalEvidence(requestData) {
  const response = await fetch(`${API_BASE_URL}/api/search`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(requestData),
  });
  if (!response.ok) {
    throw new Error(`Server returned ${response.status}: ${await response.text()}`);
  }
  return await response.json();
}

export async function getRagasMetrics() {
  const response = await fetch(`${API_BASE_URL}/api/eval/metrics`);
  if (!response.ok) {
    throw new Error(`Metrics API error: ${response.statusText}`);
  }
  return await response.json();
}

export async function runRagasEvaluation(requestData = {}) {
  const response = await fetch(`${API_BASE_URL}/api/eval/run`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(requestData),
  });
  if (!response.ok) {
    throw new Error(`Eval API error: ${response.statusText}`);
  }
  return await response.json();
}
