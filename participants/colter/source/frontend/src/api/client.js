async function request(path, options = {}) {
  const res = await fetch(path, {
    headers: { 'Content-Type': 'application/json', ...(options.headers || {}) },
    ...options,
  });
  if (!res.ok) {
    let detail;
    try {
      detail = await res.json();
    } catch (_) {
      detail = await res.text();
    }
    const err = new Error(`API ${res.status}`);
    err.status = res.status;
    err.detail = detail;
    throw err;
  }
  if (res.status === 204) return null;
  const ct = res.headers.get('Content-Type') || '';
  return ct.includes('application/json') ? res.json() : res;
}

export const api = {
  listTemplates: () => request('/api/templates'),
  getTemplate: (id) => request(`/api/templates/${id}`),
  saveTemplate: (doc) =>
    request(`/api/templates/${doc.id}`, {
      method: 'PUT',
      body: JSON.stringify(doc),
    }),
  createTemplate: (doc) =>
    request('/api/templates', { method: 'POST', body: JSON.stringify(doc) }),

  listPresentations: () => request('/api/presentations'),
  getPresentation: (id) => request(`/api/presentations/${id}`),
  createPresentation: (doc) =>
    request('/api/presentations', {
      method: 'POST',
      body: JSON.stringify(doc),
    }),
  savePresentation: (doc) =>
    request(`/api/presentations/${doc.id}`, {
      method: 'PUT',
      body: JSON.stringify(doc),
    }),
  deletePresentation: (id) =>
    request(`/api/presentations/${id}`, { method: 'DELETE' }),

  uploadAsset: async (file) => {
    const fd = new FormData();
    fd.append('file', file);
    const res = await fetch('/api/assets', { method: 'POST', body: fd });
    if (!res.ok) throw new Error(`Upload failed: ${res.status}`);
    return res.json();
  },

  exportPptxUrl: (id) => `/api/presentations/${id}/export/pptx`,
};
