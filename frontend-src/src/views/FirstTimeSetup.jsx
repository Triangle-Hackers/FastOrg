import React from 'react';
import '../styles/FirstTimeSetup.css';

const SetupWizard = ({
  loading,
  isNewUser,
  error,
  onFinishSetup
}) => {
  if (loading) return <div>Loading setup wizard...</div>;
  if (error) return <div>{error}</div>;

  if (!isNewUser) {
    return <div>You already completed setup</div>;
  }

  const handleSubmit = (e) => {
    e.preventDefault();
    const org_name = e.target.org_name.value.trim();
    
    if (!org_name) {
      alert('Please enter an organization name');
      return;
    }
    
    const formData = { org_name };
    console.log('Submitting form data:', formData); // Add logging
    onFinishSetup(formData);
  };

  return (
    <div className="setup-container">
      <h1>First-Time Setup</h1>
      <form onSubmit={handleSubmit}>
        <div className="form-group">

        </div>
        <div className="form-group">
          <label>What is your organization name?</label>
          <input type="text" name="org_name" />
        </div>
        {/* Add more wizard steps or fields as needed */}
        
        <button type="submit">Complete Setup</button>
      </form>
    </div>
  );
};

export default SetupWizard; 