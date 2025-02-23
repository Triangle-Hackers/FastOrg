import React, { useState, useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import SetupWizard from '../views/FirstTimeSetup';
import { getCompletedSetup, setCompletedSetup } from '../components/global_setup_state';
import InviteCodePopup from '../components/InviteCodePopup';

const FirstTimeSetupController = () => {
  const [loading, setLoading] = useState(true);
  const [isNewUser, setIsNewUser] = useState(false);
  const [error, setError] = useState(null);
  const [done, setDone] = useState(false);
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
      let res = await fetch(`http://localhost:8000/create-org/${setupData.org_name}`, {
        method: 'GET',
        credentials: 'include',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(setupData),
      });

      if (!res.ok) {
        throw new Error('Failed to create organization');
      }

      const data = await res.json();
      const newInviteCode = data.invite_code;
      setInviteCode(newInviteCode);  // Store invite code in state

      // Show the popup with the invite code
      setShowInvitePopup(true);

      // After the user sees the invite code (inside the popup), 
      // we might still proceed with the 'complete-setup' call
      // For demonstration, we're keeping it right here:
      res = await fetch('http://localhost:8000/complete-setup', {
        method: 'PUT',
        credentials: 'include',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(setupData),
      });

      if (!res.ok) {
        throw new Error('Failed to complete setup');
      }

      // In a real-world flow, you might:
      // 1. Wait until the user clicks OK on the popup.
      // 2. Then navigate('/home').
      // For brevity, we do it immediately after the fetch call succeeds.
      // So the user sees the popup (over the new page) or you can reorder as needed.

      navigate('/home');
    } catch (err) {
      setError('Error completing setup');
      console.error(err);
    }
  };

  // Example form or button to trigger handleFinishSetup
  // The "setupData" object would come from user input
  const onSetupSubmit = () => {
    const exampleSetupData = { org_name: 'ExampleOrg' };
    handleFinishSetup(exampleSetupData);
  };

  // Function to close popup
  const closeInvitePopup = () => {
    setShowInvitePopup(false);
  };

  return (
    <div>
      {error && <p style={{ color: 'red' }}>{error}</p>}
      
      <button onClick={onSetupSubmit}>Finish Setup</button>

      {
        showInvitePopup && (
          <InviteCodePopup
            inviteCode={inviteCode}
            onClose={closeInvitePopup}
          />
        )
      }
    </div>
  );
};

export default FirstTimeSetupController; 