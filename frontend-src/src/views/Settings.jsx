import React, { useState } from 'react';
import '../styles/Settings.css';
import Navbar from '../components/Navbar';

const Settings = ({ 
    user, 
    loading, 
    error, 
    handleUpdateNickname 
}) => {
    const [activeTab, setActiveTab] = useState('account');
    const [nickname, setNickname] = useState(user?.nickname || '');

    const handleSubmit = (e) => {
        e.preventDefault();
        handleUpdateNickname(nickname);
    };

    if (loading) return <div>Loading...</div>;
    if (error) return <div>Error: {error}</div>;

    return (
        <div className="settings-container">
            <Navbar />
            <div className="toolbar">
                <div className="user-info">
                    <span>{user?.nickname || user?.name}</span>
                    <span>{user?.email}</span>
                </div>
                <div className="actions">
                    <button>Home</button>
                    <button>Logout</button>
                </div>
            </div>

            <div className="settings-content">
                <h1>Settings</h1>
                
                <div className="settings-tabs">
                    <button 
                        className={`tab-button ${activeTab === 'account' ? 'active' : ''}`}
                        onClick={() => setActiveTab('account')}
                    >
                        Account Settings
                    </button>
                    <button 
                        className={`tab-button ${activeTab === 'app' ? 'active' : ''}`}
                        onClick={() => setActiveTab('app')}
                    >
                        App Settings
                    </button>
                </div>

                {activeTab === 'account' ? (
                    <div className="settings-section">
                        <h2>Account Settings</h2>
                        <div className="settings-form">
                            <div className="form-group">
                                <label>Nickname</label>
                                <input 
                                    type="text" 
                                    value={nickname}
                                    onChange={(e) => setNickname(e.target.value)}
                                    placeholder="Enter your nickname"
                                />
                            </div>
                            <div className="form-group">
                                <label>Email</label>
                                <input type="email" value={user?.email} readOnly />
                            </div>
                            <button 
                                className="save-button" 
                                onClick={handleSubmit}
                                disabled={loading}
                            >
                                {loading ? 'Saving...' : 'Save Account Settings'}
                            </button>
                        </div>
                    </div>
                ) : (
                    <div className="settings-section">
                        <h2>App Settings</h2>
                        <div className="settings-form">
                            <div className="form-group">
                                <label>Notification Preferences</label>
                                <select defaultValue="all">
                                    <option value="all">All Notifications</option>
                                    <option value="important">Important Only</option>
                                    <option value="none">None</option>
                                </select>
                            </div>
                            <div className="form-group">
                                <label>Theme</label>
                                <select defaultValue="light">
                                    <option value="light">Light</option>
                                    <option value="dark">Dark</option>
                                    <option value="system">System Default</option>
                                </select>
                            </div>
                            <div className="form-group">
                                <label>Language</label>
                                <select defaultValue="en">
                                    <option value="en">English</option>
                                    <option value="es">Spanish</option>
                                    <option value="fr">French</option>
                                </select>
                            </div>
                            <div className="form-group">
                                <label>Email Digest</label>
                                <select defaultValue="daily">
                                    <option value="daily">Daily</option>
                                    <option value="weekly">Weekly</option>
                                    <option value="never">Never</option>
                                </select>
                            </div>
                            <button className="save-button">Save App Settings</button>
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
};

export default Settings;