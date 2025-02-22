import React, { useEffect, useState } from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import Home from './views/Home';
import AIRequest from './views/AIRequest';
import LandingPage from './views/LandingPage';
import NotFound from './views/NotFound';

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
        <Route path="/" element={isSessionValid ? <Home /> : <LandingPage />} />
        <Route path="/home" element={isSessionValid ? <Home /> : <LandingPage />} />
        <Route path="/ai-request" element={isSessionValid ? <AIRequest /> : <LandingPage />} />
        <Route path="*" element={<NotFound />} />
      </Routes>
    </BrowserRouter>
  );
};

export default App;