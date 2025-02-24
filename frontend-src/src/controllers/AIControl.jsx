import React, { useState, useEffect } from 'react';
import AIRequest from '../views/AIRequest';
import fetchWithConfig from '../utils/fetchUtils';
import api from '../models/apiService';

const AIController = () => {
    /* Set states for api ai input vars */
    const [request, setRequest] = useState('');
    const [result, setResult] = useState(null);
    const [error, setError] = useState(null);
    const [loading, setLoading] = useState(false);
    const [orgName, setOrgName] = useState(null);

    useEffect(() => {
        fetchOrgName();
    }, []);

    const fetchOrgName = async () => {
        try {
            const profileRes = await fetchWithConfig('/fetch-full-profile');
            if (!profileRes.ok) {
                throw new Error('Failed to fetch full profile');
            }
    
            const fullProfile = await profileRes.json();
            const org_name = fullProfile.user.user_metadata.org_name;
            setOrgName(org_name);
        } catch (err) {
            console.error('Error fetching organization name:', err);
            setError('Error fetching organization details');
        }
    };

    const handleAIRequest = async () => {
        if (!request.trim()) return;
        if (!orgName) {
            setError("Please join an organization first");
            return;
        }

        setLoading(true);
        setError(null);
        try {
            const response = await api.post('/generate-mql', { 
                prompt: request, 
                org_name: orgName 
            });
            
            console.log(response);

            if (response.data) {
                setResult(response.data);
            } else {
                setError('No results found');
            }
        } catch (err) {
            console.log(err);
            setError('Failed to process AI request');
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