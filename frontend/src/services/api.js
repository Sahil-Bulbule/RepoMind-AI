   
                           
                                     
   

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000';

async function handleResponse(response) {
  if (!response.ok) {
    let errorDetail = `Request failed with status ${response.status}`;
    try {
      const data = await response.json();
      if (data && data.detail) {
        errorDetail = typeof data.detail === 'string' ? data.detail : JSON.stringify(data.detail);
      }
    } catch {
                                 
    }
    throw new Error(errorDetail);
  }
  return response.json();
}

export const api = {
                  
  async getHealth() {
    const res = await fetch(`${API_BASE}/health`);
    return handleResponse(res);
  },

                             
  async analyzeUser(username, forceRefresh = false) {
    const res = await fetch(`${API_BASE}/api/github/analyze`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username, force_refresh: forceRefresh }),
    });
    return handleResponse(res);
  },

                               
  async refreshUser(username) {
    const res = await fetch(`${API_BASE}/api/github/refresh/${encodeURIComponent(username)}`, {
      method: 'POST',
    });
    return handleResponse(res);
  },

                             
  async getStatus(username) {
    const res = await fetch(`${API_BASE}/api/github/status/${encodeURIComponent(username)}`);
    return handleResponse(res);
  },

                        
  async getProfile(username) {
    const res = await fetch(`${API_BASE}/api/github/profile/${encodeURIComponent(username)}`);
    return handleResponse(res);
  },

                          
  async getRepositories(username) {
    const res = await fetch(`${API_BASE}/api/github/repositories/${encodeURIComponent(username)}`);
    return handleResponse(res);
  },

                                                
  async getRepositoryDetail(username, repoName) {
    const res = await fetch(
      `${API_BASE}/api/github/repository/${encodeURIComponent(username)}/${encodeURIComponent(repoName)}`
    );
    return handleResponse(res);
  },

                      
  async sendChatMessage(githubUsername, message, conversationHistory = [], repository = null) {
    const res = await fetch(`${API_BASE}/api/chat`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        github_username: githubUsername,
        message,
        conversation_history: conversationHistory,
        repository_filter: repository?.name || null,
        repository_id: repository?.id ?? null,
        repository_name: repository?.name || null,
        repository_full_name: repository?.full_name || null,
        repository_url: repository?.html_url || null,
      }),
    });
    return handleResponse(res);
  },

  async getRepositorySuggestions(username, repositoryId) {
    const res = await fetch(
      `${API_BASE}/api/github/repository/${encodeURIComponent(username)}/id/${encodeURIComponent(repositoryId)}/suggestions`
    );
    return handleResponse(res);
  },

                    
  async search(githubUsername, query, repositoryFilter = null, limit = 10) {
    const res = await fetch(`${API_BASE}/api/search`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        github_username: githubUsername,
        query,
        repository_filter: repositoryFilter,
        limit,
      }),
    });
    return handleResponse(res);
  },
};
