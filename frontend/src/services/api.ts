import axios from 'axios';
import { API_BASE_URL } from '@/utils/constants';
import type {
  PortfolioMetrics,
  SME,
  AlertSignal,
  Task,
  Scenario,
  ChatMessage,
  Alert,
} from './types';

// ─── Single axios instance ────────────────────────────────────────────────────
// ALL traffic goes through backend port 8000.
// Backend proxies:  POST /api/v1/chat  →  agents:8081/chat
// Backend handles:  POST /api/v1/scenarios/run  +  GET /api/v1/scenarios/:id/status
// agentsApi is intentionally removed — no direct frontend→agents connection.
const api = axios.create({ baseURL: API_BASE_URL });

api.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error('API Error:', error.response?.status, error.config?.url, error.message);
    return Promise.reject(error);
  }
);

// ─── Helpers ─────────────────────────────────────────────────────────────────
const SECTOR_ICONS: Record<string, string> = {
  technology: '💻', software: '💻', retail: '🛍️',
  manufacturing: '🏭', healthcare: '🏥', financial: '🏦',
  finance: '🏦', construction: '🏗️', hospitality: '🏨',
  transport: '🚚', logistics: '🚚', energy: '⚡',
  agriculture: '🌾', education: '🎓', media: '📺',
};

const GEO_ICONS: Record<string, string> = {
  uk: '🇬🇧', 'united kingdom': '🇬🇧', de: '🇩🇪', germany: '🇩🇪',
  fr: '🇫🇷', france: '🇫🇷', es: '🇪🇸', spain: '🇪🇸',
  it: '🇮🇹', italy: '🇮🇹', nl: '🇳🇱', netherlands: '🇳🇱',
  ie: '🇮🇪', ireland: '🇮🇪', eu: '🇪🇺', europe: '🇪🇺',
};

function sectorIcon(name: string): string {
  const k = name.toLowerCase();
  for (const [key, icon] of Object.entries(SECTOR_ICONS)) if (k.includes(key)) return icon;
  return '🏢';
}

function geoIcon(name: string): string {
  const k = name.toLowerCase();
  for (const [key, icon] of Object.entries(GEO_ICONS)) if (k.includes(key)) return icon;
  return '🌍';
}

function formatExposure(value: number): string {
  if (!value) return '€0';
  if (value >= 1_000_000) return `€${(value / 1_000_000).toFixed(1)}M`;
  if (value >= 1_000) return `€${(value / 1_000).toFixed(0)}K`;
  return `€${value}`;
}

// ─── SME response mapper ──────────────────────────────────────────────────────
// Single source of truth for snake_case → camelCase mapping.
// Used by both getSMEs (list) and getSMEById (detail) so new fields
// are automatically available in both contexts.
function mapSMEResponse(sme: any): any {
  return {
    // Core fields (always present)
    id: sme.id,
    name: sme.name,
    riskScore: sme.risk_score,
    riskCategory: sme.risk_category,
    exposure: formatExposure(sme.exposure),
    sector: sme.sector,
    geography: sme.geography,
    trend: sme.trend,
    trendValue: sme.trend_value,

    // ── Rating overlay ──────────────────────────────────────────────────
    indicativeGrade: sme.indicative_grade ?? '',
    bankRating: sme.bank_rating ?? '',
    ratingGapNotches: sme.rating_gap_notches ?? 0,

    // ── PD overlay ──────────────────────────────────────────────────────
    pdOriginal: sme.pd_original ?? 0,
    pdAdjusted: sme.pd_adjusted ?? 0,

    // ── Score delta ─────────────────────────────────────────────────────
    scorePrevious: sme.score_previous ?? sme.risk_score ?? 0,
    scoreNarrative: sme.score_change_reason ?? sme.score_narrative ?? '',
    activeSignals: (sme.active_signals ?? []).map((s: any) => ({
      label: s.label ?? '',
      impact: s.impact ?? 0,
    })),

    // ── Detail panel ────────────────────────────────────────────────────
    bankRatingStale: sme.bank_rating_stale ?? (sme.rating_gap_notches ?? 0) >= 2,
    sectorHealth: sme.sector_health ?? 'stable',
    geographyRisk: sme.geography_risk ?? 'low',
    complianceStatus: sme.compliance_status ?? 'compliant',
    netProfitMargin: sme.net_profit_margin ?? 0,
    loanOriginationDate: sme.loan_origination_date ?? '',

    // ── Risk component scores ────────────────────────────────────────────
    scoreFinancial: sme.score_financial ?? 0,
    scoreOperational: sme.score_operational ?? 0,
    scoreMarket: sme.score_market ?? 0,
    scoreAltdata: sme.score_altdata ?? 0,

    // ── Pass through any extra fields the backend may add ───────────────
    revenue: sme.revenue,
    ebitda: sme.ebitda,
    employeeCount: sme.employee_count,
    debtServiceCoverage: sme.debt_service_coverage,
    currentRatio: sme.current_ratio,
    cashReserves: sme.cash_reserves,
    totalDebt: sme.total_debt,
    lastReviewDate: sme.last_review_date,
  };
}

// ─── Portfolio API ────────────────────────────────────────────────────────────
export const portfolioAPI = {
  // GET /api/v1/portfolio/summary
  getMetrics: async (): Promise<PortfolioMetrics> => {
    const { data } = await api.get('/api/v1/portfolio/summary');
    return {
      totalSMEs: data.total_smes,
      totalExposure: `€${(data.total_exposure / 1_000_000).toFixed(1)}M`,
      avgRiskScore: data.avg_risk_score,
      criticalCount: data.risk_distribution.counts.critical,
      mediumCount: data.risk_distribution.counts.medium,
      stableCount: data.risk_distribution.counts.stable,
      defaultProbability: 2.8,
      portfolioTrend: 'stable' as const,
    };
  },

  // GET /api/v1/portfolio/smes?limit=100
  getSMEs: async (): Promise<SME[]> => {
    const { data } = await api.get('/api/v1/portfolio/smes?limit=100');
    return data.smes.map(mapSMEResponse);
  },

  // GET /api/v1/portfolio/smes/:id
  getSMEById: async (id: string): Promise<any> => {
    const { data } = await api.get(`/api/v1/portfolio/smes/${id}`);
    return mapSMEResponse(data);
  },

  /**
   * GET /api/v1/portfolio/breakdown/:riskLevel
   * Backend: { risk_level, total: { smes, exposure }, by_sector[], by_geography[] }
   * Frontend (BreakdownModal) needs: { title, total.{smes,exposure,percent}, sectors[], geographies[] }
   * — icons and percents are derived here since backend doesn't provide them.
   */
  getBreakdownData: async (riskLevel: string) => {
    const { data } = await api.get(`/api/v1/portfolio/breakdown/${riskLevel}`);

    const totalSMEs = data.total?.smes ?? 0;
    const totalExposure = data.total?.exposure ?? 0;
    const portfolioPct = `${((totalSMEs / 1284) * 100).toFixed(1)}%`;

    const sectors = (data.by_sector ?? []).map((s: any) => {
      const count = s.count ?? s.smes ?? 0;
      return {
        icon: sectorIcon(s.sector ?? s.name ?? ''),
        name: s.sector ?? s.name ?? '—',
        smes: count,
        exposure: formatExposure(s.total_exposure ?? s.exposure ?? 0),
        percent: `${((count / (totalSMEs || 1)) * 100).toFixed(1)}%`,
      };
    });

    const geographies = (data.by_geography ?? []).map((g: any) => {
      const count = g.count ?? g.smes ?? 0;
      return {
        icon: geoIcon(g.geography ?? g.name ?? ''),
        name: g.geography ?? g.name ?? '—',
        smes: count,
        exposure: formatExposure(g.total_exposure ?? g.exposure ?? 0),
        percent: `${((count / (totalSMEs || 1)) * 100).toFixed(1)}%`,
      };
    });

    return {
      title: `${riskLevel.charAt(0).toUpperCase() + riskLevel.slice(1)} Risk — Detailed Breakdown`,
      total: { smes: totalSMEs, exposure: formatExposure(totalExposure), percent: portfolioPct },
      sectors,
      geographies,
    };
  },
};


// ─── Tasks API ────────────────────────────────────────────────────────────────
export const tasksAPI = {
  // GET /api/v1/tasks
  getTasks: async (): Promise<Task[]> => {
    const { data } = await api.get('/api/v1/tasks');
    return data.tasks ?? [];
  },

  // POST /api/v1/tasks
  createTask: async (task: Partial<Task>) => {
    const { data } = await api.post('/api/v1/tasks', task);
    return data;
  },

  // PUT /api/v1/tasks/:id
  updateTask: async (id: string, updates: Partial<Task>) => {
    const { data } = await api.put(`/api/v1/tasks/${id}`, updates);
    return data;
  },

  // DELETE /api/v1/tasks/:id
  deleteTask: async (id: string): Promise<void> => {
    await api.delete(`/api/v1/tasks/${id}`);
  },
};

// ─── Scenarios API ────────────────────────────────────────────────────────────
const SCENARIO_POLL_INTERVAL_MS = 1500;
const SCENARIO_POLL_TIMEOUT_MS = 120_000; // 2 min

async function pollScenarioJob(jobId: string): Promise<any> {
  const deadline = Date.now() + SCENARIO_POLL_TIMEOUT_MS;
  while (Date.now() < deadline) {
    await new Promise(r => setTimeout(r, SCENARIO_POLL_INTERVAL_MS));
    const { data } = await api.get(`/api/v1/scenarios/${jobId}/status`);
    if (data.status === 'completed') return data.result;
    if (data.status === 'failed') throw new Error(data.error ?? 'Scenario job failed');
    // queued / processing — continue polling
  }
  throw new Error('Scenario timed out after 2 minutes');
}

function mapJobResultToScenario(description: string, result: any): Scenario {
  // Support both camelCase (new scenario_service) and snake_case (legacy)
  const pi = result?.portfolioImpact ?? result?.portfolio_impact ?? {};
  const el = result?.estimatedLoss ?? result?.estimated_loss ?? {};
  const recs = result?.recommendations ?? null;

  return {
    id: `scenario_${Date.now()}`,
    name: description,
    status: 'completed',
    progress: 100,
    createdAt: new Date().toISOString(),
    completedAt: new Date().toISOString(),
    duration: result?.duration ?? result?.processing_time ?? 15,

    results: result ? {
      portfolioImpact: {
        criticalBefore: pi.criticalBefore ?? pi.critical_before ?? 0,
        criticalAfter: pi.criticalAfter ?? pi.critical_after ?? 0,
        defaultProbBefore: pi.defaultProbBefore ?? pi.default_prob_before ?? 0,
        defaultProbAfter: pi.defaultProbAfter ?? pi.default_prob_after ?? 0,
        avgScoreBefore: pi.avgScoreBefore ?? pi.avg_score_before ?? 0,
        avgScoreAfter: pi.avgScoreAfter ?? pi.avg_score_after ?? 0,
        totalExposure: pi.totalExposure ?? pi.total_exposure,
        newCriticalExposure: pi.newCriticalExposure ?? pi.new_critical_exposure,
      },

      // ── 3-year loss projection ─────────────────────────────────────
      estimatedLoss: {
        current: el.current ?? el.current_year ?? 0,
        year1: el.year1 ?? el.year_1 ?? 0,
        year2: el.year2 ?? el.year_2 ?? 0,
        year3: el.year3 ?? el.year_3 ?? 0,
        lgdAssumption: el.lgdAssumption ?? el.lgd_assumption ?? 0.45,
        note: el.note,
      },

      // ── Sector impact — richer shape ───────────────────────────────
      sectorImpact: (result.sectorImpact ?? result.sector_impact ?? []).map((s: any) => ({
        sector: s.sector,
        smes: s.smes ?? s.count ?? 0,
        avgChange: s.avgChange ?? s.avg_change ?? 0,
        newCritical: s.newCritical ?? s.new_critical ?? 0,
        totalExposure: s.totalExposure ?? s.total_exposure ?? 0,
        estimatedLoss: s.estimatedLoss ?? s.estimated_loss ?? 0,
      })),

      // ── Top impacted SMEs — extended shape ─────────────────────────
      topImpacted: (result.topImpacted ?? result.top_impacted ?? []).map((s: any) => ({
        smeId: s.smeId ?? s.sme_id,
        smeName: s.smeName ?? s.sme_name,
        scoreBefore: s.scoreBefore ?? s.score_before ?? 0,
        scoreAfter: s.scoreAfter ?? s.score_after ?? 0,
        change: s.change ?? 0,
        reason: s.reason ?? '',
        sector: s.sector,
        geography: s.geography,
        exposure: s.exposure,
      })),
    } : undefined,

    // ── Recommendations — map warranted tier + scope ───────────────────
    recommendations: recs ? {
      warrantedTier: recs.warranted_tier ?? recs.warrantedTier ?? 'moderate',
      recommendationScope: recs.recommendation_scope ?? recs.recommendationScope ?? 'portfolio',
      newCriticalCount: recs.new_critical_count ?? recs.newCriticalCount,
      estimatedLossCurrent: recs.estimated_loss_current ?? recs.estimatedLossCurrent,
      ultraConservative: {
        reserveIncrease: recs.ultraConservative?.reserveIncrease ?? recs.ultra_conservative?.reserve_increase ?? '',
        sectorAdjustments: recs.ultraConservative?.sectorAdjustments ?? recs.ultra_conservative?.sector_adjustments ?? [],
        timeline: recs.ultraConservative?.timeline ?? recs.ultra_conservative?.timeline ?? '30 days',
        riskMitigation: recs.ultraConservative?.riskMitigation ?? recs.ultra_conservative?.risk_mitigation ?? 'Maximum',
      },
      conservative: {
        reserveIncrease: recs.conservative?.reserveIncrease ?? '',
        sectorAdjustments: recs.conservative?.sectorAdjustments ?? [],
        timeline: recs.conservative?.timeline ?? '60 days',
        riskMitigation: recs.conservative?.riskMitigation ?? 'High',
      },
      moderate: {
        reserveIncrease: recs.moderate?.reserveIncrease ?? '',
        sectorAdjustments: recs.moderate?.sectorAdjustments ?? [],
        timeline: recs.moderate?.timeline ?? '90 days',
        riskMitigation: recs.moderate?.riskMitigation ?? 'Standard',
      },
    } : null,
  };
}

export const scenariosAPI = {
  // GET /api/v1/scenarios
  getScenarios: async (): Promise<Scenario[]> => {
    try {
      const { data } = await api.get('/api/v1/scenarios');
      return (data.scenarios ?? []).map((s: any) =>
        mapJobResultToScenario(s.name ?? s.description ?? 'Scenario', s.result ?? s)
      );
    } catch {
      return []; // endpoint may be empty on first load
    }
  },

  /**
   * POST /api/v1/scenarios/run  { description }  → { job_id }
   * then poll GET /api/v1/scenarios/:job_id/status until status === 'completed'
   */
  createScenario: async (description: string): Promise<Scenario> => {
    const { data } = await api.post('/api/v1/scenarios/run', { description });
    const jobId = data.job_id;
    if (!jobId) throw new Error('Backend did not return a job_id');
    const result = await pollScenarioJob(jobId);
    return mapJobResultToScenario(description, result);
  },

  getScenarioById: async (id: string): Promise<Scenario> => {
    const { data } = await api.get(`/api/v1/scenarios/${id}`);
    return mapJobResultToScenario(data.name ?? id, data.result ?? data);
  },

  deleteScenario: async (id: string): Promise<void> => {
    await api.delete(`/api/v1/scenarios/${id}`);
  },
};

// ─── Chat API ─────────────────────────────────────────────────────────────────
// POST /api/v1/chat  (backend proxies to agents:8081/chat)
export const chatAPI = {
  sendMessage: async (message: string, sessionId: string = 'default') => {
    const { data } = await api.post('/api/v1/chat', { message, session_id: sessionId });
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

// ─── Alert API ────────────────────────────────────────────────────────────────
// Maps both live-feed alerts (Change 8 shape) and historic news intelligence
// into the unified Alert type.
function mapAlertResponse(raw: any): Alert {
  const a = raw.alert ?? raw;
  // signals: backend may return news-style [{source,detail}] or alert-style [{signal_type,detail,source}]
  const signals: AlertSignal[] = (a.signals ?? []).map((s: any) => ({
    source: s.source ?? s.signal_type ?? '',
    detail: s.detail ?? '',
  }));
  return {
    id: a.id ?? `alert_${Date.now()}`,
    timestamp: a.timestamp ?? new Date().toISOString(),
    severity: a.severity ?? 'warning',
    scope: a.scope ?? 'sme',
    affected_count: a.affected_count ?? 1,
    smeId: a.sme_id ?? '',
    smeName: a.sme_name ?? '',
    exposure: typeof a.exposure === 'number'
      ? formatExposure(a.exposure)
      : (a.exposure ?? '€0'),
    title: a.title ?? a.event_type ?? 'Alert',
    summary: a.summary ?? a.event_summary ?? '',
    signals,
    recommendation: a.recommendation ?? '',
    dismissed: false,
  };
}

export const alertAPI = {
  // POST /api/v1/alerts/simulate — fire a new live alert
  simulateFeed: async (): Promise<Alert> => {
    const { data } = await api.post('/api/v1/alerts/simulate');
    return mapAlertResponse(data);
  },

  // GET /api/v1/alerts/history — all historic alerts (news + past live alerts)
  getAlertHistory: async (): Promise<Alert[]> => {
    const { data } = await api.get('/api/v1/alerts/history');
    return (data.alerts ?? []).map(mapAlertResponse);
  },
};

export default api;