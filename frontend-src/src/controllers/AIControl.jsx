import React, { useState } from 'react';
import axios from 'axios';
import AIRequest from '../views/AIRequest';

const AIController = () => {
    /* Set states for api ai input vars */
    const [request, setRequest] = useState('');
    const [result, setResult] = useState(null);
    const [error, setError] = useState(null);
    const [loading, setLoading] = useState(false);

    const handleAIRequest = async () => {
        if (!request.trim()) return;
        setLoading(true);
        setError(null);

        try {
            /* Grabs response from api */
            const response = await axios.post('API ENDPOINT HERE', { request });
            setResult(response.data);
        } catch (err) {
            setError('There was an error processing your command.');
        } finally {
            setLoading(false);
            setRequest('');
        }
    };

    return (
        <AIRequest
            request={request}
            setRequest={setRequest}
            handleAIRequest={handleAIRequest}
            result={result}
            error={error}
            loading={loading}
        />
    );
};

export default AIController;