const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export const apiClient = {
  async get(endpoint, options = {}) {
    return this.request(endpoint, { ...options, method: 'GET' });
  },

  async post(endpoint, data, options = {}) {
    return this.request(endpoint, {
      ...options,
      method: 'POST',
      body: data instanceof FormData ? data : JSON.stringify(data),
      headers: data instanceof FormData ? {} : { 'Content-Type': 'application/json' },
    });
  },

  async put(endpoint, data, options = {}) {
    return this.request(endpoint, {
      ...options,
      method: 'PUT',
      body: data instanceof FormData ? data : JSON.stringify(data),
      headers: data instanceof FormData ? {} : { 'Content-Type': 'application/json' },
    });
  },

  async delete(endpoint, options = {}) {
    return this.request(endpoint, { ...options, method: 'DELETE' });
  },

  async request(endpoint, options = {}) {
    const url = `${API_BASE_URL}${endpoint}`;
    
    // Ajouter le token d'authentification si disponible
    const sessionToken = localStorage.getItem('session_token');
    if (sessionToken) {
      options.headers = {
        ...options.headers,
        'X-Session-Token': sessionToken,
      };
    }

    // Timeout adaptatif : 30 secondes pour les analyses d'image, 10 secondes pour le reste
    const isImageAnalysis = endpoint.includes('/analyze/');
    const timeoutDuration = isImageAnalysis ? 30000 : 10000;
    
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), timeoutDuration);
    options.signal = controller.signal;

    try {
      const response = await fetch(url, options);
      clearTimeout(timeoutId);

      // Gérer l'expiration de session
      if (response.status === 401) {
        localStorage.clear();
        window.location.href = '/auth';
        throw new Error('Session expirée');
      }

      if (!response.ok) {
        const data = await response.json().catch(() => ({}));
        throw {
          status: response.status,
          message: data.detail || data.message || `HTTP error! status: ${response.status}`,
          data
        };
      }

      return await response.json();
    } catch (error) {
      clearTimeout(timeoutId);
      if (error.name === 'AbortError') {
        console.error('Request timeout:', endpoint);
        throw new Error('La requête a expiré. Veuillez réessayer.');
      }
      console.error('API request failed:', error);
      throw error;
    }
  },
};

export { API_BASE_URL };