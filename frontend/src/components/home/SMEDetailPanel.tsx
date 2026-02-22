import { useState, useEffect } from 'react'
import { AlertCircle, TrendingUp, TrendingDown, Minus, Loader } from 'lucide-react'
import { useSelector, useDispatch } from 'react-redux'
import { RootState } from '@/store'
import { setActiveTab } from '@/store/uiSlice'
import { addTask } from '@/store/tasksSlice'
import { addScenario } from '@/store/scenariosSlice'
import { Badge } from '../common/Badge'
import { Button } from '../common/Button'
import { portfolioAPI } from '@/services/api'

const SMEDetailPanel = () => {
  const dispatch = useDispatch()
  const selectedSME = useSelector((state: RootState) => state.portfolio.selectedSME)

  const [smeDetail, setSmeDetail] = useState<any>(null)
  const [isLoading, setIsLoading] = useState(false)

  useEffect(() => {
    if (!selectedSME) return
    setIsLoading(true)
    setSmeDetail(null)
    portfolioAPI.getSMEById(selectedSME.id)
      .then(setSmeDetail)
      .catch(console.error)
      .finally(() => setIsLoading(false))
  }, [selectedSME?.id])

  if (!selectedSME) {
    return (
      <div style={{
        background: 'var(--uui-surface-main)',
        border: '1px solid var(--uui-neutral-60)',
        borderRadius: 'var(--uui-border-radius)',
        height: 'calc(100vh - 320px)',
        display: 'flex', alignItems: 'center', justifyContent: 'center'
      }}>
        <div style={{ textAlign: 'center' }}>
          <div style={{ fontSize: '48px', marginBottom: '16px' }}>📊</div>
          <p style={{ fontSize: '16px', fontWeight: 600, color: 'var(--uui-text-secondary)' }}>
            Select an SME to view details
          </p>
          <p style={{ fontSize: '13px', marginTop: '8px', color: 'var(--uui-text-tertiary)' }}>
            Click on any SME from the list to see comprehensive analysis
          </p>
        </div>
      </div>
    )
  }

  const getRiskBadgeVariant = (category: string) => {
    switch (category) {
      case 'critical': return 'critical'
      case 'medium': return 'warning'
      case 'stable': return 'success'
      default: return 'info'
    }
  }

  const getTrendIcon = (trend: string) => {
    switch (trend) {
      case 'up': return <TrendingUp size={16} style={{ color: 'var(--uui-critical-60)' }} />
      case 'down': return <TrendingDown size={16} style={{ color: 'var(--uui-success-60)' }} />
      default: return <Minus size={16} style={{ color: 'var(--uui-text-tertiary)' }} />
    }
  }

  const getTrendColor = (trend: string) => {
    switch (trend) {
      case 'up': return 'var(--uui-critical-60)'
      case 'down': return 'var(--uui-success-60)'
      default: return 'var(--uui-text-tertiary)'
    }
  }

  const formatCurrency = (value: number) => {
    if (!value) return 'N/A'
    if (value >= 1_000_000) return `€${(value / 1_000_000).toFixed(1)}M`
    if (value >= 1_000) return `€${(value / 1_000).toFixed(0)}K`
    return `€${value}`
  }

  const getExternalVariant = (value: string): any => {
    if (!value) return 'info'
    const v = value.toLowerCase()
    if (v.includes('high') || v.includes('critical') || v.includes('poor')) return 'critical'
    if (v.includes('medium') || v.includes('moderate')) return 'warning'
    return 'success'
  }

  const sectionTitle = (text: string, icon?: React.ReactNode) => (
    <div style={{
      display: 'flex', alignItems: 'center', gap: '6px',
      fontSize: '12px', fontWeight: 600,
      color: 'var(--uui-text-tertiary)',
      textTransform: 'uppercase' as const,
      marginBottom: '9px',
    }}>
      {icon}
      {text}
    </div>
  )

  const infoBox = (label: string, value: string) => (
    <div style={{
      padding: '9px 12px',
      background: 'var(--uui-neutral-70)',
      borderRadius: 'var(--uui-border-radius)',
    }}>
      <div style={{ fontSize: '10px', color: 'var(--uui-text-tertiary)', textTransform: 'uppercase', marginBottom: '3px' }}>
        {label}
      </div>
      <div style={{ fontSize: '14px', fontWeight: 600, color: 'var(--uui-text-primary)' }}>
        {value}
      </div>
    </div>
  )

  // Derived from API response with safe fallbacks
  const riskDrivers = smeDetail?.risk_drivers ?? []
  const financials = smeDetail?.details ?? {}
  const externalFactors = smeDetail?.external_factors ?? {}
  const trendDirection = smeDetail?.trend?.direction ?? selectedSME.trend
  const trendValue = smeDetail?.trend?.value ?? selectedSME.trendValue

  // ── Rating overlay — pulled from enriched SME (via mapSMEResponse) ───────
  const indicativeGrade = selectedSME.indicativeGrade ?? smeDetail?.indicative_grade ?? '—'
  const bankRating = selectedSME.bankRating ?? smeDetail?.bank_rating ?? '—'
  const ratingGapNotches = selectedSME.ratingGapNotches ?? smeDetail?.rating_gap_notches ?? 0
  const bankRatingStale = ratingGapNotches >= 2

  // ── PD overlay ────────────────────────────────────────────────────────────
  const pdOriginal = selectedSME.pdOriginal ?? smeDetail?.pd_original ?? null
  const pdAdjusted = selectedSME.pdAdjusted ?? smeDetail?.pd_adjusted ?? null
  const pdDelta = (pdOriginal !== null && pdAdjusted !== null)
    ? Math.round((pdAdjusted - pdOriginal) * 10) / 10
    : null
  const activeSignalCount = (selectedSME.activeSignals ?? []).length ||
    (smeDetail?.active_signals ?? []).length

  const handleCreateTask = () => {
    dispatch(addTask({
      id: `task_${Date.now()}`,
      title: `Review ${selectedSME.name} — Risk Score ${selectedSME.riskScore}`,
      smeId: selectedSME.id,
      smeName: selectedSME.name,
      exposure: selectedSME.exposure,
      assignee: 'Unassigned',
      priority: selectedSME.riskCategory === 'critical' ? 'high' : 'medium',
      dueDate: new Date(Date.now() + 3 * 24 * 60 * 60 * 1000).toISOString(),
      status: 'upcoming',
      description: `Manual review triggered from SME detail panel. Current risk score: ${selectedSME.riskScore}.`,
      source: 'SME Detail Panel',
      createdAt: new Date().toISOString(),
    }))
    dispatch(setActiveTab('tasks'))
  }

  const handleRunScenario = () => {
    dispatch(addScenario({
      id: `scenario_${Date.now()}`,
      name: `${selectedSME.name} — Impact Analysis`,
      status: 'in_progress',
      progress: 0,
      createdAt: new Date().toISOString(),
    }))
    dispatch(setActiveTab('scenarios'))
  }

  return (
    <div style={{
      background: 'var(--uui-surface-main)',
      border: '1px solid var(--uui-neutral-60)',
      borderRadius: 'var(--uui-border-radius)',
      height: 'calc(100vh - 320px)',
      overflowY: 'auto',
    }}>
      {/* Sticky Header */}
      <div style={{
        position: 'sticky', top: 0, zIndex: 10,
        background: 'var(--uui-neutral-70)',
        borderBottom: '1px solid var(--uui-neutral-60)',
        padding: '12px 18px',
      }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
          {/* Left */}
          <div style={{ flex: 1 }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '6px' }}>
              <span style={{ fontSize: '11px', color: 'var(--uui-text-tertiary)', fontFamily: 'var(--uui-font-mono)' }}>
                {selectedSME.id}
              </span>
              <Badge variant={getRiskBadgeVariant(selectedSME.riskCategory) as any}>
                {selectedSME.riskCategory.toUpperCase()}
              </Badge>
            </div>
            <h2 style={{ fontSize: '18px', fontWeight: 700, color: 'var(--uui-text-primary)', marginBottom: '6px' }}>
              {selectedSME.name}
            </h2>
            <div style={{ display: 'flex', alignItems: 'center', gap: '16px', fontSize: '13px', color: 'var(--uui-text-secondary)' }}>
              <span>💼 {selectedSME.sector}</span>
              <span>📍 {selectedSME.geography}</span>
              <span style={{ fontFamily: 'var(--uui-font-mono)', fontWeight: 600 }}>{selectedSME.exposure}</span>
            </div>
          </div>

          {/* Right - Score */}
          <div style={{ textAlign: 'right' }}>
            <div style={{ fontSize: '36px', fontWeight: 700, fontFamily: 'var(--uui-font-mono)', color: 'var(--uui-text-primary)' }}>
              {selectedSME.riskScore}
            </div>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'flex-end', gap: '4px', marginTop: '4px' }}>
              {getTrendIcon(trendDirection)}
              <span style={{ fontSize: '12px', fontFamily: 'var(--uui-font-mono)', fontWeight: 600, color: getTrendColor(trendDirection) }}>
                {trendValue > 0 ? '+' : ''}{trendValue} this quarter
              </span>
            </div>
          </div>
        </div>

        {/* ── Three-field rating row ──────────────────────────────────────────
            Live Score (our real-time) | Indicative Grade | Bank Rating (static)
            The gap between Indicative and Bank Rating is the core value prop —
            our signals have moved ahead of the bank's quarterly update cycle. */}
        <div style={{
          display: 'grid', gridTemplateColumns: '1fr 1fr 1fr',
          gap: '1px',
          marginTop: '12px',
          background: 'var(--uui-neutral-60)',   // gap colour
          borderRadius: 'var(--uui-border-radius)',
          overflow: 'hidden',
        }}>
          {/* Live Score */}
          <div style={{
            padding: '10px 12px',
            background: 'var(--uui-neutral-80)',
            textAlign: 'center',
          }}>
            <div style={{ fontSize: '10px', fontWeight: 600, color: 'var(--uui-text-tertiary)', textTransform: 'uppercase', marginBottom: '4px', letterSpacing: '0.5px' }}>
              Live Score
            </div>
            <div style={{ fontSize: '22px', fontWeight: 700, fontFamily: 'var(--uui-font-mono)', color: 'var(--uui-text-primary)' }}>
              {selectedSME.riskScore}
            </div>
            <div style={{ fontSize: '10px', color: 'var(--uui-text-tertiary)', marginTop: '2px' }}>
              real-time
            </div>
          </div>

          {/* Indicative Grade — our signal-derived grade */}
          <div style={{
            padding: '10px 12px',
            background: 'var(--uui-neutral-80)',
            textAlign: 'center',
            borderLeft: bankRatingStale ? '2px solid var(--uui-warning-60)' : 'none',
          }}>
            <div style={{ fontSize: '10px', fontWeight: 600, color: 'var(--uui-text-tertiary)', textTransform: 'uppercase', marginBottom: '4px', letterSpacing: '0.5px' }}>
              Indicative Grade
            </div>
            <div style={{
              fontSize: '22px', fontWeight: 700, fontFamily: 'var(--uui-font-mono)',
              color: bankRatingStale ? 'var(--uui-warning-60)' : 'var(--uui-text-primary)',
            }}>
              {indicativeGrade}
            </div>
            <div style={{ fontSize: '10px', color: 'var(--uui-text-tertiary)', marginTop: '2px' }}>
              our signals
            </div>
          </div>

          {/* Bank Rating — official quarterly rating */}
          <div style={{
            padding: '10px 12px',
            background: 'var(--uui-neutral-80)',
            textAlign: 'center',
          }}>
            <div style={{ fontSize: '10px', fontWeight: 600, color: 'var(--uui-text-tertiary)', textTransform: 'uppercase', marginBottom: '4px', letterSpacing: '0.5px' }}>
              Bank Rating
            </div>
            <div style={{ fontSize: '22px', fontWeight: 700, fontFamily: 'var(--uui-font-mono)', color: 'var(--uui-text-secondary)' }}>
              {bankRating}
            </div>
            <div style={{ fontSize: '10px', color: 'var(--uui-text-tertiary)', marginTop: '2px' }}>
              last quarterly
            </div>
          </div>
        </div>

        {/* ── Stale rating warning banner ─────────────────────────────────────
            Only shown when ratingGapNotches >= 2.
            This is the "wow moment" Sandro described — our live grade has
            deteriorated significantly ahead of the bank's official update. */}
        {bankRatingStale && (
          <div style={{
            display: 'flex', alignItems: 'flex-start', gap: '8px',
            marginTop: '8px',
            padding: '9px 12px',
            background: 'rgba(var(--uui-warning-rgb, 245, 158, 11), 0.12)',
            border: '1px solid var(--uui-warning-60)',
            borderRadius: 'var(--uui-border-radius)',
          }}>
            <span style={{ fontSize: '14px', flexShrink: 0, marginTop: '1px' }}>⚠️</span>
            <div>
              <span style={{ fontSize: '12px', fontWeight: 700, color: 'var(--uui-warning-60)' }}>
                {ratingGapNotches}-notch deterioration detected
              </span>
              <span style={{ fontSize: '12px', color: 'var(--uui-text-secondary)', marginLeft: '6px' }}>
                — bank rating ({bankRating}) may not reflect current risk signals. Our indicative grade: {indicativeGrade}.
              </span>
            </div>
          </div>
        )}
      </div>

      {/* Loading */}
      {isLoading && (
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', padding: '48px', gap: '12px' }}>
          <Loader size={20} style={{ animation: 'spin 1s linear infinite', color: 'var(--uui-primary-60)' }} />
          <span style={{ fontSize: '13px', color: 'var(--uui-text-tertiary)' }}>Loading SME details...</span>
        </div>
      )}

      {/* Content */}
      {!isLoading && (
        <div style={{ padding: '18px', display: 'flex', flexDirection: 'column', gap: '18px' }}>

          {/* ── PD Row — Original PD vs Signal-Adjusted PD ──────────────────────
              Shows the bank's static PD alongside our overlay-adjusted PD.
              The delta with signal count is the quantified version of the
              stale rating gap narrative. Only rendered when PD data is present. */}
          {pdOriginal !== null && pdAdjusted !== null && (
            <section>
              {sectionTitle('Probability of Default')}
              <div style={{
                padding: '12px 14px',
                background: 'var(--uui-neutral-70)',
                borderRadius: 'var(--uui-border-radius)',
                borderLeft: pdDelta !== null && pdDelta > 2
                  ? '3px solid var(--uui-critical-60)'
                  : '3px solid var(--uui-neutral-50)',
              }}>
                {/* PD before → after row */}
                <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '8px' }}>
                  {/* Bank's static PD */}
                  <div style={{ textAlign: 'center', minWidth: '64px' }}>
                    <div style={{ fontSize: '10px', color: 'var(--uui-text-tertiary)', textTransform: 'uppercase', marginBottom: '2px' }}>
                      Bank PD
                    </div>
                    <div style={{ fontSize: '20px', fontWeight: 700, fontFamily: 'var(--uui-font-mono)', color: 'var(--uui-text-secondary)' }}>
                      {pdOriginal}%
                    </div>
                  </div>

                  {/* Arrow */}
                  <div style={{ color: 'var(--uui-text-tertiary)', fontSize: '18px', lineHeight: 1 }}>→</div>

                  {/* Our adjusted PD */}
                  <div style={{ textAlign: 'center', minWidth: '64px' }}>
                    <div style={{ fontSize: '10px', color: 'var(--uui-text-tertiary)', textTransform: 'uppercase', marginBottom: '2px' }}>
                      Signal PD
                    </div>
                    <div style={{
                      fontSize: '20px', fontWeight: 700, fontFamily: 'var(--uui-font-mono)',
                      color: pdDelta !== null && pdDelta > 0 ? 'var(--uui-critical-60)' : 'var(--uui-success-60)',
                    }}>
                      {pdAdjusted}%
                    </div>
                  </div>

                  {/* Delta badge */}
                  {pdDelta !== null && (
                    <div style={{
                      marginLeft: 'auto',
                      padding: '4px 10px',
                      borderRadius: '999px',
                      background: pdDelta > 0
                        ? 'rgba(var(--uui-critical-rgb, 239, 68, 68), 0.15)'
                        : 'rgba(var(--uui-success-rgb, 34, 197, 94), 0.15)',
                      fontSize: '13px', fontWeight: 700, fontFamily: 'var(--uui-font-mono)',
                      color: pdDelta > 0 ? 'var(--uui-critical-60)' : 'var(--uui-success-60)',
                    }}>
                      {pdDelta > 0 ? '+' : ''}{pdDelta}pp
                    </div>
                  )}
                </div>

                {/* Narrative line */}
                <div style={{
                  fontSize: '12px',
                  color: 'var(--uui-text-tertiary)',
                  lineHeight: 1.5,
                  paddingTop: '8px',
                  borderTop: '1px solid var(--uui-neutral-60)',
                }}>
                  {pdDelta !== null && pdDelta > 0
                    ? `PD moved ${pdOriginal}% → ${pdAdjusted}% due to ${activeSignalCount > 0 ? activeSignalCount : ''} live signal${activeSignalCount !== 1 ? 's' : ''}. Bank's quarterly model not yet updated.`
                    : `PD unchanged from bank model — no material signal uplift detected.`
                  }
                </div>
              </div>
            </section>
          )}

          {/* Risk Drivers */}
          <section>
            {sectionTitle('Key Risk Drivers', <AlertCircle size={14} />)}
            {riskDrivers.length > 0 ? (
              <div style={{ display: 'flex', flexDirection: 'column', gap: '9px' }}>
                {riskDrivers.map((driver: any, idx: number) => {
                  const isNegative = (driver.direction ?? 'increase') === 'increase'
                  const accentColor = isNegative ? 'var(--uui-critical-60)' : 'var(--uui-success-60)'
                  return (
                    <div key={idx} style={{
                      display: 'flex', alignItems: 'center', justifyContent: 'space-between',
                      padding: '12px',
                      background: 'var(--uui-neutral-70)',
                      borderRadius: 'var(--uui-border-radius)',
                      borderLeft: `3px solid ${accentColor}`,
                    }}>
                      <div style={{ flex: 1 }}>
                        <div style={{ fontSize: '13px', fontWeight: 600, color: 'var(--uui-text-primary)', marginBottom: '3px' }}>
                          {driver.factor ?? driver.label}
                        </div>
                        <div style={{ fontSize: '11px', color: 'var(--uui-text-tertiary)' }}>
                          Source: {driver.source}
                        </div>
                      </div>
                      <div style={{ textAlign: 'right' }}>
                        <div style={{ fontSize: '18px', fontWeight: 700, color: accentColor }}>
                          {isNegative ? '+' : '-'}{Math.abs(driver.impact ?? 0)}
                        </div>
                        <div style={{ fontSize: '11px', color: 'var(--uui-text-tertiary)' }}>points</div>
                      </div>
                    </div>
                  )
                })}
              </div>
            ) : (
              <div style={{ padding: '18px', textAlign: 'center', color: 'var(--uui-text-tertiary)', fontSize: '13px', background: 'var(--uui-neutral-70)', borderRadius: 'var(--uui-border-radius)' }}>
                No risk drivers available
              </div>
            )}
          </section>

          {/* Financial Metrics */}
          <section>
            {sectionTitle('Financial Metrics')}
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px' }}>
              {infoBox('Annual Revenue', formatCurrency(financials.revenue))}
              {infoBox('EBITDA', formatCurrency(financials.ebitda))}
              {infoBox('Debt Service Coverage', financials.debt_service_coverage ? `${financials.debt_service_coverage.toFixed(2)}x` : 'N/A')}
              {infoBox('Cash Reserves', formatCurrency(financials.cash_reserves))}
            </div>
          </section>

          {/* External Risk Factors */}
          <section>
            {sectionTitle('External Risk Factors')}
            <div style={{ display: 'flex', flexDirection: 'column', gap: '9px' }}>
              {[
                { label: 'Sector Health', value: externalFactors.sector_health ?? externalFactors.sectorHealth ?? '—' },
                { label: 'Geography Risk', value: externalFactors.geography_risk ?? externalFactors.geographyRisk ?? '—' },
                { label: 'Compliance Status', value: externalFactors.compliance_status ?? externalFactors.compliance ?? '—' },
              ].map((item, idx) => (
                <div key={idx} style={{
                  display: 'flex', alignItems: 'center', justifyContent: 'space-between',
                  padding: '9px 12px',
                  background: 'var(--uui-neutral-70)',
                  borderRadius: 'var(--uui-border-radius)',
                }}>
                  <span style={{ fontSize: '13px', color: 'var(--uui-text-secondary)' }}>{item.label}</span>
                  <Badge variant={getExternalVariant(item.value)}>{item.value}</Badge>
                </div>
              ))}
            </div>
          </section>

          {/* Actions */}
          <section style={{ paddingTop: '12px', borderTop: '1px solid var(--uui-neutral-60)' }}>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '9px' }}>
              <Button variant="primary" size="md" onClick={handleCreateTask}>Create Task</Button>
              <Button variant="secondary" size="md" onClick={handleRunScenario}>Run Scenario</Button>
              <div style={{ gridColumn: '1 / -1' }}>
                <Button variant="secondary" size="md" fullWidth>View Full History</Button>
              </div>
            </div>
          </section>

        </div>
      )}
    </div>
  )
}

export default SMEDetailPanel