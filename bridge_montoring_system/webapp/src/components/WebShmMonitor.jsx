import React, { useState, useEffect, useCallback } from 'react';
import axios from 'axios';
import { Line, Bar } from 'react-chartjs-2';
import {
  Chart as ChartJS, CategoryScale, LinearScale, PointElement,
  LineElement, BarElement, Title, Tooltip, Legend,
} from 'chart.js';

ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, BarElement, Title, Tooltip, Legend);

const API_URL = 'http://localhost:5001/api/status';

// Helper to safely parse stringified array from Flask
const safeParse = (data) => {
    try {
        return data ? JSON.parse(data) : [];
    } catch (e) {
        return [];
    }
};

function WebShmMonitor() {
  const [plotData, setPlotData] = useState({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchPlotData = useCallback(async () => {
    try {
      const response = await axios.get(API_URL);
      const data = response.data;
      
      // Parse all necessary arrays
      setPlotData({
        ...data,
        // The API returns the plotting arrays as JSON strings, so we must parse them
        rms_window: safeParse(data.rms_window),
        fft_power: safeParse(data.fft_power),
        fft_freqs: safeParse(data.fft_freqs),
        energy_dist: safeParse(data.energy_dist),
        freq_history: safeParse(data.freq_history),
        damage_history: safeParse(data.damage_history),
      });
      setError(null);
    } catch (err) {
      setError(`Failed to fetch high-fidelity plot data. Ensure 'app.py' is running and the ESP32 is connected.`);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchPlotData(); 
    // Set fetch interval to 1000ms (1 Hz) to match server update frequency
    const interval = setInterval(fetchPlotData, 1000); 
    return () => clearInterval(interval); 
  }, [fetchPlotData]);

  if (loading) return <div className="chart-container">Loading Real-Time Plots...</div>;
  if (error) return <div className="chart-container error">{error}</div>;

  // --- Chart Data Generators ---

  // 1. Raw RMS Signal Plot
  const rmsChartData = {
    labels: plotData.rms_window.map((_, i) => i),
    datasets: [{
      label: 'Raw RMS Window (g)',
      data: plotData.rms_window,
      borderColor: '#3498db',
      pointRadius: 0,
      tension: 0.1,
    }],
  };
  // 2. FFT Spectrum Plot
  const fftChartData = {
    labels: plotData.fft_freqs.map(f => f.toFixed(1)),
    datasets: [{
      label: 'Current Power Spectrum',
      data: plotData.fft_power,
      borderColor: '#e74c3c',
      pointRadius: 1,
      tension: 0.1,
    }],
  };
  // 3. Natural Frequency History Plot
  const freqHistoryChartData = {
    labels: plotData.freq_history.map((_, i) => i),
    datasets: [{
      label: 'Natural Frequency (Hz)',
      data: plotData.freq_history,
      borderColor: '#9b59b6',
      pointRadius: 2,
    }],
  };
  // 4. Damage Index History Plot
  const damageChartData = {
    labels: plotData.damage_history.map((_, i) => i),
    datasets: [{
      label: 'Damage Index (%)',
      data: plotData.damage_history,
      borderColor: '#f39c12',
      pointRadius: 2,
    }],
  };
  // 5. Energy Distribution Plot
  const energyChartData = {
    labels: ['0-5Hz', '5-15Hz', '15-30Hz', '30-60Hz', '60-100Hz'],
    datasets: [{
      label: 'Energy Distribution',
      data: plotData.energy_dist,
      backgroundColor: ['#1abc9c', '#2ecc71', '#f1c40f', '#e67e22', '#c0392b'],
    }],
  };


  return (
    <>
    <h2 style={{marginTop: '2rem'}}>📈 Advanced SHM Modal Analysis Results (Real-Time Serial Feed)</h2>
    <div className="status-grid" style={{gridTemplateColumns: 'repeat(auto-fit, minmax(400px, 1fr))'}}>
      <div className="chart-container">
        <h3>1. Raw RMS Signal (Last 500 Samples)</h3>
        <div style={{ height: '300px' }}><Line data={rmsChartData} options={{scales: {x: {display: false}}}} /></div>
      </div>

      <div className="chart-container">
        <h3>2. Frequency Spectrum</h3>
        <div style={{ height: '300px' }}><Line data={fftChartData} options={{scales: {x: {title: {display: true, text: 'Frequency (Hz)'}}, y: {beginAtZero: true}}}} /></div>
      </div>

      <div className="chart-container">
        <h3>3. Natural Frequency Trend (Last 100)</h3>
        <div style={{ height: '300px' }}><Line data={freqHistoryChartData} /></div>
      </div>
      
      <div className="chart-container">
        <h3>4. Damage Index Trend (Last 100)</h3>
        <div style={{ height: '300px' }}><Line data={damageChartData} /></div>
      </div>
      
      <div className="chart-container" style={{gridColumn: 'span 2'}}>
        <h3>5. Energy Distribution</h3>
        <div style={{ height: '300px' }}><Bar data={energyChartData} /></div>
      </div>
    </div>
    </>
  );
}

export default WebShmMonitor;