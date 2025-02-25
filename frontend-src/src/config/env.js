const getBackendUrl = () => {
  return import.meta.env.VITE_BACKEND_URL || 'http://localhost:8000';
};

const getExternalUrl = () => {
  return import.meta.env.VITE_EXTERNAL_URL || 'http://localhost:8000';
};

export const config = {
  backendUrl: getBackendUrl(),
  externalUrl: getExternalUrl(),
};

export default config;