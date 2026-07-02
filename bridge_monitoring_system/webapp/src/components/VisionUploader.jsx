import React, { useState, useRef } from 'react';

// YOUR ROBOFLOW CONFIGURATION
const ROBOFLOW_API_KEY = "cm89aQXKE5csMXuUBcm3"; 
const WORKFLOW_URL = "https://serverless.roboflow.com/mini-project-alaox/workflows/detect-count-and-visualize";

function VisionUploader() {
  const [selectedFile, setSelectedFile] = useState(null);
  const [preview, setPreview] = useState(null);
  const [analysisResult, setAnalysisResult] = useState(null); 
  const [outputImage, setOutputImage] = useState(null); 
  const [crackCount, setCrackCount] = useState(null); 
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  
  const [isDragging, setIsDragging] = useState(false);
  const fileInputRef = useRef(null);

  // ================= HELPER FUNCTIONS =================

  const fileToBase64 = (file) => {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.readAsDataURL(file);
      reader.onload = () => resolve(reader.result); 
      reader.onerror = (error) => reject(error);
    });
  };

  // ================= FILE HANDLING =================

  const handleFileSelect = (file) => {
    if (file && file.type.startsWith('image/')) {
      setSelectedFile(file);
      setPreview(URL.createObjectURL(file));
      // Reset previous results
      setAnalysisResult(null);
      setOutputImage(null);
      setCrackCount(null);
      setError(null);
    } else {
      setError("Please upload a valid image file.");
    }
  };

  const onInputChange = (event) => {
    const file = event.target.files[0];
    handleFileSelect(file);
  };

  const onDragOver = (e) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const onDragLeave = (e) => {
    e.preventDefault();
    setIsDragging(false);
  };

  const onDrop = (e) => {
    e.preventDefault();
    setIsDragging(false);
    const file = e.dataTransfer.files[0];
    handleFileSelect(file);
  };

  const onClickUpload = () => {
    fileInputRef.current.click();
  };

  // ================= API ANALYSIS =================

  const onAnalyze = async () => {
    if (!selectedFile) return;
    setLoading(true);
    setError(null);
    setOutputImage(null);
    setCrackCount(null);

    try {
      const base64File = await fileToBase64(selectedFile);
      const pureBase64 = base64File.split(',')[1]; 

      const response = await fetch(WORKFLOW_URL, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          api_key: ROBOFLOW_API_KEY,
          inputs: {
            "image": { "type": "base64", "value": pureBase64 }
          }
        })
      });

      const result = await response.json();
      if (result.error) throw new Error(result.error.message);
      
      setAnalysisResult(result);

      if (result.outputs && result.outputs.length > 0) {
        const outputData = result.outputs[0];
        if (outputData.output_image && outputData.output_image.value) {
            setOutputImage(outputData.output_image.value);
        }
        if (outputData.predictions !== undefined) {
            setCrackCount(outputData.predictions);
        }
      } else {
          console.warn("Unexpected JSON structure", result);
      }

    } catch (err) {
      console.error(err);
      setError(err.message || 'Analysis failed');
    } finally {
      setLoading(false);
    }
  };

  // ================= RENDER =================

  return (
    <div className="vision-uploader card" style={{ 
      display: 'flex', 
      flexDirection: 'column', 
      height: '600px', 
      padding: '0',    
      background: '#fff', 
      border: '1px solid #ddd', 
      borderRadius: '8px',
      overflow: 'hidden' // PREVENTS ENTIRE CARD SCROLLING
    }}>
      
      {/* 1. HEADER (Fixed at Top) */}
      <div style={{ 
        padding: '20px', 
        borderBottom: '1px solid #eee', 
        backgroundColor: '#fff', 
        zIndex: 10,
        flexShrink: 0 
      }}>
        <h2 style={{marginTop: 0, marginBottom: '15px'}}>Crack Detection Model</h2>
        
        {/* Upload Box */}
        <div 
          onDragOver={onDragOver}
          onDragLeave={onDragLeave}
          onDrop={onDrop}
          onClick={onClickUpload}
          style={{
            border: isDragging ? '2px dashed #3498db' : '2px dashed #ccc',
            borderRadius: '8px',
            padding: '10px',
            textAlign: 'center',
            cursor: 'pointer',
            backgroundColor: isDragging ? '#f0f8ff' : '#fafafa',
            marginBottom: '10px'
          }}
        >
          <input 
            type="file" 
            accept="image/*" 
            onChange={onInputChange} 
            ref={fileInputRef} 
            style={{ display: 'none' }} 
          />
          <p style={{ margin: 0, color: '#555', fontSize: '0.9em' }}>
            {isDragging ? "Drop here..." : "Drag & Drop or Click to Upload"}
          </p>
        </div>

        {/* Buttons */}
        <button 
          onClick={onAnalyze} 
          disabled={!selectedFile || loading}
          style={{ 
            width: '100%',
            padding: '10px', 
            background: loading ? '#ccc' : '#3498db', 
            color: 'white', 
            border: 'none', 
            borderRadius: '4px',
            cursor: loading ? 'not-allowed' : 'pointer',
            fontWeight: 'bold'
          }}
        >
          {loading ? 'Processing...' : 'Run Analysis'}
        </button>

        {error && <div style={{color: 'red', marginTop: '5px', textAlign:'center', fontSize: '0.9em'}}>{error}</div>}
      </div>

      {/* 2. CONTENT AREA (Flex Layout) */}
      <div style={{ 
        flex: 1,           
        display: 'flex',
        flexDirection: 'column',
        padding: '15px',
        overflow: 'hidden',
        minHeight: 0
      }}>
        
        {/* A. IMAGE SECTION (Takes all available space) */}
        <div style={{ 
          flex: 1, 
          minHeight: 0, 
          display: 'flex', 
          flexDirection: 'column', 
          alignItems: 'center', 
          justifyContent: 'center',
          marginBottom: '10px',
          overflow: 'hidden'
        }}>
          {outputImage ? (
              <img 
                src={`data:image/jpeg;base64,${outputImage}`} 
                alt="Result" 
                style={{
                  maxWidth: '100%', 
                  maxHeight: '100%', 
                  objectFit: 'contain',
                  border: '2px solid #2ecc71', 
                  borderRadius:'4px'
                }} 
              />
          ) : preview ? (
              <img 
                src={preview} 
                alt="Input" 
                style={{ 
                  maxWidth: '100%', 
                  maxHeight: '100%', 
                  objectFit: 'contain',
                  borderRadius: '4px', 
                  border: '1px solid #eee' 
                }} 
              />
          ) : (
            <p style={{color: '#ccc'}}>No image selected</p>
          )}
        </div>

        {/* B. JSON SECTION (Has internal scroll) */}
        {analysisResult && (
          <div style={{ flexShrink: 0 }}>
            <details style={{ 
              background: '#f8f9fa', 
              border: '1px solid #eee',
              borderRadius: '4px',
              padding: '5px',
            }}>
              <summary style={{cursor:'pointer', color:'#555', fontWeight:'bold', fontSize:'0.8em', marginBottom: '5px'}}>
                Show Raw JSON
              </summary>
              <div style={{
                backgroundColor: '#fff',
                border: '1px solid #ccc',
                padding: '5px',
                borderRadius: '4px'
              }}>
                <pre style={{ 
                  margin: 0, 
                  fontSize: '10px', 
                  whiteSpace: 'pre-wrap', 
                  wordBreak: 'break-all',
                  maxHeight: '150px',       // LIMIT HEIGHT
                  overflowY: 'auto'         // ENABLE SCROLL ONLY HERE
                }}>
                  {JSON.stringify(analysisResult, (key, value) => {
                    if ((key === 'value' || key === 'base64') && typeof value === 'string' && value.length > 50) {
                      return "<Base64 Omitted>"; 
                    }
                    return value;
                  }, 2)}
                </pre>
              </div>
            </details>
          </div>
        )}

      </div>
    </div>
  );
}

export default VisionUploader;