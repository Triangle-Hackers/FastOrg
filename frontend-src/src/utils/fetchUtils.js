import config from '../config/env';

export const fetchWithConfig = async (endpoint, options = {}) => {
  const url = `${config.backendUrl}${endpoint}`;
  const defaultOptions = {
    credentials: 'include',
    headers: {
      'Content-Type': 'application/json',
      'Accept': 'application/json',
      'X-Requested-With': 'XMLHttpRequest',
    },
  };

  const response = await fetch(url, {
    ...defaultOptions,
    ...options,
    credentials: 'include',
    headers: {
      ...defaultOptions.headers,
      ...options.headers,
    },
  });

  return response;
};

export default fetchWithConfig; 