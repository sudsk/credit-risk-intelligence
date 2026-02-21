// SME Types
export interface SME {
  id: string;
  name: string;
  riskScore: number;
  riskCategory: 'critical' | 'medium' | 'stable';
  exposure: string;
  sector: string;
  geography: string;
  trend: 'up' | 'down' | 'stable';
  trendValue: number;
}

// Portfolio Types
export interface PortfolioMetrics {
  totalSMEs: number;
  totalExposure: string;
  avgRiskScore: number;
  criticalCount: number;
  mediumCount: number;
  stableCount: number;
  defaultProbability: number;
  portfolioTrend: 'up' | 'down' | 'stable';
}

export interface SectorBreakdown {
  icon: string;
  name: string;
  smes: number;
  exposure: string;
  percent: string;
}

export interface GeographyBreakdown {
  icon: string;
  name: string;
  smes: number;
  exposure: string;
  percent: string;
}

export interface BreakdownData {
  title: string;
  total: {
    smes: number;
    exposure: string;
    percent: string;
  };
  sectors: SectorBreakdown[];
  geographies: GeographyBreakdown[];
}

// Event Types
export interface PredictedEvent {
  id: string;
  date: string;
  daysUntil: number;          // mapped from backend snake_case days_until
  title: string;
  probability: number;
  affects: {
    smes: number;
    exposure: string;         // formatted string e.g. "€2.1M"
  };
  impact: string;
  keySMEs: string[];          // non-optional — api.ts mapper defaults to []
  source: string;
  description: string;
}

// News Types — corrected to match backend response + NewsIntelligence.tsx
export interface NewsSignal {
  source: string;
  detail: string;
}

export interface NewsItem {
  id: string;
  timestamp: string;
  sme_id: string;
  sme_name: string;
  exposure: string;           // formatted string e.g. "€250K"
  title: string;
  summary: string;
  severity: 'critical' | 'warning';
  signals: NewsSignal[];
  recommendation: string;
}

// Task Types
export interface Task {
  id: string;
  title: string;
  smeId: string;
  smeName: string;
  exposure: string;
  assignee: string;
  priority: 'high' | 'medium' | 'low';
  dueDate: string;
  status: 'overdue' | 'due_today' | 'upcoming' | 'completed';
  description: string;
  source: string;
  createdAt: string;
}

// Scenario Types
export interface Scenario {
  id: string;
  name: string;
  status: 'in_progress' | 'completed';
  progress?: number;
  duration?: number;
  createdAt: string;
  completedAt?: string;
  results?: ScenarioResults;
  recommendations?: ScenarioRecommendation;
}

export interface ScenarioResults {
  portfolioImpact: {
    criticalBefore: number;
    criticalAfter: number;
    defaultProbBefore: number;
    defaultProbAfter: number;
    avgScoreBefore: number;
    avgScoreAfter: number;
  };
  sectorImpact: {
    sector: string;
    smes: number;
    avgChange: number;
  }[];
  topImpacted: {
    smeId: string;
    smeName: string;
    scoreBefore: number;
    scoreAfter: number;
    change: number;
    reason: string;
  }[];
}

// Chat Types
export interface ChatMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: string;
}

export interface Alert {
  id: string;
  timestamp: string;
  severity: 'critical' | 'warning';
  smeId: string;
  smeName: string;
  exposure: string;
  eventType: 'executive_departure' | 'payment_delay' | 'regulation' | 'sector_shock' | 'client_churn';
  eventSummary: string;
  dataSources: string[];
  dismissed: boolean;
}

export interface RecommendationTier {
  reserveIncrease: string;
  sectorAdjustments: string[];
  timeline: string;
  riskMitigation: string;
}

export interface ScenarioRecommendation {
  ultraConservative: RecommendationTier;
  conservative: RecommendationTier;
  moderate: RecommendationTier;
}