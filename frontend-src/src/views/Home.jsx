import React from 'react';
import { NavLink } from 'react-router-dom';
import './Home.css';

const Home = () => {
    return (
        <div className="home-container">
            {/* Header */}
            <header className="header">
                <div className="org-name">User org</div>
                <div className="software-name">Software name</div>
            </header>

            {/* Navbar */}
            <nav className="navbar">
                <ul>
                    <li>
                        <NavLink to="/" end activeClassName="active">
                            Dashboard
                        </NavLink>
                    </li>
                    <li><NavLink to="/AIRequest" end activeClassName="active">
                            AIRequest
                        </NavLink>
                    </li>
                </ul>
            </nav>

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