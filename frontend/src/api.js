// API base configuration
const API_BASE_URL = 'http://localhost:8000';

// Get auth token from localStorage
export const getToken = () => {
  return localStorage.getItem('token');
};

// Get user data from localStorage
export const getUser = () => {
  const user = localStorage.getItem('user');
  return user ? JSON.parse(user) : null;
};

// Save auth data to localStorage
export const saveAuth = (token, user) => {
  localStorage.setItem('token', token);
  localStorage.setItem('user', JSON.stringify(user));
};

// Clear auth data from localStorage
export const clearAuth = () => {
  localStorage.removeItem('token');
  localStorage.removeItem('user');
};

// Check if user is authenticated
export const isAuthenticated = () => {
  return !!getToken();
};

// API call wrapper with error handling
const apiCall = async (endpoint, options = {}) => {
  const token = getToken();
  
  const config = {
    headers: {
      'Content-Type': 'application/json',
      ...(token && { Authorization: `Bearer ${token}` }),
      ...options.headers,
    },
    ...options,
  };

  try {
    const response = await fetch(`${API_BASE_URL}${endpoint}`, config);
    const data = await response.json();

    if (!response.ok) {
      throw new Error(data.detail || 'Something went wrong');
    }

    return data;
  } catch (error) {
    throw error;
  }
};

// Auth API calls
export const login = async (email, password) => {
  const data = await apiCall('/api/auth/login', {
    method: 'POST',
    body: JSON.stringify({ email, password }),
  });

  return data;
};

export const register = async (email, password, role = 'USER') => {
  return apiCall('/api/auth/register', {
    method: 'POST',
    body: JSON.stringify({ email, password, role }),
  });
};

// Sweet API calls
export const getSweets = async () => {
  return apiCall('/api/sweets');
};

export const searchSweets = async (params) => {
  const queryString = new URLSearchParams();
  
  if (params.name) queryString.append('name', params.name);
  if (params.category) queryString.append('category', params.category);
  if (params.min_price) queryString.append('min_price', params.min_price);
  if (params.max_price) queryString.append('max_price', params.max_price);
  
  const url = `/api/sweets/search${queryString.toString() ? '?' + queryString.toString() : ''}`;
  return apiCall(url);
};

export const createSweet = async (sweetData) => {
  return apiCall('/api/sweets', {
    method: 'POST',
    body: JSON.stringify(sweetData),
  });
};

export const updateSweet = async (id, sweetData) => {
  return apiCall(`/api/sweets/${id}`, {
    method: 'PUT',
    body: JSON.stringify(sweetData),
  });
};

export const deleteSweet = async (id) => {
  return apiCall(`/api/sweets/${id}`, {
    method: 'DELETE',
  });
};

export const purchaseSweet = async (id, quantity) => {
  return apiCall(`/api/sweets/${id}/purchase`, {
    method: 'POST',
    body: JSON.stringify({ quantity }),
  });
};

export const restockSweet = async (id, quantity) => {
  return apiCall(`/api/sweets/${id}/restock`, {
    method: 'POST',
    body: JSON.stringify({ quantity }),
  });
};
