import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import SetupWizard from '../views/FirstTimeSetup';

const FirstTimeSetupController = () => {
  const [loading, setLoading] = useState(true);
  const [isNewUser, setIsNewUser] = useState(false);
  const [error, setError] = useState(null);
  const navigate = useNavigate();

  useEffect(() => {
    checkIfNewUser();
  }, []);

  const checkIfNewUser = async () => {
    setLoading(true);
    try {
      const res = await fetch('http://localhost:8000/verify-session', {
        credentials: 'include',
      });
      if (!res.ok) {
        throw new Error('Not authenticated');
      }
      const data = await res.json();
      const completed = data.user?.app_metadata?.completed_setup;
      // If user has completed setup, redirect to home
      if (completed) {
        navigate('/home');
      } else {
        setIsNewUser(true);
      }
    } catch (err) {
      setError('Failed to check new user status.');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleFinishSetup = async (setupData) => {
    // We assume we have an endpoint that marks the user's completed_setup as true
    try {
      const res = await fetch('http://localhost:8000/complete-setup', {
        method: 'PUT',
        credentials: 'include',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(setupData),
      });

      if (!res.ok) {
        throw new Error('Failed to complete setup');
      }

      // If we succeed, go to home
      navigate('/home');
    } catch (err) {
      setError('Error completing setup');
      console.error(err);
    }
  };

  return (
    <SetupWizard
      loading={loading}
      isNewUser={isNewUser}
      error={error}
      onFinishSetup={handleFinishSetup}
    />
  );
};

export default FirstTimeSetupController; 