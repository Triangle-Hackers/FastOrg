
import React, { useEffect, useState } from 'react';
import PropTypes from 'prop-types';
import { useNavigate } from 'react-router-dom';
import '../styles/Home.css';
import Navbar from '../components/Navbar';
import { getCompletedSetup } from '../components/global_setup_state';

const Home = ({ 
    userData, 
    loading, 
    error,
    roster,
    setRoster,
    infoMessage,
    setInfoMessage,
    handleViewRoster 
}) => {
    const navigate = useNavigate();

    useEffect(() => {
        if (!getCompletedSetup()) {
            navigate('/setup');
        }
    }, []);

    const [mode] = useState(() => {
            return localStorage.getItem('mode') || 'light';
        });

    const [isEditMode, setIsEditMode] = useState(false);
    const [editedRoster, setEditedRoster] = useState(roster);

    if (loading) return <div>Loading...</div>;
    if (error) return <div>Error: {error}</div>;

    const handleEditToggle = () => {
        setIsEditMode((prev) => !prev);
    };

    const handleRemoveEntry = (index) => {
        const newRoster = editedRoster.filter((_, i) => i !== index);
        setEditedRoster(newRoster);
    };

    const handleChangeValue = (index, field, value) => {
        const updatedRoster = [...editedRoster];
        updatedRoster[index][field] = value;
        setEditedRoster(updatedRoster);
    };

    const handleSaveChanges = () => {
        setRoster(editedRoster);
        setIsEditMode(false);
        setInfoMessage('Roster updated successfully');
    };


    return (
        <div className={`home-container ${mode}`}>
            <Navbar />

            <div className="main-content-wrapper">
                <div className="operations-info-container">
                    <section className="operations-section">

                        <h2>Roster View</h2>
                        <div className="buttons">
                            <button onClick={handleViewRoster}>View Full Roster</button>

                        </div>
                    </section>
                    <section className="info-section">
                        <h2>Information</h2>
                        {isEditMode ? (
                            <div>
                                <ul>
                                    {editedRoster.map((member, index) => (
                                        <li key={index}>
                                            <input
                                                type="text"
                                                value={member.name}
                                                onChange={(e) =>
                                                    handleChangeValue(index, 'name', e.target.value)
                                                }
                                            />
                                            <input
                                                type="text"
                                                value={member.role}
                                                onChange={(e) =>
                                                    handleChangeValue(index, 'role', e.target.value)
                                                }
                                            />
                                            <button onClick={() => handleRemoveEntry(index)}>
                                                Remove
                                            </button>
                                        </li>
                                    ))}
                                </ul>
                                <button onClick={handleSaveChanges}>Save Changes</button>
                            </div>

                        ) : (
                            <div>
                                {roster && roster.length > 0 ? (
                                    <ul>
                                        {roster.map((member, index) => (
                                            <li key={index}>
                                                {member.name} - {member.role}
                                            </li>
                                        ))}
                                    </ul>
                                ) : (
                                    <p>{infoMessage}</p>
                                )}
                                <button onClick={handleEditToggle}>Edit</button>
                            </div>
                        )}
                    </section>

                    <div className="buttons">
                    </div>
                </div>
            </div>
        </div>
    );
};

Home.propTypes = {
    userData: PropTypes.object,
    loading: PropTypes.bool.isRequired,
    error: PropTypes.string,
    roster: PropTypes.array.isRequired,
    setRoster: PropTypes.func.isRequired,
    infoMessage: PropTypes.string.isRequired,
    setInfoMessage: PropTypes.func.isRequired,
    handleViewRoster: PropTypes.func.isRequired,
};

export default Home;