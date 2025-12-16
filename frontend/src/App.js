import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './App.css';

const API_BASE_URL = 'http://localhost:8000';

function App() {
  const [images, setImages] = useState([]);
  const [selectedImage, setSelectedImage] = useState(null);
  const [uploadFile, setUploadFile] = useState(null);
  const [query, setQuery] = useState('');
  const [queryResult, setQueryResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);

  // Load images on mount
  useEffect(() => {
    fetchImages();
  }, []);

  const fetchImages = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/api/images`);
      setImages(response.data.images);
    } catch (err) {
      console.error('Error fetching images:', err);
    }
  };

  const handleFileSelect = (event) => {
    const file = event.target.files[0];
    setUploadFile(file);
  };

  const handleUpload = async () => {
    if (!uploadFile) {
      setError('Please select a file first');
      return;
    }

    setUploading(true);
    setError(null);
    setSuccess(null);

    const formData = new FormData();
    formData.append('file', uploadFile);

    try {
      const response = await axios.post(
        `${API_BASE_URL}/api/images/upload`,
        formData,
        {
          headers: {
            'Content-Type': 'multipart/form-data',
          },
        }
      );

      setSuccess(`Image uploaded successfully: ${response.data.filename}`);
      setUploadFile(null);

      // Reset file input
      const fileInput = document.getElementById('file-input');
      if (fileInput) fileInput.value = '';

      // Refresh image list
      await fetchImages();

      // Auto-select the newly uploaded image
      setSelectedImage(response.data.id);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to upload image');
    } finally {
      setUploading(false);
    }
  };

  const handleQuery = async () => {
    if (!selectedImage) {
      setError('Please select an image first');
      return;
    }

    if (!query.trim()) {
      setError('Please enter a query');
      return;
    }

    setLoading(true);
    setError(null);
    setQueryResult(null);

    try {
      const response = await axios.post(
        `${API_BASE_URL}/api/query`,
        null,
        {
          params: {
            query: query,
            image_id: selectedImage,
          },
        }
      );

      setQueryResult(response.data);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to process query');
    } finally {
      setLoading(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter') {
      handleQuery();
    }
  };

  return (
    <div className="App">
      <header className="header">
        <h1>GIS Satellite Analysis</h1>
        <p>AI-Powered Imagery Analysis with Natural Language Queries</p>
      </header>

      {error && <div className="error">{error}</div>}
      {success && <div className="success">{success}</div>}

      <div className="main-content">
        {/* Upload Section */}
        <div className="card">
          <h2>Upload Image</h2>
          <div
            className="upload-section"
            onClick={() => document.getElementById('file-input').click()}
          >
            <input
              id="file-input"
              type="file"
              accept=".tif,.tiff,.jpg,.jpeg,.png"
              onChange={handleFileSelect}
            />
            <p style={{ marginBottom: '10px' }}>
              {uploadFile ? uploadFile.name : 'Click to select GeoTIFF image'}
            </p>
            <p style={{ fontSize: '0.9em', color: '#666' }}>
              Supported: GeoTIFF, JPEG, PNG with world files
            </p>
          </div>
          <button
            className="upload-button"
            onClick={handleUpload}
            disabled={!uploadFile || uploading}
          >
            {uploading ? 'Uploading...' : 'Upload Image'}
          </button>
        </div>

        {/* Image List */}
        <div className="card">
          <h2>
            Available Images
            {images.length > 0 && <span className="badge">{images.length}</span>}
          </h2>
          <div className="image-list">
            {images.length === 0 ? (
              <p style={{ color: '#666', textAlign: 'center', padding: '20px' }}>
                No images uploaded yet
              </p>
            ) : (
              images.map((img) => (
                <div
                  key={img.id}
                  className={`image-item ${selectedImage === img.id ? 'selected' : ''}`}
                  onClick={() => setSelectedImage(img.id)}
                >
                  <h4>{img.filename}</h4>
                  <p>Resolution: {img.resolution}m | Size: {img.size}</p>
                  <p>Uploaded: {new Date(img.upload_date).toLocaleString()}</p>
                </div>
              ))
            )}
          </div>
        </div>
      </div>

      {/* Query Section */}
      <div className="card query-section">
        <h2>Natural Language Query</h2>
        <div className="query-input-group">
          <input
            type="text"
            className="query-input"
            placeholder='Try: "number of cars" or "how many vehicles"'
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            onKeyPress={handleKeyPress}
            disabled={!selectedImage}
          />
          <button
            className="query-button"
            onClick={handleQuery}
            disabled={!selectedImage || !query.trim() || loading}
          >
            {loading ? 'Analyzing...' : 'Analyze'}
          </button>
        </div>

        {!selectedImage && (
          <p style={{ color: '#666', fontStyle: 'italic' }}>
            Select an image above to start querying
          </p>
        )}

        {loading && (
          <div className="loading">
            <p>Processing your query with AI...</p>
          </div>
        )}

        {queryResult && (
          <div className="results">
            <h3>Analysis Results</h3>
            <div className="response-text">
              {queryResult.response}
            </div>

            <div className="result-details">
              <h4>Details</h4>
              {queryResult.result.count !== undefined && (
                <p>
                  <strong>Count:</strong> {queryResult.result.count} {queryResult.result.object_type}(s)
                </p>
              )}
              {queryResult.result.from_cache && (
                <p style={{ color: '#667eea', fontStyle: 'italic' }}>
                  (Retrieved from cache)
                </p>
              )}
              {queryResult.result.detections && (
                <details style={{ marginTop: '10px' }}>
                  <summary style={{ cursor: 'pointer', color: '#667eea' }}>
                    View detection details ({queryResult.result.detections.length})
                  </summary>
                  <pre>{JSON.stringify(queryResult.result.detections.slice(0, 5), null, 2)}</pre>
                  {queryResult.result.detections.length > 5 && (
                    <p style={{ fontStyle: 'italic', color: '#666' }}>
                      Showing first 5 of {queryResult.result.detections.length} detections
                    </p>
                  )}
                </details>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default App;
