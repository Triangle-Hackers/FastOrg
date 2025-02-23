import React, { useState, useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import SetupWizard from '../views/FirstTimeSetup';
import { getCompletedSetup, setCompletedSetup } from '../components/global_setup_state';

const FirstTimeSetupController = () => {
  const [loading, setLoading] = useState(true);
  const [isNewUser, setIsNewUser] = useState(false);
  const [error, setError] = useState(null);
  const navigate = useNavigate();

  useEffect(() => {
    if (!getCompletedSetup()) {
      checkIfNewUser();
    }
  });

  const checkIfNewUser = async () => {
    setLoading(true);
    try {
      // Verify session
      const sessionRes = await fetch('http://localhost:8000/verify-session', {
        credentials: 'include',
      });
      if (!sessionRes.ok) {
        throw new Error('Not authenticated');
      }

      // Fetch full user profile
      const profileRes = await fetch('http://localhost:8000/fetch-full-profile', {
        credentials: 'include',
      });
      if (!profileRes.ok) {
        throw new Error('Failed to fetch full profile');
      }

      const fullProfile = await profileRes.json();
      const completed = fullProfile.user.user_metadata?.completed_setup;

      console.log(fullProfile);
      // If user has completed setup, redirect to home
      if (completed) {
        setCompletedSetup(true);
        console.log(getCompletedSetup());
        navigate('/home');
      } else {
        setCompletedSetup(false);
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