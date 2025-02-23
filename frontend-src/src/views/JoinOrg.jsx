import React, { useState } from 'react';
import "../styles/JoinOrg.css";

const JoinOrg = ({schema, error, successMessage, fetchSchema, submitMemberData, inviteCode, setInviteCode}) => {
    const [formData, setFormData] = useState({});

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
    };

    return (
        <div className="join-org-container">
            <h1>Join an Organization</h1>
            <input 
                type="text"
                placeholder="Enter Invite Code"
                value={inviteCode}
                onChange={(e) => setInviteCode(e.target.value)}
            />
            <button onClick={() => fetchSchema(inviteCode)}>Fetch Form</button>

            {schema && (
                <form onSubmit={handleSubmit}>
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
            )}
            {error && <p style={{ color: "red" }}>{error}</p>}
            {successMessage && <p style={{ color: "green" }}>{successMessage}</p>}
        </div>
    );
};

export default JoinOrg;