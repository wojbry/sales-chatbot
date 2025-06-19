// src/App.js
import React from 'react';
import LookerDashboard from './components/LookerDashboard';
import ChatAgent from './components/ChatAgent';
import './App.css'; // Import the CSS file

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
      </main>
      <footer className="App-footer">
        <p>&copy; 2024 AI Sales Analytics Project</p>
      </footer>
    </div>
  );
}

export default App;