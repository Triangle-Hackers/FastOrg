import React, { useState } from 'react';
import '../styles/AIRequest.css';
import Navbar from '../components/Navbar';

const AIRequest = () => {
    const [nValue, setNValue] = useState(1);
    const [mValue, setMValue] = useState(1);
    const [tableHTML, setTableHTML] = useState('');

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

    return (
        <div className={`ai-container ${mode}`}>
            
            {/* Navbar */}
            <Navbar />

            {/* AI Request Panel */}
            <div className="ai-panel">
                <div className="responses">
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
                    <form onSubmit={handleTableGeneration} style={{ marginBottom: '1rem' }}>
                        <label style={{ marginRight: '8px' }}>
                            N:
                            <input
                                type="number"
                                value={nValue}
                                onChange={(e) => setNValue(e.target.value)}
                                min="1"
                                style={{ marginLeft: '4px', marginRight: '12px' }}
                            />
                        </label>

                        <label style={{ marginRight: '8px' }}>
                            M:
                            <input
                                type="number"
                                value={mValue}
                                onChange={(e) => setMValue(e.target.value)}
                                min="1"
                                style={{ marginLeft: '4px', marginRight: '12px' }}
                            />
                        </label>

                        <button type="submit">Generate Table</button>
                    </form>
                </div>
            </div>
        </div>
    );
};

export default AIRequest;