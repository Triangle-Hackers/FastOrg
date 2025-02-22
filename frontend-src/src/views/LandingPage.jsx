import React from 'react';
import './LandingPage.css';

const LandingPage = () => {
    const handleLogin = () => {
        window.location.href = 'http://localhost:8000/login';
    };

    return (
        <div className="landing-container">
            <h1>Welcome to our CRM</h1>
            <p>You should use this software trust</p>
            <div className="buttons">
                <button onClick={handleLogin}>Log In</button>
                <button onClick={handleLogin}>Sign Up</button>
            </div>
        </div>
    );
};

export default LandingPage;