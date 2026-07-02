import React from 'react';

function BridgeMonitoringFlowchart() {
  return (
    <div style={{
      width: '210mm',
      height: '297mm',
      padding: '10mm',
      backgroundColor: 'white',
      fontFamily: 'Arial, sans-serif',
      fontSize: '7px',
      margin: '0 auto',
      boxSizing: 'border-box',
      position: 'relative'
    }}>
      <div style={{
        textAlign: 'center',
        fontSize: '14px',
        fontWeight: 'bold',
        marginBottom: '8px',
        color: '#1a1a1a'
      }}>
        Bridge Health Monitoring System - Complete Flowchart
      </div>

      <svg width="100%" height="100%" viewBox="0 0 800 1050" style={{border: '1px solid #e0e0e0'}}>
        <defs>
          <marker id="arrowhead" markerWidth="10" markerHeight="10" refX="9" refY="3" orient="auto">
            <polygon points="0 0, 10 3, 0 6" fill="#333" />
          </marker>
          
          <filter id="shadow" x="-50%" y="-50%" width="200%" height="200%">
            <feDropShadow dx="1" dy="1" stdDeviation="1" floodOpacity="0.3"/>
          </filter>
        </defs>

        <ellipse cx="400" cy="20" rx="60" ry="15" fill="#90EE90" stroke="#333" strokeWidth="1.5" filter="url(#shadow)"/>
        <text x="400" y="24" textAnchor="middle" fontSize="9" fontWeight="bold">System Start</text>
        
        <rect x="340" y="45" width="120" height="35" rx="3" fill="#87CEEB" stroke="#333" strokeWidth="1.5" filter="url(#shadow)"/>
        <text x="400" y="58" textAnchor="middle" fontSize="8" fontWeight="bold">ESP32 Setup</text>
        <text x="400" y="68" textAnchor="middle" fontSize="7">MPU6050, Flex,</text>
        <text x="400" y="76" textAnchor="middle" fontSize="7">Float Sensors</text>

        <path d="M 400 100 L 440 125 L 400 150 L 360 125 Z" fill="#FFE4B5" stroke="#333" strokeWidth="1.5" filter="url(#shadow)"/>
        <text x="400" y="123" textAnchor="middle" fontSize="7" fontWeight="bold">Calibration</text>
        <text x="400" y="132" textAnchor="middle" fontSize="7" fontWeight="bold">Complete?</text>

        <rect x="50" y="110" width="100" height="40" rx="3" fill="#FFD700" stroke="#333" strokeWidth="1.5" filter="url(#shadow)"/>
        <text x="100" y="123" textAnchor="middle" fontSize="7" fontWeight="bold">Calibration Phase</text>
        <text x="100" y="131" textAnchor="middle" fontSize="6.5">15 seconds</text>
        <text x="100" y="139" textAnchor="middle" fontSize="6.5">Learn Baseline</text>
        <text x="100" y="147" textAnchor="middle" fontSize="6.5">Set Threshold</text>

        <rect x="340" y="170" width="120" height="30" rx="3" fill="#98FB98" stroke="#333" strokeWidth="1.5" filter="url(#shadow)"/>
        <text x="400" y="183" textAnchor="middle" fontSize="8" fontWeight="bold">Monitoring Mode</text>
        <text x="400" y="193" textAnchor="middle" fontSize="7">Read Sensors at 500Hz</text>

        <rect x="340" y="215" width="120" height="25" rx="3" fill="#B0E0E6" stroke="#333" strokeWidth="1.5" filter="url(#shadow)"/>
        <text x="400" y="225" textAnchor="middle" fontSize="7" fontWeight="bold">Calculate RMS</text>
        <text x="400" y="233" textAnchor="middle" fontSize="6.5">Rolling Window</text>

        <path d="M 400 255 L 435 280 L 400 305 L 365 280 Z" fill="#FFE4B5" stroke="#333" strokeWidth="1.5" filter="url(#shadow)"/>
        <text x="400" y="278" textAnchor="middle" fontSize="7" fontWeight="bold">RMS Exceeds</text>
        <text x="400" y="286" textAnchor="middle" fontSize="7" fontWeight="bold">Threshold?</text>

        <rect x="210" y="265" width="90" height="30" rx="3" fill="#FF6B6B" stroke="#333" strokeWidth="1.5" filter="url(#shadow)"/>
        <text x="255" y="276" textAnchor="middle" fontSize="7" fontWeight="bold">DAMAGED</text>
        <text x="255" y="284" textAnchor="middle" fontSize="6">Alert + LED Blink</text>
        <text x="255" y="291" textAnchor="middle" fontSize="6">Slow</text>

        <rect x="500" y="265" width="90" height="30" rx="3" fill="#4CAF50" stroke="#333" strokeWidth="1.5" filter="url(#shadow)"/>
        <text x="545" y="276" textAnchor="middle" fontSize="7" fontWeight="bold">NORMAL</text>
        <text x="545" y="284" textAnchor="middle" fontSize="6">LED OFF</text>

        <rect x="340" y="320" width="120" height="30" rx="3" fill="#DDA0DD" stroke="#333" strokeWidth="1.5" filter="url(#shadow)"/>
        <text x="400" y="331" textAnchor="middle" fontSize="7" fontWeight="bold">Serial CSV Output</text>
        <text x="400" y="339" textAnchor="middle" fontSize="6">timestamp, RMS, mag,</text>
        <text x="400" y="346" textAnchor="middle" fontSize="6">water, flex, status</text>

        <rect x="60" y="370" width="100" height="35" rx="3" fill="#9370DB" stroke="#333" strokeWidth="1.5" filter="url(#shadow)"/>
        <text x="110" y="382" textAnchor="middle" fontSize="8" fontWeight="bold">Python Backend</text>
        <text x="110" y="390" textAnchor="middle" fontSize="7">main.py</text>
        <text x="110" y="398" textAnchor="middle" fontSize="7">Serial Worker</text>

        <rect x="640" y="370" width="100" height="35" rx="3" fill="#00BCD4" stroke="#333" strokeWidth="1.5" filter="url(#shadow)"/>
        <text x="690" y="382" textAnchor="middle" fontSize="7" fontWeight="bold">Matplotlib Monitor</text>
        <text x="690" y="390" textAnchor="middle" fontSize="6.5">Real-time 8 Plots</text>
        <text x="690" y="398" textAnchor="middle" fontSize="6.5">CSV Logging</text>

        <rect x="60" y="425" width="100" height="40" rx="3" fill="#8A2BE2" stroke="#333" strokeWidth="1.5" filter="url(#shadow)"/>
        <text x="110" y="438" textAnchor="middle" fontSize="7" fontWeight="bold">FFT Analysis</text>
        <text x="110" y="446" textAnchor="middle" fontSize="6">Natural Frequency</text>
        <text x="110" y="453" textAnchor="middle" fontSize="6">Energy Distribution</text>
        <text x="110" y="460" textAnchor="middle" fontSize="6">Damage Index</text>

        <rect x="60" y="485" width="100" height="45" rx="3" fill="#FF8C00" stroke="#333" strokeWidth="1.5" filter="url(#shadow)"/>
        <text x="110" y="497" textAnchor="middle" fontSize="7" fontWeight="bold">Health Status</text>
        <text x="110" y="505" textAnchor="middle" fontSize="6">CRITICAL LEAK</text>
        <text x="110" y="512" textAnchor="middle" fontSize="6">CRITICAL DAMAGE</text>
        <text x="110" y="519" textAnchor="middle" fontSize="6">WARNING DAMAGE</text>
        <text x="110" y="526" textAnchor="middle" fontSize="6">HEALTHY</text>

        <rect x="60" y="550" width="100" height="30" rx="3" fill="#20B2AA" stroke="#333" strokeWidth="1.5" filter="url(#shadow)"/>
        <text x="110" y="562" textAnchor="middle" fontSize="7" fontWeight="bold">Aggregation</text>
        <text x="110" y="570" textAnchor="middle" fontSize="6.5">Every 3 Seconds</text>
        <text x="110" y="577" textAnchor="middle" fontSize="6.5">Avg RMS, Flex</text>

        <ellipse cx="110" cy="615" rx="50" ry="20" fill="#9370DB" stroke="#333" strokeWidth="1.5" filter="url(#shadow)"/>
        <text x="110" y="612" textAnchor="middle" fontSize="7" fontWeight="bold">MySQL DB</text>
        <text x="110" y="620" textAnchor="middle" fontSize="6">shm trend log</text>

        <rect x="230" y="545" width="100" height="40" rx="3" fill="#FF9800" stroke="#333" strokeWidth="1.5" filter="url(#shadow)"/>
        <text x="280" y="558" textAnchor="middle" fontSize="8" fontWeight="bold">Flask API</text>
        <text x="280" y="566" textAnchor="middle" fontSize="7">Port 5001</text>
        <text x="280" y="573" textAnchor="middle" fontSize="6">/api/status</text>
        <text x="280" y="580" textAnchor="middle" fontSize="6">/api/update vision</text>

        <rect x="380" y="545" width="110" height="40" rx="3" fill="#2196F3" stroke="#333" strokeWidth="1.5" filter="url(#shadow)"/>
        <text x="435" y="558" textAnchor="middle" fontSize="8" fontWeight="bold">React Dashboard</text>
        <text x="435" y="566" textAnchor="middle" fontSize="7">Fetch Every 1s</text>
        <text x="435" y="573" textAnchor="middle" fontSize="6">Status Cards</text>
        <text x="435" y="580" textAnchor="middle" fontSize="6">Historical Charts</text>

        <rect x="380" y="605" width="110" height="50" rx="3" fill="#64B5F6" stroke="#333" strokeWidth="1.5" filter="url(#shadow)"/>
        <text x="435" y="618" textAnchor="middle" fontSize="7" fontWeight="bold">Display Charts</text>
        <text x="435" y="626" textAnchor="middle" fontSize="6">RMS Trend</text>
        <text x="435" y="633" textAnchor="middle" fontSize="6">Flex Trend</text>
        <text x="435" y="640" textAnchor="middle" fontSize="6">Damage Index</text>
        <text x="435" y="647" textAnchor="middle" fontSize="6">Crack Count</text>
        <text x="435" y="654" textAnchor="middle" fontSize="6">HealthChart.jsx</text>

        <rect x="540" y="605" width="110" height="50" rx="3" fill="#E91E63" stroke="#333" strokeWidth="1.5" filter="url(#shadow)"/>
        <text x="595" y="618" textAnchor="middle" fontSize="7" fontWeight="bold">Vision Upload</text>
        <text x="595" y="626" textAnchor="middle" fontSize="6">VisionUploader.jsx</text>
        <text x="595" y="633" textAnchor="middle" fontSize="6">Image to Base64</text>
        <text x="595" y="640" textAnchor="middle" fontSize="6">Roboflow API</text>
        <text x="595" y="647" textAnchor="middle" fontSize="6">Crack Detection</text>
        <text x="595" y="654" textAnchor="middle" fontSize="6">Display Results</text>

        <rect x="20" y="700" width="760" height="330" rx="5" fill="#F5F5F5" stroke="#666" strokeWidth="2"/>
        <text x="400" y="720" textAnchor="middle" fontSize="11" fontWeight="bold">System Architecture and Data Flow</text>

        <rect x="40" y="735" width="720" height="70" rx="3" fill="#E8F5E9" stroke="#4CAF50" strokeWidth="2"/>
        <text x="400" y="750" textAnchor="middle" fontSize="9" fontWeight="bold">Layer 1: Hardware (ESP32)</text>
        
        <rect x="60" y="760" width="150" height="35" rx="2" fill="#C8E6C9" stroke="#333" strokeWidth="1"/>
        <text x="135" y="772" textAnchor="middle" fontSize="7" fontWeight="bold">Sensors</text>
        <text x="135" y="780" textAnchor="middle" fontSize="6">MPU6050 (500Hz)</text>
        <text x="135" y="787" textAnchor="middle" fontSize="6">Flex + Float</text>

        <rect x="230" y="760" width="150" height="35" rx="2" fill="#C8E6C9" stroke="#333" strokeWidth="1"/>
        <text x="305" y="772" textAnchor="middle" fontSize="7" fontWeight="bold">Processing</text>
        <text x="305" y="780" textAnchor="middle" fontSize="6">15s Calibration</text>
        <text x="305" y="787" textAnchor="middle" fontSize="6">RMS Calculation</text>

        <rect x="400" y="760" width="150" height="35" rx="2" fill="#C8E6C9" stroke="#333" strokeWidth="1"/>
        <text x="475" y="772" textAnchor="middle" fontSize="7" fontWeight="bold">Output</text>
        <text x="475" y="780" textAnchor="middle" fontSize="6">Serial at 115200</text>
        <text x="475" y="787" textAnchor="middle" fontSize="6">CSV Format</text>

        <rect x="570" y="760" width="170" height="35" rx="2" fill="#C8E6C9" stroke="#333" strokeWidth="1"/>
        <text x="655" y="772" textAnchor="middle" fontSize="7" fontWeight="bold">Status Indicator</text>
        <text x="655" y="780" textAnchor="middle" fontSize="6">LED: Calibrating/Normal/Alert</text>
        <text x="655" y="787" textAnchor="middle" fontSize="6">States: CAL, NORMAL, DAMAGED</text>

        <rect x="40" y="820" width="360" height="95" rx="3" fill="#E3F2FD" stroke="#2196F3" strokeWidth="2"/>
        <text x="220" y="835" textAnchor="middle" fontSize="9" fontWeight="bold">Layer 2: Python Backend (main.py)</text>
        
        <rect x="60" y="845" width="155" height="60" rx="2" fill="#BBDEFB" stroke="#333" strokeWidth="1"/>
        <text x="137" y="857" textAnchor="middle" fontSize="7" fontWeight="bold">Serial Worker Thread</text>
        <text x="137" y="865" textAnchor="middle" fontSize="6">Parse CSV Data</text>
        <text x="137" y="872" textAnchor="middle" fontSize="6">FFT: 1000 samples baseline</text>
        <text x="137" y="879" textAnchor="middle" fontSize="6">Calculate Damage Index</text>
        <text x="137" y="886" textAnchor="middle" fontSize="6">Determine Health Status</text>
        <text x="137" y="893" textAnchor="middle" fontSize="6">3s Aggregation Buffer</text>
        <text x="137" y="900" textAnchor="middle" fontSize="6">Save to MySQL</text>

        <rect x="230" y="845" width="155" height="60" rx="2" fill="#BBDEFB" stroke="#333" strokeWidth="1"/>
        <text x="307" y="857" textAnchor="middle" fontSize="7" fontWeight="bold">Flask Web Server</text>
        <text x="307" y="865" textAnchor="middle" fontSize="6">Port 5001</text>
        <text x="307" y="872" textAnchor="middle" fontSize="6">GET /api/status</text>
        <text x="307" y="879" textAnchor="middle" fontSize="6">POST /api/update vision</text>
        <text x="307" y="886" textAnchor="middle" fontSize="6">GET /api/reset</text>
        <text x="307" y="893" textAnchor="middle" fontSize="6">CORS Enabled</text>
        <text x="307" y="900" textAnchor="middle" fontSize="6">JSON Response</text>

        <rect x="415" y="820" width="345" height="95" rx="3" fill="#FFF3E0" stroke="#FF9800" strokeWidth="2"/>
        <text x="587" y="835" textAnchor="middle" fontSize="9" fontWeight="bold">Parallel: Matplotlib Monitor (monitor matplotlib.py)</text>
        
        <rect x="435" y="845" width="155" height="60" rx="2" fill="#FFE0B2" stroke="#333" strokeWidth="1"/>
        <text x="512" y="857" textAnchor="middle" fontSize="7" fontWeight="bold">Real-Time Visualization</text>
        <text x="512" y="865" textAnchor="middle" fontSize="6">8 Subplot Dashboard</text>
        <text x="512" y="872" textAnchor="middle" fontSize="6">FFT Analysis Independent</text>
        <text x="512" y="879" textAnchor="middle" fontSize="6">Natural Frequency</text>
        <text x="512" y="886" textAnchor="middle" fontSize="6">Energy Distribution</text>
        <text x="512" y="893" textAnchor="middle" fontSize="6">Water/Flex Display</text>
        <text x="512" y="900" textAnchor="middle" fontSize="6">CSV Export</text>

        <rect x="605" y="845" width="140" height="60" rx="2" fill="#FFE0B2" stroke="#333" strokeWidth="1"/>
        <text x="675" y="857" textAnchor="middle" fontSize="7" fontWeight="bold">Plots</text>
        <text x="675" y="865" textAnchor="middle" fontSize="6">1. Vibration vs Threshold</text>
        <text x="675" y="872" textAnchor="middle" fontSize="6">2. Freq Spectrum</text>
        <text x="675" y="879" textAnchor="middle" fontSize="6">3. Natural Freq Shift</text>
        <text x="675" y="886" textAnchor="middle" fontSize="6">4. Damage Index</text>
        <text x="675" y="893" textAnchor="middle" fontSize="6">5-8. Energy/Water/Flex</text>

        <rect x="40" y="930" width="720" height="85" rx="3" fill="#F3E5F5" stroke="#9C27B0" strokeWidth="2"/>
        <text x="400" y="945" textAnchor="middle" fontSize="9" fontWeight="bold">Layer 3: React Frontend (Dashboard.jsx, HealthChart.jsx, VisionUploader.jsx)</text>
        
        <rect x="60" y="955" width="160" height="50" rx="2" fill="#E1BEE7" stroke="#333" strokeWidth="1"/>
        <text x="140" y="967" textAnchor="middle" fontSize="7" fontWeight="bold">Dashboard Component</text>
        <text x="140" y="975" textAnchor="middle" fontSize="6">Polls API every 1s</text>
        <text x="140" y="982" textAnchor="middle" fontSize="6">Status Cards Display</text>
        <text x="140" y="989" textAnchor="middle" fontSize="6">Health/RMS/Flex/Water</text>
        <text x="140" y="996" textAnchor="middle" fontSize="6">Parse JSON predictions</text>

        <rect x="240" y="955" width="160" height="50" rx="2" fill="#E1BEE7" stroke="#333" strokeWidth="1"/>
        <text x="320" y="967" textAnchor="middle" fontSize="7" fontWeight="bold">HealthChart Component</text>
        <text x="320" y="975" textAnchor="middle" fontSize="6">Chart.js Line Charts</text>
        <text x="320" y="982" textAnchor="middle" fontSize="6">4 Trends: RMS, Flex,</text>
        <text x="320" y="989" textAnchor="middle" fontSize="6">Damage, Crack Count</text>
        <text x="320" y="996" textAnchor="middle" fontSize="6">Zoom and Pan Support</text>

        <rect x="420" y="955" width="160" height="50" rx="2" fill="#E1BEE7" stroke="#333" strokeWidth="1"/>
        <text x="500" y="967" textAnchor="middle" fontSize="7" fontWeight="bold">Vision Uploader</text>
        <text x="500" y="975" textAnchor="middle" fontSize="6">Drag and Drop Upload</text>
        <text x="500" y="982" textAnchor="middle" fontSize="6">Image to Base64</text>
        <text x="500" y="989" textAnchor="middle" fontSize="6">Roboflow API Call</text>
        <text x="500" y="996" textAnchor="middle" fontSize="6">Display Annotated Result</text>

        <rect x="600" y="955" width="140" height="50" rx="2" fill="#E1BEE7" stroke="#333" strokeWidth="1"/>
        <text x="670" y="967" textAnchor="middle" fontSize="7" fontWeight="bold">External API</text>
        <text x="670" y="975" textAnchor="middle" fontSize="6">Roboflow Workflow</text>
        <text x="670" y="982" textAnchor="middle" fontSize="6">Crack Detection Model</text>
        <text x="670" y="989" textAnchor="middle" fontSize="6">Returns: Image + Count</text>
        <text x="670" y="996" textAnchor="middle" fontSize="6">POST to /update vision</text>

        <line x1="400" y1="35" x2="400" y2="45" stroke="#333" strokeWidth="2" markerEnd="url(#arrowhead)"/>
        <line x1="400" y1="80" x2="400" y2="100" stroke="#333" strokeWidth="2" markerEnd="url(#arrowhead)"/>
        <line x1="360" y1="125" x2="150" y2="125" stroke="#333" strokeWidth="2" markerEnd="url(#arrowhead)"/>
        <text x="250" y="120" fontSize="7" fill="#d00">No</text>
        <line x1="150" y1="150" x2="400" y2="150" stroke="#333" strokeWidth="2" markerEnd="url(#arrowhead)"/>
        <line x1="400" y1="150" x2="400" y2="170" stroke="#333" strokeWidth="2" markerEnd="url(#arrowhead)"/>
        <text x="420" y="165" fontSize="7" fill="#0a0">Yes</text>
        <line x1="400" y1="200" x2="400" y2="215" stroke="#333" strokeWidth="2" markerEnd="url(#arrowhead)"/>
        <line x1="400" y1="240" x2="400" y2="255" stroke="#333" strokeWidth="2" markerEnd="url(#arrowhead)"/>
        <line x1="365" y1="280" x2="300" y2="280" stroke="#333" strokeWidth="2" markerEnd="url(#arrowhead)"/>
        <text x="320" y="275" fontSize="7" fill="#d00">Yes</text>
        <line x1="435" y1="280" x2="500" y2="280" stroke="#333" strokeWidth="2" markerEnd="url(#arrowhead)"/>
        <text x="460" y="275" fontSize="7" fill="#0a0">No</text>
        <line x1="255" y1="295" x2="255" y2="310" stroke="#333" strokeWidth="2"/>
        <line x1="545" y1="295" x2="545" y2="310" stroke="#333" strokeWidth="2"/>
        <line x1="255" y1="310" x2="400" y2="310" stroke="#333" strokeWidth="2"/>
        <line x1="545" y1="310" x2="400" y2="310" stroke="#333" strokeWidth="2"/>
        <line x1="400" y1="310" x2="400" y2="320" stroke="#333" strokeWidth="2" markerEnd="url(#arrowhead)"/>
        <line x1="340" y1="335" x2="160" y2="335" stroke="#333" strokeWidth="2"/>
        <line x1="160" y1="335" x2="160" y2="370" stroke="#333" strokeWidth="2" markerEnd="url(#arrowhead)"/>
        <line x1="460" y1="335" x2="640" y2="335" stroke="#333" strokeWidth="2"/>
        <line x1="640" y1="335" x2="640" y2="370" stroke="#333" strokeWidth="2" markerEnd="url(#arrowhead)"/>
        <line x1="110" y1="405" x2="110" y2="425" stroke="#333" strokeWidth="2" markerEnd="url(#arrowhead)"/>
        <line x1="110" y1="465" x2="110" y2="485" stroke="#333" strokeWidth="2" markerEnd="url(#arrowhead)"/>
        <line x1="110" y1="530" x2="110" y2="550" stroke="#333" strokeWidth="2" markerEnd="url(#arrowhead)"/>
        <line x1="110" y1="580" x2="110" y2="595" stroke="#333" strokeWidth="2" markerEnd="url(#arrowhead)"/>
        <line x1="160" y1="565" x2="230" y2="565" stroke="#333" strokeWidth="2" markerEnd="url(#arrowhead)"/>
        <line x1="330" y1="565" x2="380" y2="565" stroke="#333" strokeWidth="2" markerEnd="url(#arrowhead)"/>
        <line x1="435" y1="585" x2="435" y2="605" stroke="#333" strokeWidth="2" markerEnd="url(#arrowhead)"/>
        <line x1="490" y1="630" x2="540" y2="630" stroke="#333" strokeWidth="2" markerEnd="url(#arrowhead)"/>
        <line x1="595" y1="655" x2="595" y2="670" stroke="#333" strokeWidth="2"/>
        <line x1="595" y1="670" x2="280" y2="670" stroke="#333" strokeWidth="2"/>
        <line x1="280" y1="670" x2="280" y2="585" stroke="#333" strokeWidth="2" markerEnd="url(#arrowhead)"/>

        <path d="M 690 405 Q 750 500 400 200" fill="none" stroke="#666" strokeWidth="1.5" strokeDasharray="3,3" markerEnd="url(#arrowhead)"/>
        <text x="720" y="340" fontSize="7" fill="#666">Continue</text>
        <text x="720" y="348" fontSize="7" fill="#666">Monitoring</text>
      </svg>
    </div>
  );
}

export default BridgeMonitoringFlowchart;