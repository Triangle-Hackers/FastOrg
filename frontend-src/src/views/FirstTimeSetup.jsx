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
    const formData = { /* gather form fields here */ };
    onFinishSetup(formData);
  };

  return (
    <div className="setup-container">
      <h1>First-Time Setup</h1>
      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label>Preferred Name</label>
          <input type="text" name="preferredName" required />
        </div>
        <div className="form-group">
          <label>Favorite Color</label>
          <input type="text" name="favoriteColor" />
        </div>
        {/* Add more wizard steps or fields as needed */}
        
        <button type="submit">Complete Setup</button>
      </form>
    </div>
  );
};

export default SetupWizard; 