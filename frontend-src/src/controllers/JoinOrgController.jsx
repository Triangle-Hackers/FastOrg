import {useState, useEffect} from "react";
import JoinOrg from "../views/JoinOrg";

const JoinOrgController = () => {
    const [schema, setSchema] = useState(null);
    const [error, setError] = useState(null);
    const [successMessage, setSuccessMessage] = useState(null);
    const [inviteCode, setInviteCode] = useState("");

    // fetch schema from backend based on invite code
    const fetchSchema = async (inviteCode) => {
        try {
            setError(null); // clear any existing errors
            setSchema(null); // clear any existing schema

            // Add debug logging
            console.log("Received inviteCode:", inviteCode);

            if (!inviteCode || typeof inviteCode === 'undefined') {
                setError("Please enter an invite code.");
                return;
            }

            if (!inviteCode.trim()) {
                setError("Please enter an invite code.");
                return;
            }

            console.log("Fetching schema for invite code:", inviteCode);

            const response = await fetch(`http://127.0.0.1:8000/get-schema?invite_code=${inviteCode}`, {
                // credentials: "include",
                method: "GET",
                headers: {
                    "Accept": "application/json",
                    "Content-Type": "application/json",
                },
            });

            console.log("Response:", response);

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || "Failed to fetch schema");
            }

            const schemaData = await response.json();
            console.log("Schema data:", schemaData);
            setSchema(schemaData);

        } catch (err) {
            console.log("Error:", err.message);
            setError(err.message);
        }
    };

    // Submit the form data to join the organization
    const submitMemberData = async (formData) => {
        try {
            setError(null); // clear any existing errors
            setSuccessMessage(null); // clear any existing success messages

            const response = await fetch(
                `http://127.0.0.1:8000/join-org?invite_code=${inviteCode}`, 
                {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json",
                    },
                    body: JSON.stringify(formData),
                    // credentials: "include",
                }
        );

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || "Failed to join organization");
            }
            setSuccessMessage("You have successfully joined the organization");
        } catch (err) {
            setError(err.message);
        }
    };

    return (
        <JoinOrg 
            schema={schema} 
            error={error} 
            successMessage={successMessage} 
            fetchSchema={fetchSchema} 
            submitMemberData={submitMemberData}
            inviteCode={inviteCode}
            setInviteCode={setInviteCode} />
    );
};

export default JoinOrgController;