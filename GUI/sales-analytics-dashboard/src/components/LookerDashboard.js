// src/components/LookerDashboard.js
import React from 'react';

// IMPORTANT: Replace with your actual Looker Studio Embed URL
const LOOKER_STUDIO_EMBED_URL = "";

const LookerDashboard = () => {
    return (
        <div className="looker-dashboard-container">
            <h2>Sales Dashboard</h2>
            {LOOKER_STUDIO_EMBED_URL === "YOUR_LOOKER_STUDIO_EMBED_URL" ? (
                <p>Please replace "YOUR_LOOKER_STUDIO_EMBED_URL" in src/components/LookerDashboard.js with your actual Looker Studio embed URL.</p>
            ) : (
                <iframe
                    title="Sales Analytics Dashboard"
                    width="100%"
                    height="100%"
                    src={LOOKER_STUDIO_EMBED_URL}
                    frameBorder="0"
                    style={{ border: 0 }}
                    allowFullScreen
                    sandbox="allow-storage-access-by-user-activation allow-scripts allow-forms allow-popups allow-popups-to-escape-sandbox allow-same-origin allow-top-navigation-by-user-activation"
                ></iframe>
            )}
        </div>
    );
};

export default LookerDashboard;