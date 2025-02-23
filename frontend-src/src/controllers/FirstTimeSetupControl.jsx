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
      
      console.log('Session response:', sessionRes.status);
      
      if (!sessionRes.ok) {
        const errorData = await sessionRes.json();
        console.error('Session verification failed:', errorData);
        throw new Error(`Not authenticated: ${errorData.detail || 'Unknown error'}`);
      }

      // Fetch full user profile
      const profileRes = await fetch('http://localhost:8000/fetch-full-profile', {
        credentials: 'include',
      });
      
      console.log('Profile response:', profileRes.status);
      
      if (!profileRes.ok) {
        const errorData = await profileRes.json();
        console.error('Profile fetch failed:', errorData);
        throw new Error(`Failed to fetch full profile: ${errorData.detail || 'Unknown error'}`);
      }

      const fullProfile = await profileRes.json();
      console.log('Full profile:', fullProfile);
      
      const completed = fullProfile.user.user_metadata?.completed_setup;

      setCompletedSetup(true);
      // If user has completed setup, redirect to home
      if (completed) {
        setCompletedSetup(true);
        console.log('Setup completed, redirecting to home');
        navigate('/home');
      } else {
        setCompletedSetup(false);
        setIsNewUser(true);
        console.log('New user, showing setup wizard');
      }
    } catch (err) {
      console.error('Detailed error:', err);
      setError(`Failed to check new user status: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  const handleFinishSetup = async (setupData) => {
    try {
      console.log('Setup data received:', setupData); // Log incoming data
      
      // First verify the user is authenticated
      const sessionRes = await fetch('http://localhost:8000/verify-session', {
        credentials: 'include',
      });
      
      if (!sessionRes.ok) {
        throw new Error('Not authenticated');
      }

      // Get the user profile
      const userResponse = await fetch('http://localhost:8000/fetch-full-profile', {
        credentials: 'include',
      });
      
      if (!userResponse.ok) {
        throw new Error('Failed to fetch user profile');
      }

      const userData = await userResponse.json();
      
      // Create the organization with the required data
      const enrichedSetupData = {
        org_name: setupData.org_name, // Changed from orgName to org_name to match form field name
        user_data: userData.user
      };

      console.log('Sending setup data:', enrichedSetupData); // Log final data being sent

      const res = await fetch('http://localhost:8000/protected/create-org', {
        method: 'POST',
        credentials: 'include',
        headers: { 
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(enrichedSetupData)
      });

      if (!res.ok) {
        const errorData = await res.json();
        console.error('Error response:', errorData); // Log error response
        throw new Error(errorData.detail || 'Failed to create organization');
      }

      const data = await res.json();
      setInviteCode(data.invite_code);
      setShowInvitePopup(true);
      navigate('/home');
    } catch (err) {
      console.error('Setup error:', err);
      setError(err.message || 'Error completing setup');
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