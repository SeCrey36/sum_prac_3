const API_BASE = '/api';

export const getTokens = () => {
  return {
    access: localStorage.getItem('access_token'),
    refresh: localStorage.getItem('refresh_token'),
  };
};

export const setTokens = (access, refresh) => {
  if (access) localStorage.setItem('access_token', access);
  if (refresh) localStorage.setItem('refresh_token', refresh);
};

export const clearTokens = () => {
  localStorage.removeItem('access_token');
  localStorage.removeItem('refresh_token');
  localStorage.removeItem('current_user');
};

export async function apiRequest(endpoint, options = {}) {
  const { access, refresh } = getTokens();
  const headers = { ...(options.headers || {}) };

  if (access && !headers['Authorization']) {
    headers['Authorization'] = `Bearer ${access}`;
  }

  // Don't set Content-Type for FormData (browser sets boundary automatically)
  if (!(options.body instanceof FormData) && !headers['Content-Type']) {
    headers['Content-Type'] = 'application/json';
  }

  let response = await fetch(`${API_BASE}${endpoint}`, {
    ...options,
    headers,
  });

  // If token expired (401), try refresh
  if (response.status === 401 && refresh) {
    try {
      const refreshRes = await fetch(`${API_BASE}/auth/refresh/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ refresh }),
      });
      if (refreshRes.ok) {
        const refreshData = await refreshRes.json();
        setTokens(refreshData.access, refreshData.refresh || refresh);
        // Retry original request with new token
        headers['Authorization'] = `Bearer ${refreshData.access}`;
        response = await fetch(`${API_BASE}${endpoint}`, {
          ...options,
          headers,
        });
      } else {
        clearTokens();
        window.dispatchEvent(new Event('auth:unauthorized'));
      }
    } catch (e) {
      clearTokens();
      window.dispatchEvent(new Event('auth:unauthorized'));
    }
  }

  return response;
}
