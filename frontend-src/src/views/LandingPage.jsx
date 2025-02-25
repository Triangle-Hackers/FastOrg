import React, { useEffect } from 'react';
import { useAuth0 } from '@auth0/auth0-react';
import '../styles/LandingPage.css';
import { setCompletedSetup } from '../components/global_setup_state';
import config from '../config/env';

const LandingPage = () => {

    useEffect(() => {
        setCompletedSetup(false);
    }, []);

    const handleGetStarted = async () => {
        try {
            // Redirect to backend login endpoint
            console.log('Redirecting to:', `${config.externalUrl}/login`);
            window.location.href = `${config.externalUrl}/login`;
        } catch (error) {
            console.error('Login error:', error);
        }
    };

    return (
        <div className="landing-container">
            <h1>Welcome to FastOrg!</h1>
            <p>Streamline your organization management</p>
            <div className="buttons">
                <button onClick={handleGetStarted}>Get Started</button>
            </div>
        </div>
    );
};

export default LandingPage;