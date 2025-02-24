const getBackendUrl = () => {
  // For Vite, environment variables must be prefixed with VITE_
  return import.meta.env.VITE_BACKEND_URL || 'http://localhost:8000';
};

export const config = {
  backendUrl: getBackendUrl(),
  // Add other environment-specific config here
};

export default config; 