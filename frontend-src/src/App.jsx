import React, { useEffect, useState } from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { setCompletedSetup } from './components/global_setup_state';
import fetchWithConfig from './utils/fetchUtils';
import LandingPage from './views/LandingPage';
import NotFound from './views/NotFound';
import AIController from './controllers/AIControl';
import HomeController from './controllers/HomeControl';
import SettingsController from './controllers/SettingsControl';
import FirstTimeSetupController from './controllers/FirstTimeSetupControl';
import JoinOrgController from './controllers/JoinOrgController';
import { getCompletedSetup } from './components/global_setup_state';

const App = () => {
  const [isSessionValid, setIsSessionValid] = useState(false);
  const [isChecking, setIsChecking] = useState(true);

  const handleAuthSuccess = async () => {
    try {
      const response = await fetchWithConfig('/');
      const data = await response.json();

      if (data.access_token) {
        localStorage.setItem("access_token", data.access_token);
      }
    } catch (error) {
      console.error('Auth success handling failed:', error);
    }
  };

  useEffect(() => {
    const checkSession = async () => {
      try {
        const response = await fetchWithConfig('/verify-session');
        
        if (response.ok) {
          setIsSessionValid(true);
          handleAuthSuccess();
          
          // Check user metadata for completed setup
          const profileRes = await fetchWithConfig('/fetch-full-profile');
          if (profileRes.ok) {
            const profile = await profileRes.json();
            const hasOrgName = profile.user.user_metadata?.org_name;
            setCompletedSetup(!!hasOrgName); // Convert to boolean
          }
        } else {
          setIsSessionValid(false);
          setCompletedSetup(false);
        }
      } catch (error) {
        console.error('Session check failed:', error);
        setIsSessionValid(false);
        setCompletedSetup(false);
      } finally {
        setIsChecking(false);
      }
    };

    checkSession();
  }, []);

  if (isChecking) {
    return <div>Loading...</div>;
  }

  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={isSessionValid ? <Navigate to="/home" replace /> : <LandingPage />} />
        <Route path="/home" element={isSessionValid ? (getCompletedSetup ? <HomeController /> : <FirstTimeSetupController /> ): <LandingPage />} />
        <Route path="/ai-request" element={isSessionValid ? <AIController /> : <LandingPage />} />
        <Route path="/settings" element={isSessionValid ? <SettingsController /> : <LandingPage />} />
        <Route path="/setup" element={isSessionValid ? <FirstTimeSetupController /> : <LandingPage />} />
        <Route path="/join-org" element={<JoinOrgController />} />
        <Route path="*" element={<NotFound />} />
      </Routes>
    </BrowserRouter>
  );
};

export default App;
