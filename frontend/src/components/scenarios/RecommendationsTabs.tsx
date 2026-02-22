import { useState } from 'react'
import { Shield, TrendingDown, Clock, User } from 'lucide-react'
import { Button } from '../common/Button'
import type { ScenarioRecommendation } from '@/services/types'

interface RecommendationsTabsProps {
  recommendations: ScenarioRecommendation
  scenarioName: string
  // Controls whether actions use portfolio-level language (CRO view) or
  // SME-level language (credit officer view). Defaults to 'portfolio'.
  recommendationScope?: 'portfolio' | 'sme'
}

const tabs = [
  { id: 'ultraConservative' as const, label: 'Ultra-Conservative', color: 'var(--uui-critical-60)' },
  { id: 'conservative' as const, label: 'Conservative', color: 'var(--uui-warning-60)' },
  { id: 'moderate' as const, label: 'Moderate', color: 'var(--uui-primary-60)' },
]

// ── Scope-specific fallback actions ──────────────────────────────────────────
// Used when the backend doesn't provide sectorAdjustments for an SME-scoped
// recommendation, or to supplement portfolio-level actions with SME language.
//
// Portfolio scope (CRO view): sector exposure + provisioning language
// SME scope (credit officer view): client engagement + covenant language

const SME_ACTIONS: Record<'ultraConservative' | 'conservative' | 'moderate', string[]> = {
  ultraConservative: [
    'Engage client immediately — schedule urgent review call within 5 days',
    'Request updated management accounts and cash flow forecast',
    'Initiate formal covenant review — check compliance with all loan covenants',
    'Consider temporary credit line freeze pending review outcome',
    'Escalate to senior credit officer and risk committee',
  ],
  conservative: [
    'Engage client — schedule review call within 2 weeks',
    'Request updated financials and trading update',
    'Review covenant headroom and flag any breaches',
    'Increase monitoring frequency to monthly',
  ],
  moderate: [
    'Send routine client check-in — request next quarterly update',
    'Review latest Companies House filings',
    'Monitor payment behaviour over next 30 days',
  ],
}

const PORTFOLIO_ACTIONS: Record<'ultraConservative' | 'conservative' | 'moderate', string[]> = {
  ultraConservative: [
    'Stop new originations in highest-risk sectors immediately',
    'Increase total provisions — apply 1.5× additional expected loss as reserve buffer',
    'Reduce maximum exposure per SME by 30% for critical category',
    'Notify board risk committee — portfolio stress threshold breached',
  ],
  conservative: [
    'Reduce new lending in most-impacted sectors by 20%',
    'Increase total provisions for newly critical SME exposure',
    'Tighten covenant monitoring frequency to monthly for critical SMEs',
    'Prepare contingency plan for further deterioration',
  ],
  moderate: [
    'Monitor most-exposed sectors closely — quarterly review',
    'No immediate restriction on new lending required',
    'Update portfolio watch list with newly impacted SMEs',
  ],
}

const RecommendationsTabs = ({
  recommendations,
  scenarioName,
  recommendationScope,
}: RecommendationsTabsProps) => {
  // Prefer the scope from recommendations object (set by backend tier logic),
  // fall back to the explicit prop, then default to portfolio.
  const scope: 'portfolio' | 'sme' =
    recommendations.recommendationScope ?? recommendationScope ?? 'portfolio'

  const isPortfolio = scope === 'portfolio'

  // Default active tab to warranted tier when available, otherwise conservative
  const defaultTab =
    (recommendations.warrantedTier === 'ultra_conservative'
      ? 'ultraConservative'
      : recommendations.warrantedTier ?? 'conservative') as
    'ultraConservative' | 'conservative' | 'moderate'

  const [activeTab, setActiveTab] = useState<'ultraConservative' | 'conservative' | 'moderate'>(
    defaultTab
  )

  const activeData = recommendations[activeTab]
  const activeColor = tabs.find(t => t.id === activeTab)?.color ?? 'var(--uui-primary-60)'
  const isWarranted = (
    (activeTab === 'ultraConservative' && recommendations.warrantedTier === 'ultra_conservative') ||
    (activeTab === recommendations.warrantedTier)
  )

  // Resolve which action bullets to show:
  // 1. Use backend-provided sectorAdjustments if present and non-empty
  // 2. Otherwise fall back to scope-specific hardcoded actions
  const fallbackActions = isPortfolio ? PORTFOLIO_ACTIONS[activeTab] : SME_ACTIONS[activeTab]
  const actions =
    activeData?.sectorAdjustments?.length > 0
      ? activeData.sectorAdjustments
      : fallbackActions

  const adjustmentsLabel = isPortfolio ? 'Portfolio Adjustments' : 'Client Actions'
  const AdjustmentsIcon = isPortfolio ? TrendingDown : User

  return (
    <div style={{
      background: 'var(--uui-neutral-70)',
      border: '1px solid var(--uui-neutral-60)',
      borderRadius: 'var(--uui-border-radius)',
      padding: '16px',
    }}>
      {/* Title row — shows scope badge so viewer knows which mode they're in */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '12px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', fontSize: '12px', fontWeight: 600, color: 'var(--uui-text-tertiary)', textTransform: 'uppercase' }}>
          <Shield size={14} />
          Recommended Actions
        </div>
        {/* Scope badge */}
        <span style={{
          fontSize: '10px', fontWeight: 700, letterSpacing: '0.4px', textTransform: 'uppercase',
          padding: '2px 8px', borderRadius: '4px',
          background: isPortfolio ? 'rgba(99,102,241,0.12)' : 'rgba(16,185,129,0.12)',
          color: isPortfolio ? 'var(--uui-primary-60)' : 'var(--uui-success-60)',
          border: `1px solid ${isPortfolio ? 'rgba(99,102,241,0.3)' : 'rgba(16,185,129,0.3)'}`,
        }}>
          {isPortfolio ? '🏦 Portfolio' : '👤 SME'}
        </span>
      </div>

      {/* Warranted tier context — shown when we know which tier is warranted */}
      {recommendations.warrantedTier && (
        <div style={{
          fontSize: '11px', color: 'var(--uui-text-tertiary)',
          marginBottom: '12px', lineHeight: 1.5,
        }}>
          Warranted tier:&nbsp;
          <span style={{
            fontWeight: 700, color: tabs.find(t =>
              t.id === (recommendations.warrantedTier === 'ultra_conservative' ? 'ultraConservative' : recommendations.warrantedTier)
            )?.color ?? 'var(--uui-text-primary)'
          }}>
            {recommendations.warrantedTier === 'ultra_conservative'
              ? 'Ultra-Conservative'
              : recommendations.warrantedTier === 'conservative'
                ? 'Conservative'
                : 'Moderate'}
          </span>
          {recommendations.newCriticalCount !== undefined && (
            <span> — {recommendations.newCriticalCount} newly critical SME{recommendations.newCriticalCount !== 1 ? 's' : ''}</span>
          )}
        </div>
      )}

      {/* Tab Buttons */}
      <div style={{ display: 'flex', gap: '6px', marginBottom: '16px' }}>
        {tabs.map((tab) => {
          const isActive = activeTab === tab.id
          const isWarrTier = (
            (tab.id === 'ultraConservative' && recommendations.warrantedTier === 'ultra_conservative') ||
            (tab.id === recommendations.warrantedTier)
          )
          return (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              style={{
                flex: 1, padding: '8px', fontSize: '12px', fontWeight: 600,
                borderRadius: 'var(--uui-border-radius)',
                border: `2px solid ${tab.color}`,
                background: isActive ? tab.color : 'transparent',
                color: isActive ? 'white' : 'var(--uui-text-secondary)',
                cursor: 'pointer', transition: 'all 0.2s',
                fontFamily: 'var(--uui-font)',
                // Warranted tier gets a subtle dot indicator below
                position: 'relative' as const,
              }}
            >
              {tab.label}
              {/* Small dot below tab label for warranted tier */}
              {isWarrTier && (
                <span style={{
                  position: 'absolute', bottom: '-7px', left: '50%',
                  transform: 'translateX(-50%)',
                  width: '5px', height: '5px',
                  borderRadius: '50%',
                  background: tab.color,
                  display: 'block',
                }} />
              )}
            </button>
          )
        })}
      </div>
      {/* Dot spacing */}
      <div style={{ marginBottom: '8px' }} />

      {/* Content */}
      {activeData && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '9px' }}>

          {/* Reserve Increase */}
          <div style={{
            background: 'var(--uui-neutral-80)',
            border: '1px solid var(--uui-neutral-60)',
            borderRadius: 'var(--uui-border-radius)',
            padding: '12px',
            display: 'flex', alignItems: 'center', justifyContent: 'space-between',
          }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <Shield size={16} style={{ color: 'var(--uui-text-tertiary)' }} />
              <span style={{ fontSize: '13px', fontWeight: 600, color: 'var(--uui-text-secondary)' }}>
                {isPortfolio ? 'Reserve Increase' : 'Recommended Reserve'}
              </span>
            </div>
            <div style={{ textAlign: 'right' }}>
              <div style={{ fontSize: '22px', fontWeight: 700, color: activeColor, fontFamily: 'var(--uui-font-mono)' }}>
                {activeData.reserveIncrease ?? '—'}
              </div>
              <div style={{ fontSize: '11px', color: 'var(--uui-text-tertiary)' }}>
                {activeData.riskMitigation} risk coverage
              </div>
            </div>
          </div>

          {/* Scope-aware actions block */}
          {actions.length > 0 && (
            <div style={{
              background: 'var(--uui-neutral-80)',
              border: `1px solid ${isWarranted ? activeColor : 'var(--uui-neutral-60)'}`,
              borderRadius: 'var(--uui-border-radius)',
              padding: '12px',
            }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '9px' }}>
                <AdjustmentsIcon size={16} style={{ color: 'var(--uui-text-tertiary)' }} />
                <span style={{ fontSize: '13px', fontWeight: 600, color: 'var(--uui-text-secondary)' }}>
                  {adjustmentsLabel}
                </span>
                {/* "Recommended" tag on warranted tier's action block */}
                {isWarranted && (
                  <span style={{
                    marginLeft: 'auto',
                    fontSize: '10px', fontWeight: 700, letterSpacing: '0.3px',
                    padding: '1px 6px', borderRadius: '4px',
                    background: `${activeColor}22`,
                    color: activeColor,
                    border: `1px solid ${activeColor}44`,
                  }}>
                    Recommended
                  </span>
                )}
              </div>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
                {actions.map((adj, idx) => (
                  <div key={idx} style={{
                    display: 'flex', alignItems: 'flex-start', gap: '8px',
                    fontSize: '12px', color: 'var(--uui-text-secondary)',
                  }}>
                    <span style={{ color: activeColor, marginTop: '2px', flexShrink: 0 }}>•</span>
                    <span>{adj}</span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Timeline */}
          <div style={{
            background: 'var(--uui-neutral-80)',
            border: '1px solid var(--uui-neutral-60)',
            borderRadius: 'var(--uui-border-radius)',
            padding: '12px',
            display: 'flex', alignItems: 'center', justifyContent: 'space-between',
          }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <Clock size={16} style={{ color: 'var(--uui-text-tertiary)' }} />
              <span style={{ fontSize: '13px', fontWeight: 600, color: 'var(--uui-text-secondary)' }}>
                Implementation Timeline
              </span>
            </div>
            <span style={{ fontSize: '13px', fontFamily: 'var(--uui-font-mono)', color: 'var(--uui-text-primary)' }}>
              {activeData.timeline}
            </span>
          </div>

          {/* Export/task buttons — label changes with scope */}
          <div style={{ display: 'flex', gap: '9px', paddingTop: '4px' }}>
            <Button variant="primary" size="sm">
              📄 Export {tabs.find(t => t.id === activeTab)?.label} Plan
            </Button>
            <Button variant="secondary" size="sm">
              {isPortfolio ? '📋 Create Portfolio Tasks' : '📋 Create SME Task'}
            </Button>
          </div>

        </div>
      )}
    </div>
  )
}

export default RecommendationsTabs