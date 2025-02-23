import React, { useState, useEffect } from 'react';
import Home from '../views/Home';

const HomeController = () => {
    // States for home page data
    const [userData, setUserData] = useState(null);
    const [organizations, setOrganizations] = useState([]);
    const [roster, setRoster] = useState([]);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);
    const [infoMessage, setInfoMessage] = useState("Requested information will appear here...");

    // Fetch user data and organizations on component mount
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

    const handleViewRoster = async () => {
        try {
            const response = await fetch("http://localhost:8000/protected/get-roster", {
                credentials: "include",
            });
            const data = await response.json();

            if (data.detail) {
                setInfoMessage(`Error: ${data.detail}`);
                setRoster([]);
            } else {
                setRoster(data.roster);
                setInfoMessage("");
            }
        } catch (error) {
            setInfoMessage("Failed to fetch roster.");
            setRoster([]);
        } finally {
            setLoading(false);
        }
    };


    console.log("HomeController rendered");
    return (
        <Home
            userData={userData}
            loading={loading}
            error={error}
            roster={roster}
            setRoster={setRoster}
            infoMessage={infoMessage}
            setInfoMessage={setInfoMessage}
            handleViewRoster={handleViewRoster}
        />
    );
};

export default HomeController;
