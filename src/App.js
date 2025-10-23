import React, { useState, useEffect, useCallback } from 'react';
import axios from 'axios';
import './App.css';

function App() {
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [patientSearch, setPatientSearch] = useState('');
  const [patientProviderSearch, setPatientProviderSearch] = useState('');
  const [providerSearch, setProviderSearch] = useState('');
  const [password, setPassword] = useState('');

  // Hardcoded configuration
  const lambdaUrl = 'https://44rc4pnqte.execute-api.us-east-1.amazonaws.com/';

  // Load search terms from localStorage on component mount
  useEffect(() => {
    const savedPatientSearch = localStorage.getItem('patientSearch');
    const savedPatientProviderSearch = localStorage.getItem('patientProviderSearch');
    const savedProviderSearch = localStorage.getItem('providerSearch');
    if (savedPatientSearch) setPatientSearch(savedPatientSearch);
    if (savedPatientProviderSearch) setPatientProviderSearch(savedPatientProviderSearch);
    if (savedProviderSearch) setProviderSearch(savedProviderSearch);
  }, []);

  // Save search terms to localStorage when they change
  useEffect(() => {
    if (patientSearch) localStorage.setItem('patientSearch', patientSearch);
  }, [patientSearch]);

  useEffect(() => {
    if (patientProviderSearch) localStorage.setItem('patientProviderSearch', patientProviderSearch);
  }, [patientProviderSearch]);

  useEffect(() => {
    if (providerSearch) localStorage.setItem('providerSearch', providerSearch);
  }, [providerSearch]);


  const fetchData = useCallback(async (searchType, searchValue) => {
    setLoading(true);
    setError(null);

    try {
      // Support both GET and POST requests for different Lambda implementations
      const requestConfig = {
        headers: {
          'Content-Type': 'application/json',
        },
        timeout: 30000 // 30 second timeout
      };

      let response;
      
      // Prepare request payload based on search type
      let requestPayload = {};
      
      if (searchType === 'patient') {
        requestPayload = {
          searchType: 'patient',
          patientName: searchValue.trim()
        };
      } else if (searchType === 'patientProvider') {
        requestPayload = {
          searchType: 'patientProvider',
          patientId: searchValue.trim()
        };
      } else if (searchType === 'provider') {
        requestPayload = {
          searchType: 'provider',
          providerName: searchValue.trim()
        };
      } else {
        setData([]);
        setLoading(false);
        return;
      }

      // Try POST first (most common for Lambda functions)
      try {
        response = await axios.post(lambdaUrl, requestPayload, requestConfig);
      } catch (postError) {
        // If POST fails, try GET with query parameters
        console.log('POST failed, trying GET with query parameters...');
        response = await axios.get(lambdaUrl, {
          ...requestConfig,
          params: requestPayload
        });
      }

      // Handle different response formats from Python Lambda functions
      let responseData = response.data;
      
      // Handle Python Lambda response formats
      if (responseData && typeof responseData === 'object') {
        if (Array.isArray(responseData)) {
          // Direct array response
          setData(responseData);
        } else if (responseData.body) {
          // Lambda proxy integration response
          try {
            const bodyData = typeof responseData.body === 'string' 
              ? JSON.parse(responseData.body) 
              : responseData.body;
            
            if (Array.isArray(bodyData)) {
              setData(bodyData);
            } else if (bodyData.data && Array.isArray(bodyData.data)) {
              setData(bodyData.data);
            } else {
              setError('Invalid response format from Lambda function');
            }
          } catch (parseError) {
            setError('Failed to parse Lambda response body');
          }
        } else if (responseData.data && Array.isArray(responseData.data)) {
          // Standard API response with data field
          setData(responseData.data);
        } else if (responseData.records && Array.isArray(responseData.records)) {
          // Alternative format with records field
          setData(responseData.records);
        } else {
          setError('Invalid response format from Lambda function');
        }
      } else {
        setError('Invalid response format from Lambda function');
      }
    } catch (err) {
      console.error('Error fetching data:', err);
      if (err.code === 'ECONNABORTED') {
        setError('Request timeout - Lambda function may be taking too long to respond');
      } else if (err.response) {
        const errorMessage = err.response.data?.message || 
                           err.response.data?.error || 
                           err.response.statusText;
        setError(`Server error: ${err.response.status} - ${errorMessage}`);
      } else if (err.request) {
        setError('Network error - Unable to reach Lambda function. Check the URL and your internet connection.');
      } else {
        setError(`Error: ${err.message}`);
      }
    } finally {
      setLoading(false);
    }
  }, []);

  // Separate search functions for each type
  const searchPatient = useCallback(() => {
    if (password !== 'shibboleth') {
      setError('Invalid password');
      return;
    }
    if (patientSearch.trim()) {
      fetchData('patient', patientSearch);
    }
  }, [patientSearch, password, fetchData]);

  const searchPatientProvider = useCallback(() => {
    if (password !== 'shibboleth') {
      setError('Invalid password');
      return;
    }
    if (patientProviderSearch.trim()) {
      // Clear patient search when running this search
      if (patientSearch) setPatientSearch('');
      fetchData('patientProvider', patientProviderSearch);
    }
  }, [patientProviderSearch, patientSearch, password, fetchData]);

  const searchProvider = useCallback(() => {
    if (password !== 'shibboleth') {
      setError('Invalid password');
      return;
    }
    if (providerSearch.trim()) {
      // Clear patient search when running this search
      if (patientSearch) setPatientSearch('');
      fetchData('provider', providerSearch);
    }
  }, [providerSearch, patientSearch, password, fetchData]);


  const renderPatientTable = () => {
    if (data.length === 0) {
      return <div className="no-data">No patient records found</div>;
    }

    // Sort by date of birth (ascending - oldest first)
    const sortedData = [...data].sort((a, b) => {
      const dobA = a.dob || '';
      const dobB = b.dob || '';
      return dobA.localeCompare(dobB);
    });

    return (
      <div className="table-container">
        <table className="table">
          <thead>
            <tr>
              <th>Name</th>
              <th>User ID</th>
              <th>Date of Birth</th>
            </tr>
          </thead>
          <tbody>
            {sortedData.map((row, rowIndex) => (
              <tr key={rowIndex}>
                <td>{row.name || 'N/A'}</td>
                <td>{row.id || 'N/A'}</td>
                <td>{row.dob || 'N/A'}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    );
  };

  const renderPatientProviderTable = () => {
    if (data.length === 0) {
      return <div className="no-data">No provider records found for this patient</div>;
    }

    // Sort by provider name (alphabetical)
    const sortedData = [...data].sort((a, b) => {
      const nameA = a.provider_name || '';
      const nameB = b.provider_name || '';
      return nameA.localeCompare(nameB);
    });

    return (
      <div className="table-container">
        <table className="table">
          <thead>
            <tr>
              <th>Provider Name</th>
              <th>Fax Number</th>
              <th>Address</th>
              <th>State</th>
              <th>Latest Consultation</th>
              <th>Latest Fill</th>
            </tr>
          </thead>
          <tbody>
            {sortedData.map((row, rowIndex) => (
              <tr key={rowIndex}>
                <td>{row.provider_name || 'N/A'}</td>
                <td>{row.fax_number || 'N/A'}</td>
                <td>{row.address || 'N/A'}</td>
                <td>{row.state || 'N/A'}</td>
                <td>{row.latest_consultation_date || 'N/A'}</td>
                <td>{row.latest_fill_date || 'N/A'}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    );
  };

  const renderProviderTable = () => {
    if (data.length === 0) {
      return <div className="no-data">No provider records found</div>;
    }

    // Sort by state (alphabetical)
    const sortedData = [...data].sort((a, b) => {
      const stateA = a.state || '';
      const stateB = b.state || '';
      return stateA.localeCompare(stateB);
    });

    return (
      <div className="table-container">
        <table className="table">
          <thead>
            <tr>
              <th>Provider Name</th>
              <th>Fax Number</th>
              <th>Address</th>
              <th>State</th>
            </tr>
          </thead>
          <tbody>
            {sortedData.map((row, rowIndex) => (
              <tr key={rowIndex}>
                <td>{row.provider_name || 'N/A'}</td>
                <td>{row.fax_number || 'N/A'}</td>
                <td>{row.address || 'N/A'}</td>
                <td>{row.state || 'N/A'}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    );
  };

  return (
    <div className="container">
        <div className="card" style={{ marginBottom: '12px' }}>
          <div className="search-section">
            <div className="form-row">
              <div className="form-group">
                <label htmlFor="password">Password:</label>
                <input
                  id="password"
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="Enter password"
                />
              </div>
            </div>
          </div>
        </div>

        <div className="card">
          <div className="search-section">
            <div className="form-row">
              <div className="form-group">
                <label htmlFor="patientSearch">Search Patient:</label>
                <input
                  id="patientSearch"
                  type="text"
                  value={patientSearch}
                  onChange={(e) => setPatientSearch(e.target.value)}
                  placeholder="Enter patient name..."
                />
                <button 
                  className="button search-button" 
                  onClick={searchPatient} 
                  disabled={loading || !patientSearch.trim()}
                  title="Search Patient"
                >
                  Search
                </button>
              </div>
              <div className="form-group">
                <label htmlFor="patientProviderSearch">Search Patient Providers:</label>
                <input
                  id="patientProviderSearch"
                  type="text"
                  value={patientProviderSearch}
                  onChange={(e) => setPatientProviderSearch(e.target.value)}
                  placeholder="Enter patient ID..."
                />
                <button 
                  className="button search-button" 
                  onClick={searchPatientProvider} 
                  disabled={loading || !patientProviderSearch.trim()}
                  title="Search Patient Providers"
                >
                  Search
                </button>
              </div>
              <div className="form-group">
                <label htmlFor="providerSearch">Search Provider:</label>
                <input
                  id="providerSearch"
                  type="text"
                  value={providerSearch}
                  onChange={(e) => setProviderSearch(e.target.value)}
                  placeholder="Enter provider name..."
                />
                <button 
                  className="button search-button" 
                  onClick={searchProvider} 
                  disabled={loading || !providerSearch.trim()}
                  title="Search Provider"
                >
                  Search
                </button>
              </div>
              <button 
                className="button clear-button" 
                onClick={() => {
                  setPatientSearch('');
                  setPatientProviderSearch('');
                  setProviderSearch('');
                  setData([]);
                }}
                title="Clear All"
              >
                ✕
              </button>
            </div>
          </div>

        {error && (
          <div className="error">
            {error}
          </div>
        )}

        {loading && (
          <div className="loading">
            <p>Fetching data from Lambda function...</p>
          </div>
        )}

        {!loading && !error && data.length > 0 && (
          <div>
            {patientSearch.trim() ? (
              <>
                <h3>Patient Search Results ({data.length} records found)</h3>
                {renderPatientTable()}
              </>
            ) : patientProviderSearch.trim() ? (
              <>
                <h3>Patient Provider Search Results ({data.length} records found)</h3>
                {renderPatientProviderTable()}
              </>
            ) : providerSearch.trim() ? (
              <>
                <h3>Provider Search Results ({data.length} records found)</h3>
                {renderProviderTable()}
              </>
            ) : null}
          </div>
        )}
      </div>
    </div>
  );
}

export default App;
