import React from 'react';
import Dashboard from './components/Dashboard';
import './index.css';

function App() {
  return (
    <div className="app-container">
      <header>
        <h1>🌉 Bridge Health Monitoring System</h1>
      </header>
      <main>
        <Dashboard />
      </main>
    </div>
  );
}

export default App;