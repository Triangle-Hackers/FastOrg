import React from 'react';
import '../styles/InviteCodePopup.css';

/**
 * A simple modal component that displays the invite code and 
 * has an OK button to close the modal.
 *
 * Props:
 *  - inviteCode (string): The invite code to display.
 *  - onClose (function): A callback function to close the modal.
 */
function InviteCodePopup({ inviteCode, onClose }) {
  return (
    <div className="invite-code-modal-overlay">
      <div className="invite-code-modal-content">
        <h2>Organization Invite Code</h2>
        <p>{inviteCode}</p>
        <button onClick={onClose}>OK</button>
      </div>
    </div>
  );
}

export default InviteCodePopup; 