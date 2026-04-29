import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 300000,
  headers: {
    'Content-Type': 'multipart/form-data',
  },
});

export const generatePresentation = async (request) => {
  const formData = new FormData();
  formData.append('prompt', request.prompt);
  formData.append('num_slides', request.numSlides.toString());
  formData.append('style', request.style);
  formData.append('tone', request.tone);
  formData.append('include_images', request.includeImages.toString());
  formData.append('template_id', (request.templateId || 1).toString());

  if (request.document) {
    formData.append('document', request.document);
  }

  const response = await api.post('/api/generate', formData);
  return response.data;
};

export const downloadPresentation = async (sessionId) => {
  const response = await api.get(`/api/download/${sessionId}`, {
    responseType: 'blob',
  });
  return response.data;
};

export const checkHealth = async () => {
  try {
    const response = await api.get('/health');
    return response.status === 200;
  } catch {
    return false;
  }
};

export default api;