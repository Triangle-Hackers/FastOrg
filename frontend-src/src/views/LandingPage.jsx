import React from 'react';
import { useAuth0 } from '@auth0/auth0-react';

const LandingPage = () => {
    const handleLogin = () => {
        window.location.href = 'http://localhost:8000/login';
    };

    return (
        <div className="landing-container">
            <h1>Welcome to our CRM!</h1>
            <p>You should use this software trust</p>
            <button onClick={handleLogin}>Log In</button>
        </div>
    );
};

export default LandingPage;