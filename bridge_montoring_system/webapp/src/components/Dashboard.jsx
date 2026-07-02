import React, { useState, useEffect, useCallback } from 'react';
import axios from 'axios';
import HealthChart from './HealthChart';
import VisionUploader from './VisionUploader'; // Import the Roboflow component
import Flowchart from './flowchart'; // Import the Flowchart component

// Frontend fetches from Port 5001 (Flask)
const API_URL = 'http://localhost:5001/api/status';

// Helper: Map backend status strings to CSS classes for color
const getStatusClass = (status) => {
  if (!status) return 'default';
  if (status.includes('HEALTHY') || status.includes('NORMAL')) return 'good';
  if (status.includes('WARNING') || status.includes('CAUTION')) return 'warning';
  if (status.includes('CRITICAL') || status.includes('LEAK') || status.includes('DAMAGED')) return 'poor';
  return 'default';
};

// Component: Single Status Card
const StatusCard = ({ title, value, statusClass }) => (
  <div className="status-card">
    <h3>{title}</h3>
    <p className={`status-text ${statusClass}`}>
      {value}
    </p>
  </div>
);

function Dashboard() {
  const [latestStatus, setLatestStatus] = useState({});
  const [historicalTrends, setHistoricalTrends] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchData = useCallback(async () => {
    try {
      const response = await axios.get(API_URL);
      const data = response.data;

      setLatestStatus(data);

      // --- PROCESS HISTORICAL DATA FOR GRAPHS ---
      const processedTrends = (data.historical_trends || []).map(item => {
        let crackCount = 0;
        try {
          if (item.predictions) {
            const preds = typeof item.predictions === 'string'
              ? JSON.parse(item.predictions)
              : item.predictions;

            if (Array.isArray(preds)) {
              crackCount = preds.length;
            }
          }
        } catch (e) {
          console.warn("Failed to parse predictions JSON", e);
          crackCount = 0;
        }

        return {
          ...item,
          crack_count: crackCount
        };
      });

      setHistoricalTrends(processedTrends);
      setError(null);
      setLoading(false);
    } catch (err) {
      console.error('Failed to fetch data:', err);
      if (loading) setError('Connection Lost. Ensure Backend is running.');
    }
  }, [loading]);

  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, 1000);
    return () => clearInterval(interval);
  }, [fetchData]);

  // --- Data Formatting ---
  const statusStr = latestStatus.shm_health_status || 'LOADING...';
  const rmsValue = latestStatus.rms_current_1 ? latestStatus.rms_current_1.toFixed(4) : '0.0000';
  const flexValue = latestStatus.flex_raw !== undefined ? latestStatus.flex_raw : '...';

  const isWaterDetected = latestStatus.float_status === 0;
  const waterText = isWaterDetected ? "WATER DETECTED" : "DRY";
  const waterClass = isWaterDetected ? "poor" : "good";

  // Common style for chart sections
  const sectionStyle = {
    marginBottom: '30px',
    backgroundColor: 'white',
    padding: '15px',
    borderRadius: '8px',
    boxShadow: '0 2px 4px rgba(0,0,0,0.05)'
  };

  return (
    <div className="dashboard">
      <h1 className="dashboard-title">Bridge Health Monitoring System</h1>

      {/* 1. STATUS CARDS ROW */}
      <div className="status-grid">
        <StatusCard
          title="System Status"
          value={statusStr}
          statusClass={getStatusClass(statusStr)}
        />
        <StatusCard
          title="Vibration (RMS)"
          value={`${rmsValue} g`}
          statusClass={parseFloat(rmsValue) > 0.15 ? 'warning' : 'good'}
        />
        <StatusCard
          title="Flex Sensor"
          value={flexValue}
          statusClass={flexValue > 3000 ? 'warning' : 'default'}
        />
        <StatusCard
          title="Water Level"
          value={waterText}
          statusClass={waterClass}
        />
      </div>

      {error && <p className="error" style={{ textAlign: 'center', marginTop: '1rem' }}>{error}</p>}

      {/* 2. VERTICAL CONTENT STACK */}
      <div className="content-stack" style={{ display: 'flex', flexDirection: 'column', gap: '20px', marginTop: '30px' }}>

        {/* SECTION A: FIRST 3 GRAPHS */}
        <div style={sectionStyle}>
          <h3>Vibration RMS Trend</h3>
          <HealthChart
            sensorData={historicalTrends}
            dataKey="rms_1"
            label="Avg RMS (g)"
            color="#3498db"
          />
        </div>

        <div style={sectionStyle}>
          <h3>Flex Sensor Trend</h3>
          <HealthChart
            sensorData={historicalTrends}
            dataKey="flex_mean"
            label="Flex Value"
            color="#9b59b6"
          />
        </div>

        <div style={sectionStyle}>
          <h3>Structural Damage Index</h3>
          <HealthChart
            sensorData={historicalTrends}
            dataKey="max_damage"
            label="Damage Index (%)"
            color="#e74c3c"
          />
        </div>

        {/* SECTION B: CRACK DETECTION MODEL */}
        <div className="vision-section" style={{ ...sectionStyle, padding: '0', overflow: 'hidden' }}>
          {/* Note: VisionUploader has its own internal padding/styling */}
          <VisionUploader />
        </div>

        {/* SECTION C: DETECTED CRACKS TREND (Below Model) */}
        <div style={sectionStyle}>
          <h3>Detected Cracks Trend</h3>
          <HealthChart
            sensorData={historicalTrends}
            dataKey="crack_count"
            label="Crack Count"
            color="#2ecc71"
          />
        </div>
      </div>
    </div>
  );
}
export default Dashboard;