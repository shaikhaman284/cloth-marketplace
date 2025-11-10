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
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor - handle errors
api.interceptors.response.use(
  (response) => response.data,
  (error) => {
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
  getCategories: () => api.get('/categories'),

  // Products
  getProducts: (params) => api.get('/products', { params }),
  getProduct: (id) => api.get(`/products/${id}`),
  getProductReviews: (id, params) => api.get(`/products/${id}/reviews`, { params }),

  // Shops
  getShops: () => api.get('/shops/approved'),
  getShop: (id) => api.get(`/shops/${id}`),

  // Orders
  createOrder: (data) => api.post('/orders/create', data),
  getMyOrders: (params) => api.get('/orders/my-orders', { params }),
  getOrder: (orderNumber) => api.get(`/orders/${orderNumber}`),
  cancelOrder: (orderNumber, reason) => api.post(`/orders/${orderNumber}/cancel`, { reason }),

  // Reviews
  createReview: (data) => api.post('/reviews/create', data),

  // Auth
  register: (data) => api.post('/auth/register', data),
  verifyToken: (token) => api.post('/auth/verify-token', { firebase_id_token: token }),
};

export default api;