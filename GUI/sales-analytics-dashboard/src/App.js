// src/App.js (partial example)
import React from 'react';
import LookerDashboard from './components/LookerDashboard';
import ChatAgent from './components/ChatAgent';
import GoogleCalendarEmbed from './components/GoogleCalendarEmbed'; // Import the new component
import './App.css';

function App() {
  return (
    <div className="App">
      <header className="App-header">
        <h1>AI-Powered Sales Insights</h1>
      </header>
      <main className="App-main-content">
        <section className="dashboard-section">
          <LookerDashboard />
        </section>
        <section className="chat-section">
          <ChatAgent />
        </section>
        <section className="calendar-section">
          <GoogleCalendarEmbed />
        </section>
      </main>
      <footer className="App-footer">
        <p>&copy; 2024 AI Sales Analytics Project</p>
      </footer>
    </div>
  );
}

export default App;