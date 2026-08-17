const API_BASE_URL = "http://127.0.0.1:8000/api";

// Helper to get JWT token from localStorage
export const getAuthToken = () => localStorage.getItem("aksharai_token");

// Helper to save JWT token
export const setAuthToken = (token) => localStorage.setItem("aksharai_token", token);

// Helper to remove JWT token on logout
export const removeAuthToken = () => localStorage.getItem("aksharai_token") && localStorage.removeItem("aksharai_token");

// Centralized API fetch wrapper with timeout & JWT header
export async function apiRequest(endpoint, options = {}) {
  const token = getAuthToken();
  const headers = {
    ...options.headers,
  };

  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }

  if (!options.isFormData && !headers["Content-Type"]) {
    headers["Content-Type"] = "application/json";
  }

  // 8-second timeout controller so requests never hang infinitely
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), 8000);

  try {
    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
      ...options,
      headers,
      signal: controller.signal
    });

    clearTimeout(timeoutId);

    if (response.status === 401) {
      removeAuthToken();
    }

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.detail || `Request failed with status ${response.status}`);
    }

    return await response.json();
  } catch (err) {
    clearTimeout(timeoutId);
    console.error(`[API FETCH ERROR] ${endpoint}:`, err);
    throw err;
  }
}

// Learning Path API
export const learningPathApi = {
  getActivePath: async (lang = 'en') => {
    return apiRequest(`/learning-path/active?lang=${lang}`);
  },
  generatePath: async (proficiencyLevel, lang = 'en') => {
    return apiRequest('/learning-path/generate', {
      method: 'POST',
      body: JSON.stringify({ proficiency_level: proficiencyLevel, lang })
    });
  },
  updateLessonStatus: async (pathLessonId, status) => {
    return apiRequest(`/learning-path/lesson/${pathLessonId}/status`, {
      method: 'PATCH',
      body: JSON.stringify({ status })
    });
  }
};

// AI Recommendation API
export const recommendationApi = {
  getRecommendations: async () => {
    return apiRequest('/recommendations');
  },
  generateExercise: async (skillType, difficultyLevel) => {
    return apiRequest('/recommendations/generate-exercise', {
      method: 'POST',
      body: JSON.stringify({ skill_type: skillType, difficulty_level: difficultyLevel })
    });
  },
  getAIStatus: async () => {
    return apiRequest('/recommendations/ai-status');
  },
  getHistory: async () => {
    return apiRequest('/recommendations/history');
  }
};
