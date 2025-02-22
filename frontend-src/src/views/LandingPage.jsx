import React from 'react';
import { useAuth0 } from '@auth0/auth0-react';
import './LandingPage.css';

const LandingPage = () => {
    const { loginWithRedirect } = useAuth0();

    const handleGetStarted = async () => {
        try {
            // Redirect to backend login endpoint
            window.location.href = 'http://localhost:8000/login';
        } catch (error) {
            console.error('Login error:', error);
        }
    };

    return (
        <div className="landing-container">
            <h1>Welcome to OrgCRM</h1>
            <p>Streamline your organization management</p>
            <div className="buttons">
                <button onClick={handleGetStarted}>Get Started</button>
            </div>
        </div>
    );
};

export default LandingPage;