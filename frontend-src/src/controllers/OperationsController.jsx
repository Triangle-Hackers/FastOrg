import React, { useState } from 'react';
import DashboardView from '../views/Home';
import { performOperation } from '../models/operationsService';

const OperationsController = () => {
    const [result, setResult] = useState(null);
    const [error, setError] = useState(null);

    const handleOperation = async (operationName) => {
        try {
            setError(null);
            const data = await performOperation(operationName);
            setResult(data);
        } catch (err) {
            setError(err.response?.data?.message || 'An error occurred');
        }
    };

    return (
        <DashboardView 
            handleOperation={handleOperation}
            result={result}
            error={error}
        />
    );
};

export default OperationsController;