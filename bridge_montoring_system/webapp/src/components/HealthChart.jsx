// HealthChart.jsx - Updated for Dynamic Units

import React, { useRef } from 'react';
import { Line } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js';
import zoomPlugin from 'chartjs-plugin-zoom';

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  zoomPlugin
);

function HealthChart({ sensorData, dataKey, label, color }) {
  const chartRef = useRef(null);
  
  // Default color if none provided
  const chartColor = color || '#3498db';

  const data = {
    // X-Axis: Time
    labels: sensorData.map(d => new Date(d.timestamp).toLocaleTimeString()),
    datasets: [
      {
        label: label,
        data: sensorData.map(d => d[dataKey]), 
        borderColor: chartColor,
        backgroundColor: chartColor,
        tension: 0.2,        // Slight curve for better visual
        pointRadius: 2,
        pointHoverRadius: 5,
        borderWidth: 2,
      },
    ],
  };
  
  const handleResetZoom = () => {
    if (chartRef.current) {
      chartRef.current.resetZoom();
    }
  };

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    animation: false, // Disable animation for performance with high data rate
    scales: {
      x: {
        ticks: { maxTicksLimit: 8 }
      },
      y: {
        beginAtZero: true
      }
    },
    plugins: {
      zoom: {
        pan: { enabled: true, mode: 'x' },
        zoom: {
          wheel: { enabled: true },
          pinch: { enabled: true },
          mode: 'x',
        },
      },
      tooltip: {
        callbacks: {
          label: function (context) {
            let val = context.parsed.y;
            let labelStr = context.dataset.label || '';
            
            // Dynamic Unit Logic
            let unit = '';
            if (labelStr.includes('Damage')) unit = '%';
            else if (labelStr.includes('Hz')) unit = ' Hz';
            else if (labelStr.includes('RMS')) unit = ' g';
            else if (labelStr.includes('Flex')) unit = ''; // Raw value has no unit
            
            return `${labelStr}: ${val !== null ? val.toFixed(2) : '0'}${unit}`;
          },
          title: function (context) {
            return context[0].label;
          }
        }
      }
    }
  };
  
  return (
    <div style={{ height: '250px', position: 'relative' }}>
      <button 
        onClick={handleResetZoom} 
        style={{ 
          position: 'absolute', 
          right: 0, 
          top: -30,
          padding: '4px 8px',
          cursor: 'pointer',
          fontSize: '0.8rem'
        }}>
        Reset Zoom
      </button>
      <Line ref={chartRef} data={data} options={options} />
    </div>
  );
}

export default HealthChart;