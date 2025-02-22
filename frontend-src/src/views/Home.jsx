import React from 'react';
import { NavLink } from 'react-router-dom';
import '../styles/Home.css';
import Navbar from '../components/Navbar';

const Home = ({ 
    userData, 
    loading, 
    error, 
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
                            <button>Operation 1</button>
                            <button>Operation 2</button>
                            <button>Operation 3</button>
                        </div>
                    </section>
                    <section className="info-section">
                        <h2>Information</h2>
                        <p>Requested information will appear here...</p>
                    </section>
                </main>
            </div>
        </div>
    );
};

export default Home;