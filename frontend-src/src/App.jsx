import React, { useEffect, useState } from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import Home from './views/Home';
import AIRequest from './views/AIRequest';
import LandingPage from './views/LandingPage';
import NotFound from './views/NotFound';
import AIController from './controllers/AIControl';
import HomeController from './controllers/HomeControl';
import SettingsController from './controllers/SettingsControl';
import FirstTimeSetupController from './controllers/FirstTimeSetupControl';

const App = () => {
  const [isSessionValid, setIsSessionValid] = useState(false);
  const [isChecking, setIsChecking] = useState(true);

  useEffect(() => {
    const checkSession = async () => {
      try {
        const response = await fetch('http://localhost:8000/verify-session', {
          credentials: 'include'
        });
        
        if (response.ok) {
          setIsSessionValid(true);
        } else {
          setIsSessionValid(false);
        }
      } catch (error) {
        console.error('Session check failed:', error);
        setIsSessionValid(false);
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
        <Route path="/home" element={isSessionValid ? <HomeController /> : <LandingPage />} />
        <Route path="/ai-request" element={isSessionValid ? <AIController /> : <LandingPage />} />
        <Route path="/settings" element={isSessionValid ? <SettingsController /> : <LandingPage />} />
        <Route path="/setup" element={isSessionValid ? <FirstTimeSetupController /> : <LandingPage />} />
        <Route path="*" element={<NotFound />} />
      </Routes>
    </BrowserRouter>
  );
};

export default App;