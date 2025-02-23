import React, { useState } from 'react';
import "../styles/JoinOrg.css";

const JoinOrg = ({schema, error, successMessage, fetchSchema, submitMemberData, inviteCode, setInviteCode, showInvite}) => {
    const [formData, setFormData] = useState({});
    const [joined, setJoined] = useState(false);


    // const handleFetchSchema = async () => {
    //     if (!inviteCode.trim()) {
    //         alert("Please enter an invite code");
    //         return;
    //     }
    //     fetchSchema(inviteCode);
    // };

    const handleSubmit = (e) => {
        e.preventDefault();
        if (!schema) {
            alert("Please fetch the schema first");
            return;
        }
        submitMemberData(formData);
        setJoined(true);
    };

    return (
        <div className="join-org-container">
            {showInvite ? (
                <div className="invite-form">
                    <h1>Join an Organization</h1>
                    <input 
                        type="text"
                        placeholder="Enter Invite Code"
                        value={inviteCode}
                        onChange={(e) => setInviteCode(e.target.value)}
                    />
                    <button onClick={() => fetchSchema(inviteCode)}>Fetch Form</button>
                </div>
            ) : (
                joined ? (
                    <div className="join-confirm">
                        <button onClick={() => window.location.href = "/Home"}>Go to Dashboard</button>
                    </div>
                ) : (
                    schema && (
                        <form className="org-form" onSubmit={handleSubmit}>
                            {schema.fields.map((field) => (
                                <div key={field.name} className="form-group">
                                    <label>{field.label}</label>
                                    <input 
                                        type={field.type}
                                        name={field.name}
                                        value={formData[field.name] || ""}
                                        onChange={(e) => setFormData({...formData, [e.target.name]: e.target.value})}
                                        required={field.required}
                                    />
                                </div>
                            ))}
                            <button type="submit">Join</button>
                        </form>
                    )
                )
            )}
            {error && <p style={{ color: "red" }}>{error}</p>}
            {successMessage && <p className="success-message">{successMessage}</p>}
        </div>
    );    
};

export default JoinOrg;