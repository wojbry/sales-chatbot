// src/components/GoogleCalendarEmbed.js
import React from 'react';

const GoogleCalendarEmbed = () => {
    // IMPORTANT: Paste your customized embed code here, obtained from Google Calendar settings.
    // Ensure you set 'default view' to 'Month' and customize other options as desired.
    const embedCode = `
        <iframe src="></iframe>
    `;

    return (
        <div className="google-calendar-embed-container">
            <h2>Upcoming Promotion Campaigns</h2>
            <div dangerouslySetInnerHTML={{ __html: embedCode }} />
            {/* Note: dangerouslySetInnerHTML is used because iframe is raw HTML. */}
            {/* This is safe here as the source is trusted. */}
        </div>
    );
};

export default GoogleCalendarEmbed;