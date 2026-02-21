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

// Alert Signal (from news intelligence / alert feed)
export interface AlertSignal {
  source: string;
  detail: string;
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

// Unified Alert — covers SME, sector, geography and macro-level signals
export interface Alert {
  id: string;
  timestamp: string;
  severity: 'critical' | 'warning';
  scope: 'sme' | 'sector' | 'geography' | 'macro';
  affected_count: number;
  smeId: string;
  smeName: string;
  exposure: string;
  title: string;
  summary: string;
  signals: AlertSignal[];
  recommendation: string;
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