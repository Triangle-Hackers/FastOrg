import React, { useState, useEffect } from 'react';
import { useAuth0 } from '@auth0/auth0-react';
import Settings from '../views/Settings';

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
            const response = await fetch('http://localhost:8000/verify-session', {
                credentials: 'include'
            });
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
            const response = await fetch('http://localhost:8000/update-nickname', {
                method: 'PUT',
                credentials: 'include',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ nickname: newNickname })
            });

            if (!response.ok) {
                throw new Error('Failed to update nickname');
            }

            // Refresh user data after update
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
            const response = await fetch('http://localhost:8000/settings', {
                method: 'PUT',
                credentials: 'include',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(settingsData)
            });
            
            if (!response.ok) {
                throw new Error('Failed to update settings');
            }
            
            // Refresh user data after update
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