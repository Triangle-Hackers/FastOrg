import React from 'react';
import PropTypes from 'prop-types';
import { NavLink } from 'react-router-dom';
import '../styles/Home.css';
import Navbar from '../components/Navbar';

const Home = ({ 
    userData, 
    loading, 
    error,
    roster,
    setRoster,
    infoMessage,
    setInfoMessage,
    handleViewRoster, 
}) => {
    if (loading) return <div>Loading...</div>;
    if (error) return <div>Error: {error}</div>;
    return (
        <div className="home-container">
            {/* Navbar */}
            <Navbar />

            {/* Main Content */}
            <div className="main-content-wrapper">
                <main className="content">
                    <section className="operations-section">
                        <h2>Operations</h2>
                        <div className="buttons">
                            <button onClick={handleViewRoster}>View Full Roster</button>
                            <button>Operation 2</button>
                            <button>Operation 3</button>
                        </div>
                    </section>
                    <section className="info-section">
                        <h2>Information</h2>
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
                </main>
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
}

export default Home;