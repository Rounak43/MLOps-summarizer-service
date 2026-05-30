// =============================================================================
// frontend/src/api/axiosInstance.js
// Centralized Reusable Axios Client with Auth Token Interceptors
// =============================================================================

import axios from 'axios';
import { authService } from '../auth/authService';

const axiosInstance = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:5000',
  timeout: 120000, // 2-minute timeout for larger NLP extraction pipelines
});

// Request Interceptor: Inject Auth JWT Token automatically on every request
axiosInstance.interceptors.request.use(
  async (config) => {
    try {
      const token = await authService.getCurrentUserToken();
      if (token) {
        config.headers.Authorization = `Bearer ${token}`;
      }
    } catch (err) {
      console.warn('[Axios] Could not retrieve authorization token:', err);
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response Interceptor: Register global error boundaries and status filters
axiosInstance.interceptors.response.use(
  (response) => response,
  (error) => {
    const errorMsg = error.response?.data?.error || error.message || 'Server connection failed';
    console.error('[Axios] Global API Error Intercept:', errorMsg);
    
    // Customize handling of specific status codes if required (e.g. 401 redirect)
    if (error.response?.status === 401) {
      console.warn('[Axios] Request returned 401 Unauthorized. Access token might be invalid.');
    }
    
    return Promise.reject(error);
  }
);

export default axiosInstance;
