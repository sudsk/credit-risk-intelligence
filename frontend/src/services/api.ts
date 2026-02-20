import axios from 'axios';
import { API_BASE_URL, AGENTS_BASE_URL } from '@/utils/constants';
import type {
  PortfolioMetrics,
  SME,
  NewsItem,
  Task,
  Scenario,
  Activity,
  ChatMessage,
  Alert,
} from './types';

const api = axios.create({ baseURL: API_BASE_URL })           // port 8000
const agentsApi = axios.create({ baseURL: AGENTS_BASE_URL })  // port 8081

// Interceptors for error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error('API Error:', error);
    return Promise.reject(error);
  }
);

// Portfolio API
export const portfolioAPI = {
  getMetrics: async (): Promise<PortfolioMetrics> => {
    const { data } = await api.get('/api/v1/portfolio/summary');
    return {
      totalSMEs: data.total_smes,
      totalExposure: `€${(data.total_exposure / 1000000).toFixed(1)}M`,
      avgRiskScore: data.avg_risk_score,
      criticalCount: data.risk_distribution.counts.critical,
      mediumCount: data.risk_distribution.counts.medium,
      stableCount: data.risk_distribution.counts.stable,
      defaultProbability: 2.8,
      portfolioTrend: 'stable' as const,
    };
  },

  getSMEs: async (): Promise<SME[]> => {
    const { data } = await api.get('/api/v1/portfolio/smes?limit=100');
    return data.smes.map((sme: any) => ({
      id: sme.id,
      name: sme.name,
      riskScore: sme.risk_score,
      riskCategory: sme.risk_category,
      exposure: `€${(sme.exposure / 1000).toFixed(0)}K`,
      sector: sme.sector,
      geography: sme.geography,
      trend: sme.trend,
      trendValue: sme.trend_value,
    }));
  },

  getSMEById: async (id: string): Promise<any> => {
    const { data } = await api.get(`/api/v1/portfolio/smes/${id}`);
    return data;
  },

  getBreakdownData: async (riskLevel: string) => {
    const { data } = await api.get(`/api/v1/portfolio/breakdown/${riskLevel}`);
    return data;
  },
};

// News & Events API
export const newsAPI = {
  getNewsIntelligence: async (): Promise<NewsItem[]> => {
    const { data } = await api.get('/api/v1/news/intelligence');
    return data.items;
  },

  getPredictedEvents: async () => {
    const { data } = await api.get('/api/v1/news/predicted-events');
    return data.events;
  },
};

// Tasks API
export const tasksAPI = {
  getTasks: async (): Promise<Task[]> => {
    const { data } = await api.get('/api/v1/tasks');
    return data.tasks;
  },

  createTask: async (task: Partial<Task>) => {
    const { data } = await api.post('/api/v1/tasks', task);
    return data;
  },

  updateTask: async (id: string, updates: Partial<Task>) => {
    const { data } = await api.put(`/api/v1/tasks/${id}`, updates);
    return data;
  },
};

// Activities API
export const activitiesAPI = {
  getActivities: async (): Promise<Activity[]> => {
    const { data } = await api.get('/api/v1/activities');
    return data.activities;
  },
};

// Scenarios API
export const scenariosAPI = {
  getScenarios: async (): Promise<Scenario[]> => {
    return [];
  },

  createScenario: async (description: string) => {
    const { data } = await agentsApi.post('/api/v1/scenarios', { description });
    return {
      id: `scenario_${Date.now()}`,
      name: description,
      status: 'completed',
      progress: 100,
      createdAt: new Date().toISOString(),
      completedAt: new Date().toISOString(),
      duration: data.duration || 15,
      results: {
        portfolioImpact: data.portfolio_impact,
        topImpacted: data.top_impacted || [],
        sectorImpact: data.sector_impact || [],
      },
      recommendations: data.recommendations || null,
    };
  },

  getScenarioById: async (_id: string): Promise<Scenario> => {
    throw new Error('Not implemented');
  },

  deleteScenario: async (_id: string): Promise<void> => {
    // Not implemented in backend
  },
};

// Chat API
export const chatAPI = {
  sendMessage: async (message: string, sessionId: string = 'default') => {
    const { data } = await agentsApi.post('/api/v1/chat', { message, session_id: sessionId });
    return {
      id: `msg_${Date.now()}`,
      role: 'assistant' as const,
      content: data.response,
      timestamp: new Date().toISOString(),
    };
  },

  getHistory: async (): Promise<ChatMessage[]> => {
    return [];
  },
};

// Alert API
export const alertAPI = {
  simulateFeed: async (): Promise<Alert> => {
    const { data } = await api.post('/api/v1/alerts/simulate');
    return {
      id: data.alert_id,
      timestamp: data.timestamp,
      severity: data.severity,
      smeId: data.sme_id,
      smeName: data.sme_name,
      exposure: `€${(data.exposure / 1000).toFixed(0)}K`,
      eventType: data.event_type,
      eventSummary: data.summary,
      dataSources: data.data_sources,
      dismissed: false,
    };
  },

  getAlertHistory: async (): Promise<Alert[]> => {
    const { data } = await api.get('/api/v1/alerts/history');
    return data.alerts.map((alert: any) => ({
      id: alert.alert_id,
      timestamp: alert.timestamp,
      severity: alert.severity,
      smeId: alert.sme_id,
      smeName: alert.sme_name,
      exposure: `€${(alert.exposure / 1000).toFixed(0)}K`,
      eventType: alert.event_type,
      eventSummary: alert.summary,
      dataSources: alert.data_sources,
      dismissed: alert.dismissed || false,
    }));
  },
};

export default api;