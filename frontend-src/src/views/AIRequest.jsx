import React, { useState } from 'react';
import '../styles/AIRequest.css';
import Navbar from '../components/Navbar';

const AIRequest = ({ request, setRequest, handleAIRequest, result, error, loading }) => {
    const [nValue, setNValue] = useState(1);
    const [mValue, setMValue] = useState(1);
    const [tableHTML, setTableHTML] = useState('');
    // const [request, setRequest] = useState('');
    // const [loading, setLoading] = useState(false);
    
    const [mode] = useState(() => {
                return localStorage.getItem('mode') || 'light';
            });

    const handleTableGeneration = (e) => {
        e.preventDefault();

        // Convert nValue/mValue to integers (they come in as strings from inputs)
        const N = parseInt(nValue, 10) || 0;
        const M = parseInt(mValue, 10) || 0;

        // Generate table HTML
        let html = '<table class="generated-table" border="1" style="border-collapse: collapse;">';
        
        // First row: number_1, number_2, ..., number_M
        html += '<tr>';
        for (let i = 1; i <= M; i++) {
            html += `<th>number_${i}</th>`;
        }
        html += '</tr>';

        // Next N rows: random numbers in each cell
        for (let row = 1; row <= N; row++) {
            html += '<tr>';
            for (let col = 1; col <= M; col++) {
                const randomNumber = Math.floor(Math.random() * 100); // random between 0 and 99
                html += `<td style="text-align:center;">${randomNumber}</td>`;
            }
            html += '</tr>';
        }

        html += '</table>';

        setTableHTML(html);
    };

    const renderResults = () => {
        if (!result) return null;
        
        return (
            <div className="query-results">
                <h3>Query Results:</h3>
                <table className="results-table">
                    <thead>
                        <tr>
                            {result[0] && Object.keys(result[0]).map(key => (
                                <th key={key}>{key}</th>
                            ))}
                        </tr>
                    </thead>
                    <tbody>
                      
                    </tbody>
                </table>
            </div>
        );
    };

    return (
        <div className={`ai-container ${mode}`}>
            
            {/* Navbar */}
            <Navbar />

            {/* AI Request Panel */}
            <div className="ai-panel">
                <div className="responses">
                    {error && <div className="error-message">{error}</div>}
                    {renderResults()}
                    {tableHTML && (
                        <div className="result">
                            <h3>Generated Table:</h3>
                            <div
                                className="table-result"
                                dangerouslySetInnerHTML={{ __html: tableHTML }}
                            />
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
                            placeholder="Enter your query (e.g., 'Show members with GPA below 2.0')" 
                            rows={4} 
                            style={{ width: '100%' }} 
                        />
                        <button type="submit" disabled={loading}>
                            {loading ? 'Processing...' : 'Submit Query'}
                        </button>
                    </form>
                </div>
            </div>
        </div>
    );
};

export default AIRequest;
