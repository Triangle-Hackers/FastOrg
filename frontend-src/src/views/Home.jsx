import React, { useEffect } from 'react';
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
        handleViewRoster();
    }, []);

    if (loading) return <div>Loading...</div>;
    if (error) return <div>Error: {error}</div>;

    return (
        <div className="home-container">
            <Navbar />

            <div className="main-content-wrapper">
                <div className="operations-info-container">
                    <section className="operations-section">
                        <h2>Roster View</h2>
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