import React, { useState, useEffect } from 'react';
import axios from 'axios';
import AIRequest from '../views/AIRequest';

const AIController = () => {
    /* Set states for api ai input vars */
    const [request, setRequest] = useState('');
    const [result, setResult] = useState(null);
    const [error, setError] = useState(null);
    const [loading, setLoading] = useState(false);
    const [orgName, setOrgName] = useState(null);

    useEffect(() => {
        const fetchOrgName = async () => {
            try {
                const token = localStorage.getItem('access_token'); // Get token from storage
                const response = await axios.get('http://127.0.0.1:8000/get-org-name', {
                    withCredentials: true,
                    headers: {
                        'Authorization': `Bearer ${token}`,
                        'Content-Type': 'application/json'
                    }
                });
                
                if (response.data && response.data.org_name) {
                    setOrgName(response.data.org_name);
                } else {
                    setError('Failed to fetch organization name');
                }
            } catch (err) {
                console.error('Error fetching organization name:', err);
                setError('Error fetching organization details');
            }
        };
        fetchOrgName();
    }, []);

    const handleAIRequest = async () => {
        if (!request.trim()) return;
        if (!orgName) {
            setError("Please join an organization first");
            return;
        }

        setLoading(true);
        setError(null);

        try {
            const token = localStorage.getItem('access_token');
            const response = await axios.post(
                "http://127.0.0.1:8000/generate-mql",
                { 
                    prompt: request, 
                    org_name: orgName 
                },
                {
                    headers: {
                        'Authorization': `Bearer ${token}`,
                        'Content-Type': 'application/json'
                    }
                }
            );

            if (response.data.result) {
                setResult(response.data.result);
            } else {
                setError('No results found');
            }
        } catch (err) {
            setError(err.response?.data?.detail || 'Error processing your request');
        } finally {
            setLoading(false);
        }
    };
    console.log("AIController rendered");
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