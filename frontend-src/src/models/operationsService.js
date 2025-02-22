/* eslint-disable no-useless-catch */
import api from './apiService';

export const performOperation = async (operationName, payload = {}) => {
    try {
        const response = await api.post('/perform-operation', { operation: operationName, ...payload});
        return response.data;
    } catch (error) {
        throw error;
    }
}