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

  // ── Rating overlay (live vs bank's static rating) ──────────────────────
  // Our real-time indicative grade derived from live risk score
  indicativeGrade: string;           // e.g. 'B', 'CCC', 'CC'
  // Bank's official rating from their system (updated quarterly)
  bankRating: string;                // e.g. 'BB+', 'BBB-'
  // How many notches our grade is worse than the bank's (positive = we see more risk)
  ratingGapNotches: number;          // 0 = aligned, 2+ = stale bank rating flag

  // ── PD overlay (bank's static PD vs our signal-adjusted PD) ───────────
  pdOriginal: number;                // bank's system PD (%) e.g. 3.0
  pdAdjusted: number;                // our overlay PD after signals (%) e.g. 5.4

  // ── Score delta ────────────────────────────────────────────────────────
  scorePrevious: number;             // score before recent signals fired
  scoreNarrative: string;            // "Score moved 45→68 because: (1) CTO departure..."
  activeSignals: ActiveSignal[];     // top signals driving the score

  // ── Detail panel fields ────────────────────────────────────────────────
  bankRatingStale: boolean;          // true when ratingGapNotches >= 2
  sectorHealth: 'improving' | 'stable' | 'deteriorating';
  geographyRisk: 'low' | 'medium' | 'high';
  complianceStatus: 'compliant' | 'watch' | 'under_review' | 'breach';
  netProfitMargin: number;           // %
  loanOriginationDate: string;       // ISO date string

  // ── Risk component scores (40/25/20/15 breakdown) ─────────────────────
  scoreFinancial: number;
  scoreOperational: number;
  scoreMarket: number;
  scoreAltdata: number;
}

export interface ActiveSignal {
  label: string;
  impact: number;   // positive = increases risk score
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
    // Exposure fields
    totalExposure?: number;
    newCriticalExposure?: number;
  };

  // ── 3-year loss projection ─────────────────────────────────────────────
  // All figures in GBP. Labelled as estimated throughout UI.
  estimatedLoss: {
    current: number;    // additional expected loss this year
    year1: number;
    year2: number;
    year3: number;
    lgdAssumption?: number;   // LGD used (default 0.45)
    note?: string;
  };

  // ── Sector breakdown — richer than before ─────────────────────────────
  sectorImpact: SectorImpact[];

  topImpacted: TopImpactedSME[];
}

export interface SectorImpact {
  sector: string;
  smes: number;
  avgChange: number;
  newCritical: number;
  totalExposure: number;
  estimatedLoss: number;    // sector-level estimated loss in £
}

export interface TopImpactedSME {
  smeId: string;
  smeName: string;
  scoreBefore: number;
  scoreAfter: number;
  change: number;
  reason: string;
  sector?: string;
  geography?: string;
  exposure?: number;
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
  reserveIncrease: string;        // formatted e.g. '£2.4M'
  sectorAdjustments: string[];    // list of action bullets
  timeline: string;               // e.g. '30 days', '60 days'
  riskMitigation: string;         // 'Maximum' | 'High' | 'Standard'
}

export interface ScenarioRecommendation {
  warrantedTier: 'ultra_conservative' | 'conservative' | 'moderate';
  ultraConservative: RecommendationTier;
  conservative: RecommendationTier;
  moderate: RecommendationTier;
  recommendationScope: 'portfolio' | 'sme';
  newCriticalCount?: number;
  estimatedLossCurrent?: number;
}