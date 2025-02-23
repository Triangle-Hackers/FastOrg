import React from 'react';
import '../styles/AIRequest.css';
import Navbar from '../components/Navbar';

const AIRequest = ({ request, setRequest, handleAIRequest, result, error, loading }) => {
    return (
        <div className="ai-container">
            
            {/* Navbar */}
            <Navbar />

            {/* AI Request Panel */}
            <div className="ai-panel">
                <div className="responses">
                    {result && (
                        <div className="result">
                            <h3>Response:</h3>
                            <pre>{JSON.stringify(result, null, 2)}</pre>
                        </div>
                    )}
                </div>
                <div className="chat-box">
                    <form onSubmit={(e) => {
                        e.preventDefault();
                        handleAIRequest();
                    }}>
                        <textarea 
                            value={request} 
                            onChange={(e) => setRequest(e.target.value)} 
                            placeholder="Enter your request..." 
                            rows={4} 
                            style={{ width: '100%' }} 
                        />
                        <button type="submit" disabled={loading}>
                            {loading ? 'Processing...' : 'Submit'}
                        </button>
                    </form>
                    {error && <div className="error">{error}</div>}
                </div>
            </div>
        </div>
    );
};

export default AIRequest;