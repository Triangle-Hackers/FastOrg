import React, { useState, useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import SetupWizard from '../views/FirstTimeSetup';
import { getCompletedSetup, setCompletedSetup } from '../components/global_setup_state';
import InviteCodePopup from '../components/InviteCodePopup';
import FirstTimeSetup from '../views/FirstTimeSetup';

const FirstTimeSetupController = () => {
  const [loading, setLoading] = useState(true);
  const [isNewUser, setIsNewUser] = useState(false);
  const [error, setError] = useState(null);
  const [showInvitePopup, setShowInvitePopup] = useState(false);
  const [inviteCode, setInviteCode] = useState('');
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
      setCompletedSetup(true);
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
      const userResponse = await fetch('http://localhost:8000/fetch-full-profile', {
        credentials: 'include',
      });
      
      if (!userResponse.ok) {
        throw new Error('Failed to fetch user profile');
      }

      const userData = await userResponse.json();
      console.log("User data fetched:", userData);

      
      const enrichedSetupData = {
        ...setupData,
        'session': { 'user': userData }
      };

      let res = await fetch('http://localhost:8000/protected/create-org', {
        method: 'POST',
        credentials: 'include',
        headers: { 
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(enrichedSetupData)
      });

      if (!res.ok) {
        throw new Error('Failed to create organization');
      }

      const data = await res.json();
      const newInviteCode = data.invite_code;
      setInviteCode(newInviteCode);  // Store invite code in state

      // Show the popup with the invite code
      setShowInvitePopup(true);
      console.log('success???');
      navigate('/home');
    } catch (err) {
      setError('Error completing setup');
      console.error(err);
    }
  };


  // Function to close popup
  const closeInvitePopup = () => {
    setShowInvitePopup(false);
  };

  return (
    <div>
      {error && <p style={{ color: 'red' }}>{error}</p>}
      {
        showInvitePopup && (
          <InviteCodePopup
            inviteCode={inviteCode}
            onClose={closeInvitePopup}
          />
        )
      }
    <SetupWizard
    loading={loading}
    isNewUser={isNewUser}
    error={error}
    onFinishSetup={handleFinishSetup} />
      
    </div>
  );
};

export default FirstTimeSetupController; 