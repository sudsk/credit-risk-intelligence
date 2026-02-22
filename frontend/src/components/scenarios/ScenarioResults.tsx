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
          <div style={{ fontSize: '11px', color: 'var(--uui-text-tertiary)', display: 'flex', alignItems: 'center', gap: '8px', flexWrap: 'wrap' }}>
            <span>Completed {formatRelativeTime(scenario.completedAt!)} • Duration: {scenario.duration}s</span>
            <span style={{
              padding: '2px 7px',
              background: 'rgba(245,158,11,0.12)',
              border: '1px solid rgba(245,158,11,0.5)',
              borderRadius: '4px',
              color: '#f59e0b',
              fontWeight: 700,
              fontSize: '10px',
              letterSpacing: '0.3px',
            }}>
              ⚠️ Estimated impact — based on historical macro vectors
            </span>
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
            <div style={{ display: 'flex', alignItems: 'baseline', justifyContent: 'space-between', marginBottom: '12px' }}>
              <div style={{ fontSize: '11px', fontWeight: 600, color: 'var(--uui-text-tertiary)', textTransform: 'uppercase' }}>
                Portfolio Impact Summary
              </div>
              <div style={{ fontSize: '10px', color: 'var(--uui-text-tertiary)', fontStyle: 'italic' }}>
                Estimated — based on historical macro vectors
              </div>
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

          {/* ── Estimated Loss Projection ─────────────────────────────────────
              Current year + 3-year forward view of additional expected loss.
              Bar width shows relative magnitude across years; value shown inline
              or as end label when bar is too narrow.
              Renders only when estimatedLoss is present and current > 0.        */}
          {results.estimatedLoss && results.estimatedLoss.current > 0 && (() => {
            const el = results.estimatedLoss
            const years = [
              { label: 'Current year', value: el.current },
              { label: 'Year 1', value: el.year1 },
              { label: 'Year 2', value: el.year2 },
              { label: 'Year 3', value: el.year3 },
            ]
            const maxVal = Math.max(...years.map(y => y.value), 1)
            const fmtGbp = (v: number) =>
              v >= 1_000_000 ? `£${(v / 1_000_000).toFixed(1)}M`
                : v >= 1_000 ? `£${(v / 1_000).toFixed(0)}K`
                  : `£${v}`

            return (
              <section>
                <div style={{ display: 'flex', alignItems: 'baseline', justifyContent: 'space-between', marginBottom: '12px' }}>
                  <div style={{ fontSize: '11px', fontWeight: 600, color: 'var(--uui-text-tertiary)', textTransform: 'uppercase' }}>
                    Estimated Loss Projection
                  </div>
                  <div style={{ fontSize: '10px', color: '#f59e0b', fontWeight: 600 }}>⚠️ Estimated</div>
                </div>
                <div style={{
                  background: 'var(--uui-neutral-70)',
                  border: '1px solid var(--uui-neutral-60)',
                  borderRadius: 'var(--uui-border-radius)',
                  padding: '14px 16px',
                  display: 'flex', flexDirection: 'column', gap: '10px',
                }}>
                  {years.map(({ label, value }, idx) => {
                    const barPct = Math.round((value / maxVal) * 100)
                    // Bars deepen in opacity year-on-year — visual cue that risk compounds
                    const opacity = 0.45 + idx * 0.14
                    const showInline = barPct > 28
                    return (
                      <div key={label} style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                        <div style={{ width: '84px', fontSize: '11px', color: 'var(--uui-text-tertiary)', flexShrink: 0 }}>
                          {label}
                        </div>
                        <div style={{ flex: 1, height: '22px', background: 'var(--uui-neutral-60)', borderRadius: '3px', overflow: 'hidden' }}>
                          <div style={{
                            width: `${barPct}%`, height: '100%',
                            background: `rgba(239,68,68,${opacity})`,
                            borderRadius: '3px',
                            display: 'flex', alignItems: 'center', paddingLeft: '7px',
                          }}>
                            {showInline && (
                              <span style={{ fontSize: '11px', fontWeight: 700, color: '#fff', fontFamily: 'var(--uui-font-mono)', whiteSpace: 'nowrap' }}>
                                {fmtGbp(value)}
                              </span>
                            )}
                          </div>
                        </div>
                        {!showInline && (
                          <div style={{ fontSize: '11px', fontWeight: 700, fontFamily: 'var(--uui-font-mono)', color: 'var(--uui-critical-60)', width: '56px', flexShrink: 0, textAlign: 'right' }}>
                            {fmtGbp(value)}
                          </div>
                        )}
                      </div>
                    )
                  })}
                  <div style={{ fontSize: '10px', color: 'var(--uui-text-tertiary)', paddingTop: '8px', borderTop: '1px solid var(--uui-neutral-60)' }}>
                    {el.note ?? `Additional expected loss estimated using LGD ${((el.lgdAssumption ?? 0.45) * 100).toFixed(0)}%. Not a re-run of the bank's full stress model.`}
                  </div>
                </div>
              </section>
            )
          })()}

          {/* ── Sector Impact Bar Chart ───────────────────────────────────────
              Horizontal bars per sector — sorted worst-first.
              Columns: sector name | score delta bar | new critical count | est. loss.
              Renders only when sectorImpact array is non-empty.               */}
          {results.sectorImpact && results.sectorImpact.length > 0 && (() => {
            const sorted = [...results.sectorImpact].sort((a, b) => b.avgChange - a.avgChange)
            const maxChange = Math.max(...sorted.map(s => s.avgChange), 1)
            const fmtGbp = (v: number) =>
              v >= 1_000_000 ? `£${(v / 1_000_000).toFixed(1)}M`
                : v >= 1_000 ? `£${(v / 1_000).toFixed(0)}K`
                  : v > 0 ? `£${v}` : '—'

            return (
              <section>
                <div style={{ display: 'flex', alignItems: 'baseline', justifyContent: 'space-between', marginBottom: '12px' }}>
                  <div style={{ fontSize: '11px', fontWeight: 600, color: 'var(--uui-text-tertiary)', textTransform: 'uppercase' }}>
                    Sector Impact Breakdown
                  </div>
                  <div style={{ fontSize: '10px', color: 'var(--uui-text-tertiary)', fontStyle: 'italic' }}>
                    Estimated — based on historical macro vectors
                  </div>
                </div>
                <div style={{
                  background: 'var(--uui-neutral-70)',
                  border: '1px solid var(--uui-neutral-60)',
                  borderRadius: 'var(--uui-border-radius)',
                  overflow: 'hidden',
                }}>
                  {/* Column headers */}
                  <div style={{
                    display: 'grid', gridTemplateColumns: '148px 1fr 72px 76px',
                    padding: '8px 14px',
                    background: 'var(--uui-neutral-80)',
                    borderBottom: '1px solid var(--uui-neutral-60)',
                  }}>
                    {['Sector', 'Score Δ', 'New Critical', 'Est. Loss'].map((h, i) => (
                      <div key={i} style={{ fontSize: '10px', fontWeight: 600, color: 'var(--uui-text-tertiary)', textTransform: 'uppercase', textAlign: i >= 2 ? 'right' : 'left' }}>
                        {h}
                      </div>
                    ))}
                  </div>

                  {/* Sector rows */}
                  {sorted.map((s, idx) => {
                    const barPct = Math.round((s.avgChange / maxChange) * 100)
                    const isHigh = s.avgChange >= maxChange * 0.65
                    const barColor = isHigh ? 'var(--uui-critical-60)' : 'var(--uui-warning-60)'
                    return (
                      <div key={s.sector} style={{
                        display: 'grid', gridTemplateColumns: '148px 1fr 72px 76px',
                        padding: '10px 14px', alignItems: 'center',
                        borderBottom: idx < sorted.length - 1 ? '1px solid var(--uui-neutral-60)' : 'none',
                        background: isHigh ? 'rgba(239,68,68,0.03)' : 'transparent',
                      }}>
                        {/* Sector name */}
                        <div style={{ fontSize: '12px', color: 'var(--uui-text-secondary)', fontWeight: isHigh ? 600 : 400, paddingRight: '8px', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                          {s.sector}
                        </div>

                        {/* Bar + score delta value */}
                        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', paddingRight: '8px' }}>
                          <div style={{ flex: 1, height: '14px', background: 'var(--uui-neutral-60)', borderRadius: '2px', overflow: 'hidden' }}>
                            <div style={{ width: `${barPct}%`, height: '100%', background: barColor, opacity: 0.7, borderRadius: '2px' }} />
                          </div>
                          <div style={{ fontSize: '11px', fontWeight: 700, fontFamily: 'var(--uui-font-mono)', color: barColor, width: '34px', textAlign: 'right', flexShrink: 0 }}>
                            +{s.avgChange}
                          </div>
                        </div>

                        {/* New critical */}
                        <div style={{ fontSize: '12px', fontFamily: 'var(--uui-font-mono)', fontWeight: (s.newCritical ?? 0) > 0 ? 700 : 400, color: (s.newCritical ?? 0) > 0 ? 'var(--uui-critical-60)' : 'var(--uui-text-tertiary)', textAlign: 'right' }}>
                          {(s.newCritical ?? 0) > 0 ? `+${s.newCritical}` : '—'}
                        </div>

                        {/* Estimated loss */}
                        <div style={{ fontSize: '11px', fontFamily: 'var(--uui-font-mono)', color: 'var(--uui-text-secondary)', textAlign: 'right' }}>
                          {fmtGbp(s.estimatedLoss ?? 0)}
                        </div>
                      </div>
                    )
                  })}
                </div>
              </section>
            )
          })()}

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