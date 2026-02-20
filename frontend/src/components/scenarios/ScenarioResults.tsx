import { useState } from 'react'
import { ChevronDown, ChevronUp, TrendingUp } from 'lucide-react'
import { formatRelativeTime, formatPercent } from '@/utils/formatters'
import { Button } from '../common/Button'
import RecommendationsTabs from './RecommendationsTabs'
import type { Scenario } from '@/services/types'

interface ScenarioResultsProps {
  scenario: Scenario
}

const ScenarioResults = ({ scenario }: ScenarioResultsProps) => {
  const [expanded, setExpanded] = useState(false)

  if (!scenario.results) {
    return (
      <div style={{ background: 'var(--uui-surface-main)', border: '1px solid var(--uui-neutral-60)', borderRadius: 'var(--uui-border-radius)', padding: '18px', textAlign: 'center' }}>
        <p style={{ fontSize: '13px', color: 'var(--uui-text-tertiary)' }}>No results available for this scenario.</p>
      </div>
    )
  }

  const results = scenario.results

  const metricCard = (label: string, before: number | string, after: number | string, delta: string, color: string) => (
    <div style={{ background: 'var(--uui-neutral-70)', border: '1px solid var(--uui-neutral-60)', borderRadius: 'var(--uui-border-radius)', padding: '12px' }}>
      <div style={{ fontSize: '11px', color: 'var(--uui-text-tertiary)', marginBottom: '6px' }}>{label}</div>
      <div style={{ fontSize: '16px', fontWeight: 700, color: 'var(--uui-text-primary)', fontFamily: 'var(--uui-font-mono)', marginBottom: '4px' }}>
        {before} → {after}
      </div>
      <div style={{ fontSize: '11px', color, display: 'flex', alignItems: 'center', gap: '3px' }}>
        <TrendingUp size={11} />
        {delta}
      </div>
    </div>
  )

  return (
    <div style={{ background: 'var(--uui-surface-main)', border: '1px solid var(--uui-neutral-60)', borderRadius: 'var(--uui-border-radius)', overflow: 'hidden' }}>
      {/* Header - clickable */}
      <div
        onClick={() => setExpanded(!expanded)}
        style={{ padding: '16px', cursor: 'pointer', display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', background: expanded ? 'var(--uui-neutral-70)' : 'var(--uui-surface-main)', borderBottom: expanded ? '1px solid var(--uui-neutral-60)' : 'none', transition: 'background 0.2s' }}
      >
        <div style={{ flex: 1 }}>
          <div style={{ fontSize: '14px', fontWeight: 700, color: 'var(--uui-text-primary)', marginBottom: '4px' }}>{scenario.name}</div>
          <div style={{ fontSize: '11px', color: 'var(--uui-text-tertiary)' }}>
            Completed {formatRelativeTime(scenario.completedAt!)} • Duration: {scenario.duration}s
          </div>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <div style={{ textAlign: 'right' }}>
            <div style={{ fontSize: '13px', fontWeight: 600, color: 'var(--uui-text-secondary)' }}>
              Critical: {results.portfolioImpact.criticalBefore} → {results.portfolioImpact.criticalAfter}
            </div>
            <div style={{ fontSize: '11px', color: 'var(--uui-critical-60)' }}>
              +{results.portfolioImpact.criticalAfter - results.portfolioImpact.criticalBefore} SMEs
            </div>
          </div>
          {expanded
            ? <ChevronUp size={18} style={{ color: 'var(--uui-text-tertiary)' }} />
            : <ChevronDown size={18} style={{ color: 'var(--uui-text-tertiary)' }} />}
        </div>
      </div>

      {/* Expanded Content */}
      {expanded && (
        <div style={{ padding: '18px', background: 'var(--uui-neutral-80)', display: 'flex', flexDirection: 'column', gap: '18px' }}>

          {/* Portfolio Impact */}
          <section>
            <div style={{ fontSize: '11px', fontWeight: 600, color: 'var(--uui-text-tertiary)', textTransform: 'uppercase', marginBottom: '12px' }}>
              Portfolio Impact Summary
            </div>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: '9px' }}>
              {metricCard('Critical SMEs',
                results.portfolioImpact.criticalBefore, results.portfolioImpact.criticalAfter,
                `+${results.portfolioImpact.criticalAfter - results.portfolioImpact.criticalBefore}`,
                'var(--uui-critical-60)')}
              {metricCard('Default Probability',
                formatPercent(results.portfolioImpact.defaultProbBefore), formatPercent(results.portfolioImpact.defaultProbAfter),
                `+${formatPercent(results.portfolioImpact.defaultProbAfter - results.portfolioImpact.defaultProbBefore)}`,
                'var(--uui-critical-60)')}
              {metricCard('Avg Risk Score',
                results.portfolioImpact.avgScoreBefore, results.portfolioImpact.avgScoreAfter,
                `+${results.portfolioImpact.avgScoreAfter - results.portfolioImpact.avgScoreBefore}`,
                'var(--uui-warning-60)')}
            </div>
          </section>

          {/* Recommendations */}
          {scenario.recommendations && (
            <RecommendationsTabs recommendations={scenario.recommendations} scenarioName={scenario.name} />
          )}

          {/* Top Impacted SMEs */}
          <section>
            <div style={{ fontSize: '11px', fontWeight: 600, color: 'var(--uui-text-tertiary)', textTransform: 'uppercase', marginBottom: '12px' }}>
              Top Impacted SMEs
            </div>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
              {results.topImpacted.map((sme: any, idx: number) => (
                <div key={idx} style={{ background: 'var(--uui-neutral-70)', border: '1px solid var(--uui-neutral-60)', borderRadius: 'var(--uui-border-radius)', padding: '12px', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                  <div style={{ flex: 1 }}>
                    <div style={{ fontSize: '13px', fontWeight: 600, color: 'var(--uui-text-primary)', marginBottom: '3px' }}>
                      {sme.smeId} {sme.smeName}
                    </div>
                    <div style={{ fontSize: '11px', color: 'var(--uui-text-tertiary)' }}>{sme.reason}</div>
                  </div>
                  <div style={{ textAlign: 'right' }}>
                    <div style={{ fontSize: '13px', fontFamily: 'var(--uui-font-mono)', color: 'var(--uui-text-secondary)' }}>
                      {sme.scoreBefore} → {sme.scoreAfter}
                    </div>
                    <div style={{ fontSize: '11px', fontWeight: 600, color: 'var(--uui-critical-60)' }}>+{sme.change}</div>
                  </div>
                </div>
              ))}
            </div>
          </section>

          {/* Actions */}
          <div style={{ display: 'flex', alignItems: 'center', gap: '9px' }}>
            <Button variant="primary" size="sm">📋 Create Tasks for Top SMEs</Button>
            <Button variant="secondary" size="sm">📊 Export Full Report</Button>
            <Button variant="secondary" size="sm">🗑️ Delete Scenario</Button>
          </div>
        </div>
      )}
    </div>
  )
}

export default ScenarioResults