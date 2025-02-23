import React from 'react';
import { NavLink } from 'react-router-dom';
import '../styles/Navbar.css';

const Navbar = () => (
    <nav className="navbar">
        <ul className="navbar-container">
            <li className="navbar-item">
                <NavLink to="/home" end className="navbar-item" activeClassName="active">
                    Dashboard
                </NavLink>
            </li>
            <li>
                <NavLink to="/ai-request" end className="navbar-item" activeClassName="active">
                    DeepConsole
                </NavLink>
            </li>
            <li className="navbar-item">
                <NavLink to="/settings" end className="navbar-item" activeClassName="active">
                    Settings
                </NavLink>
            </li>
        </ul>
    </nav>
);

export default Navbar;
