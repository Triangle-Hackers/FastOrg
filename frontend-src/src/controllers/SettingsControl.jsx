import React, { useState, useEffect } from 'react';
import { useAuth0 } from '@auth0/auth0-react';
import Settings from '../views/Settings';
import fetchWithConfig from '../utils/fetchUtils';

const SettingsController = () => {
    const { user } = useAuth0();
    const [userData, setUserData] = useState(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);

    useEffect(() => {
        fetchUserData();
    }, []);

    const fetchUserData = async () => {
        setLoading(true);
        try {
            const response = await fetchWithConfig('/verify-session');
            if (response.ok) {
                const data = await response.json();
                setUserData(data.user);
            } else {
                throw new Error('Failed to fetch user data');
            }
        } catch (err) {
            setError('Error loading user data');
            console.error('Error:', err);
        } finally {
            setLoading(false);
        }
    };

    const handleUpdateNickname = async (newNickname) => {
        setLoading(true);
        try {
            const response = await fetchWithConfig('/update-nickname', {
                method: 'PUT',
                body: JSON.stringify({ nickname: newNickname })
            });

            if (!response.ok) {
                throw new Error('Failed to update nickname');
            }

            await fetchUserData();
        } catch (err) {
            setError('Error updating nickname');
            console.error('Error:', err);
        } finally {
            setLoading(false);
        }
    };

    const handleUpdateSettings = async (settingsData) => {
        setLoading(true);
        try {
            const response = await fetchWithConfig('/settings', {
                method: 'PUT',
                body: JSON.stringify(settingsData)
            });
            
            if (!response.ok) {
                throw new Error('Failed to update settings');
            }
            
            await fetchUserData();
        } catch (err) {
            setError('Error updating settings');
            console.error('Error:', err);
        } finally {
            setLoading(false);
        }
    };

    return (
        <Settings
            userData={userData}
            user={user}
            loading={loading}
            error={error}
            handleUpdateNickname={handleUpdateNickname}
            handleUpdateSettings={handleUpdateSettings}
        />
    );
};

export default SettingsController; 