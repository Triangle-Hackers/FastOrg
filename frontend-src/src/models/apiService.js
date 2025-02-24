/* eslint-disable no-useless-catch */
import axios from 'axios';
import config from '../config/env';

const api = axios.create({
    baseURL: config.backendUrl,
    withCredentials: true,  // Ensures cookies and auth sessions are included
    headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'X-Requested-With': 'XMLHttpRequest',
    },
});

export const generateMQL = async (prompt, schema) => {
    try {
        const response = await api.post('/generate-mql', { prompt, schema });
        return response.data;
    } catch (error) {
        throw error;
    }
};

export default api;