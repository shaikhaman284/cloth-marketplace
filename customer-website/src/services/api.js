import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'https://api.awm27.shop';

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  }
});

// Request interceptor - add auth token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('authToken');
    if (token) {
      config.headers.Authorization = `Token ${token}`;
    }
    console.log('API Request:', config.method.toUpperCase(), config.url, config.params);
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor - handle errors
api.interceptors.response.use(
  (response) => {
    console.log('API Response:', response.config.url, response.data);
    return response.data;
  },
  (error) => {
    console.error('API Error:', error.response?.status, error.response?.data);
    if (error.response?.status === 401) {
      localStorage.removeItem('authToken');
      localStorage.removeItem('user');
      window.location.href = '/login';
    }
    return Promise.reject(error.response?.data || error.message);
  }
);

// API Methods
export const apiService = {
  // Categories
  getCategories: () => api.get('/api/categories'),

  // Products
  getProducts: (params = {}) => {
    console.log('getProducts called with params:', params);
    return api.get('/api/products', { params });
  },
  getProduct: (id) => api.get(`/api/products/${id}`),
  getProductReviews: (id, params) => api.get(`/api/products/${id}/reviews`, { params }),

  // Shops
  getShops: () => api.get('/api/shops/approved'),
  getShop: (id) => api.get(`/api/shops/${id}`),

  // Orders
  createOrder: (data) => api.post('/api/orders/create', data),
  getMyOrders: (params) => api.get('/api/orders/my-orders', { params }),
  getOrder: (orderNumber) => api.get(`/api/orders/${orderNumber}`),
  cancelOrder: (orderNumber, reason) => api.post(`/api/orders/${orderNumber}/cancel`, { reason }),

  // Reviews
  createReview: (data) => api.post('/api/reviews/create', data),

  // Auth
  register: (data) => api.post('/api/auth/register', data),
  verifyToken: (token) => api.post('/api/auth/verify-token', { firebase_id_token: token }),
};

export default api;