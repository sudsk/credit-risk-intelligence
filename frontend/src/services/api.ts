import axios from 'axios';
import { API_BASE_URL } from '@/utils/constants';
import type {
  PortfolioMetrics,
  SME,
  PredictedEvent,
  NewsItem,
  Task,
  Scenario,
  Activity,
  ChatMessage,
} from './types';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

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
      defaultProbability: 2.8, // Calculate from data if available
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

  getBreakdownData: async (riskLevel: string): Promise<any> => {
    // This endpoint doesn't exist in backend yet, use mock data
    const { data } = await api.get('/api/v1/portfolio/summary');
    return data;
  },
};

// News & Events API
export const newsAPI = {
  getPredictedEvents: async (): Promise<PredictedEvent[]> => {
    // Backend doesn't have this endpoint yet - return empty or mock
    return [];
  },

  getNewsIntelligence: async (): Promise<NewsItem[]> => {
    // Backend doesn't have this endpoint yet - return empty or mock
    return [];
  },
};

// Tasks API
export const tasksAPI = {
  getTasks: async (): Promise<Task[]> => {
    // Backend doesn't have this endpoint yet
    return [];
  },

  createTask: async (task: Partial<Task>): Promise<Task> => {
    // Mock implementation - store in localStorage or Redux only
    return {
      id: `task_${Date.now()}`,
      ...task,
      createdAt: new Date().toISOString(),
    } as Task;
  },

  updateTask: async (id: string, updates: Partial<Task>): Promise<Task> => {
    throw new Error('Not implemented');
  },

  deleteTask: async (id: string): Promise<void> => {
    // Not implemented
  },

  completeTask: async (id: string): Promise<Task> => {
    throw new Error('Not implemented');
  },
};


// Scenarios API
export const scenariosAPI = {
  getScenarios: async (): Promise<Scenario[]> => {
    // Backend doesn't have list endpoint yet, return empty
    return [];
  },

  createScenario: async (description: string): Promise<Scenario> => {
    // Parse description to determine scenario type
    let scenario_type = 'recession';
    let parameters: any = { severity: 'moderate', duration_months: 12 };

    if (description.toLowerCase().includes('interest')) {
      scenario_type = 'interest_rate';
      parameters = { rate_increase_bps: 200 };
    } else if (description.toLowerCase().includes('sector')) {
      scenario_type = 'sector_shock';
      parameters = { sector: 'Retail/Fashion', revenue_impact_pct: -20 };
    } else if (description.toLowerCase().includes('regulation')) {
      scenario_type = 'regulation';
      parameters = {
        regulation: 'New Regulation',
        affected_sectors: ['Retail/Fashion'],
        revenue_at_risk_pct: 30
      };
    }

    const { data } = await api.post('/api/v1/scenarios/run', {
      scenario_type,
      parameters,
    });

    return {
      id: `scenario_${Date.now()}`,
      name: description,
      status: 'completed',
      progress: 100,
      createdAt: new Date().toISOString(),
      completedAt: new Date().toISOString(),
      duration: 15,
      results: {
        portfolioImpact: {
          criticalBefore: data.impact?.smes_materially_affected || 23,
          criticalAfter: data.impact?.new_critical_count || 25,
          defaultProbBefore: 2.8,
          defaultProbAfter: 3.1,
          avgScoreBefore: 64,
          avgScoreAfter: 66,
        },
        sectorImpact: [],
        topImpacted: data.top_impacted_smes?.slice(0, 5).map((sme: any) => ({
          smeId: sme.id,
          smeName: sme.name,
          scoreBefore: sme.current_risk,
          scoreAfter: sme.new_risk,
          change: sme.risk_increase,
          reason: 'Impact from scenario',
        })) || [],
      },
      // ADD THIS: recommendations from backend or generate mock
      recommendations: data.recommendations || {
        ultraConservative: {
          reserveIncrease: '€25M',
          sectorAdjustments: [
            'Reduce automotive sector exposure by 20%',
            'Exit high-risk SMEs in affected sectors',
            'Increase monitoring frequency to daily'
          ],
          timeline: 'Immediate (within 48 hours)',
          riskMitigation: '95%',
        },
        conservative: {
          reserveIncrease: '€18M',
          sectorAdjustments: [
            'Reduce automotive sector exposure by 15%',
            'Review covenants for high-risk SMEs'
          ],
          timeline: 'Within 30 days',
          riskMitigation: '85%',
        },
        moderate: {
          reserveIncrease: '€10M',
          sectorAdjustments: [
            'Monitor automotive sector closely',
            'Prepare contingency plans'
          ],
          timeline: 'Within 60 days',
          riskMitigation: '70%',
        },
      },
    }
  },

  getScenarioById: async (id: string): Promise<Scenario> => {
    throw new Error('Not implemented');
  },

  deleteScenario: async (id: string): Promise<void> => {
    // Not implemented in backend
  },
};

// Activities API
export const activitiesAPI = {
  getActivities: async (): Promise<Activity[]> => {
    // Backend doesn't have this endpoint yet
    return [];
  },
};

// Chat API
export const chatAPI = {
  sendMessage: async (message: string): Promise<ChatMessage> => {
    const { data } = await api.post('/api/v1/chat', {
      query: message,
    });
    return {
      id: `msg_${Date.now()}`,
      role: 'assistant',
      content: data.answer,
      timestamp: new Date().toISOString(),
    };
  },

  getHistory: async (): Promise<ChatMessage[]> => {
    // Backend doesn't support history yet, return empty
    return [];
  },
};

// Alert API
export const alertAPI = {
  simulateFeed: async (): Promise<Alert> => {
    const { data } = await api.post('/api/v1/alerts/simulate')
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
    }
  },

  getAlertHistory: async (): Promise<Alert[]> => {
    const { data } = await api.get('/api/v1/alerts/history')
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
    }))
  },
}

export default api;
