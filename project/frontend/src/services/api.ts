
import axios from 'axios'

const API_BASE_URL = '/api'

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Model Registry API
export const modelRegistryAPI = {
  registerModel: (data: any) => api.post('/models/register', data),
  getModels: () => api.get('/models'),
  getModel: (id: string) => api.get(`/models/${id}`),
  verifyModel: (id: string) => api.post(`/models/${id}/verify`),
}

// Routing API
export const routingAPI = {
  routeQuery: (query: string, capability?: string) => 
    api.post('/route', null, { params: { query, capability } }),
  getStats: (hours: number = 24) => api.get('/routing/stats', { params: { hours } }),
  commitBatch: (period: string) => api.post('/routing/commit-batch', null, { params: { period } }),
}

// Performance API
export const performanceAPI = {
  reportPerformance: (data: any) => api.post('/performance/report', data),
  getModelPerformance: (modelId: string, limit: number = 100) => 
    api.get(`/performance/${modelId}`, { params: { limit } }),
}

// Violation API
export const violationAPI = {
  reportViolation: (data: any) => api.post('/violations/report', data),
  getModelViolations: (modelId: string, limit: number = 100) => 
    api.get(`/violations/${modelId}`, { params: { limit } }),
}

// Trust Score API
export const trustScoreAPI = {
  getAllScores: () => api.get('/trust-scores'),
  getModelScore: (modelId: string) => api.get(`/trust-scores/${modelId}`),
}

// Dashboard API
export const dashboardAPI = {
  getOverview: () => api.get('/dashboard/overview'),
}

export default api
