/* ── API Configuration ── */

// API Configuration
const API_CONFIG = {
  // Local development (using test_local.py)
  LOCAL: {
    enabled: true,
    baseUrl: 'http://localhost:5000'
  },
  
  // AWS Lambda API Gateway (after deployment)
  AWS: {
    enabled: false,
    baseUrl: '', // Set this after running: terraform output api_endpoint
    stage: 'dev'
  }
};

// Get active API endpoint
function getApiEndpoint() {
  if (API_CONFIG.AWS.enabled && API_CONFIG.AWS.baseUrl) {
    return `${API_CONFIG.AWS.baseUrl}/${API_CONFIG.AWS.stage}`;
  }
  return API_CONFIG.LOCAL.baseUrl;
}

// API endpoints
const API_ENDPOINTS = {
  uploadPDF: () => `${getApiEndpoint()}/upload`,
  search: () => `${getApiEndpoint()}/search`,
  getCandidates: () => `${getApiEndpoint()}/candidates`
};

// Export for use in app.js
window.API_CONFIG = API_CONFIG;
window.API_ENDPOINTS = API_ENDPOINTS;
window.getApiEndpoint = getApiEndpoint;
