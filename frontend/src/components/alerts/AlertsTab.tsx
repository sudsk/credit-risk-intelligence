import { AlertCircle, Bell, Clock, Loader, RefreshCw, ChevronDown, ChevronUp, Users } from 'lucide-react'
import { useState, useEffect } from 'react'
import { useDispatch } from 'react-redux'
import { setActiveTab } from '@/store/uiSlice'
import { setSelectedSME } from '@/store/portfolioSlice'
import { addScenario } from '@/store/scenariosSlice'
import { addTask } from '@/store/tasksSlice'
import { Button } from '../common/Button'
import { Card, CardHeader, CardTitle, CardContent } from '../common/Card'
import { Badge } from '../common/Badge'
import { formatRelativeTime } from '@/utils/formatters'
import { alertAPI, portfolioAPI } from '@/services/api'
import type { Alert, SME } from '@/services/types'

// ── Credit officer roster ─────────────────────────────────────────────────────
// Kept here so it's easy to swap in a real API call later
const CREDIT_OFFICERS = [
  { value: 'john.smith', label: 'John Smith' },
  { value: 'jane.doe', label: 'Jane Doe' },
  { value: 'sarah.chen', label: 'Sarah Chen' },
  { value: 'mike.wilson', label: 'Mike Wilson' },
  { value: 'priya.sharma', label: 'Priya Sharma' },
]

// Alert scope labels used in the meta row
const SCOPE_META: Record<string, (a: Alert) => string> = {
  sme: (a) => `${a.smeId}  ${a.smeName}`,
  sector: (a) => `🏭 Sector · ${a.smeName} · ${a.affected_count} SMEs affected`,
  geography: (a) => `📍 Geography · ${a.smeName} · ${a.affected_count} SMEs affected`,
  macro: (a) => `🌐 Macro · Portfolio-wide · ${a.affected_count} SMEs affected`,
}

// ── Types ──────────────────────────────────────────────────────────────────────

interface TaskDraft {
  assignee: string
  priority: 'high' | 'medium' | 'low'
}

interface AffectedSMERow {
  sme: SME
  // estimated score delta from the alert's sector/macro context
  estimatedImpact: number
  agentAnalysis: string | null
  isAnalysing: boolean
}

// ── Helper — build task description from alert ────────────────────────────────
// Pre-populates with signal summary, recommended action, severity and exposure
// so the credit officer has full context without opening the alert again.
function buildTaskDescription(alert: Alert): string {
  const lines: string[] = [
    `Alert: ${alert.title}`,
    `Severity: ${alert.severity.toUpperCase()} | Exposure: ${alert.exposure}`,
    '',
    `Summary: ${alert.summary}`,
  ]
  if (alert.signals.length > 0) {
    lines.push('', 'Signals detected:')
    alert.signals.forEach(s => lines.push(`  • ${s.source}: ${s.detail}`))
  }
  if (alert.recommendation) {
    lines.push('', `Recommended action: ${alert.recommendation}`)
  }
  return lines.join('\n')
}

// ── Subcomponent — Affected SME list for industry-wide alerts ────────────────
// Shown when scope is sector, geography or macro.
// Loads SMEs from portfolio, filters to match alert's sector/geography,
// adds estimated impact preview, then lets user trigger per-SME agent analysis.

interface AffectedSMEListProps {
  alert: Alert
  accentColor: string
}

const AffectedSMEList = ({ alert, accentColor }: AffectedSMEListProps) => {
  const dispatch = useDispatch()
  const [rows, setRows] = useState<AffectedSMERow[]>([])
  const [isLoading, setIsLoading] = useState(false)
  const [analysedAll, setAnalysedAll] = useState(false)
  const [isAnalysingAll, setIsAnalysingAll] = useState(false)
  const [showAll, setShowAll] = useState(false)

  // Load and filter portfolio SMEs relevant to this alert
  useEffect(() => {
    setIsLoading(true)
    portfolioAPI.getSMEs()
      .then(smes => {
        // Filter: sector alerts match by sector, geography by geography, macro = all
        const filtered = smes.filter(s => {
          if (alert.scope === 'sector') return s.sector.toLowerCase().includes(alert.smeName.toLowerCase()) || alert.smeName.toLowerCase().includes(s.sector.toLowerCase())
          if (alert.scope === 'geography') return s.geography.toLowerCase().includes(alert.smeName.toLowerCase())
          return true // macro — all SMEs
        })

        // Sort by risk score desc — highest risk first
        const sorted = filtered
          .sort((a, b) => b.riskScore - a.riskScore)
          .slice(0, alert.scope === 'macro' ? 20 : 50)

        setRows(sorted.map(sme => ({
          sme,
          // Deterministic estimated impact based on sector sensitivity + severity
          estimatedImpact: Math.round(
            (alert.severity === 'critical' ? 8 : 4) *
            (sme.riskCategory === 'critical' ? 1.5 : sme.riskCategory === 'medium' ? 1.1 : 0.7)
          ),
          agentAnalysis: null,
          isAnalysing: false,
        })))
      })
      .catch(console.error)
      .finally(() => setIsLoading(false))
  }, [alert.id])

  // Simulate per-SME agent analysis — in production this calls the SME agent
  const analyseOne = async (idx: number) => {
    setRows(prev => prev.map((r, i) => i === idx ? { ...r, isAnalysing: true } : r))
    await new Promise(res => setTimeout(res, 900 + Math.random() * 600))
    const sme = rows[idx].sme
    const impact = rows[idx].estimatedImpact
    const analysis = [
      `Risk score estimated to increase by +${impact}pts based on ${alert.scope} signal.`,
      sme.riskCategory === 'critical'
        ? `Already critical — expedite credit review.`
        : sme.riskCategory === 'medium'
          ? `Approaching critical threshold. Monitor closely.`
          : `Currently stable — monitor for secondary effects.`,
      alert.recommendation
        ? `Recommended action: ${alert.recommendation}`
        : `Review latest financials and covenant compliance.`,
    ].join(' ')
    setRows(prev => prev.map((r, i) => i === idx ? { ...r, isAnalysing: false, agentAnalysis: analysis } : r))
  }

  const analyseAll = async () => {
    setIsAnalysingAll(true)
    for (let i = 0; i < Math.min(rows.length, 10); i++) {
      if (!rows[i].agentAnalysis) await analyseOne(i)
    }
    setIsAnalysedAll(true)
    setIsAnalysingAll(false)
  }

  // helper to avoid closure issue
  const setIsAnalysedAll = setAnalysedAll

  const visibleRows = showAll ? rows : rows.slice(0, 5)

  if (isLoading) {
    return (
      <div style={{ display: 'flex', alignItems: 'center', gap: '8px', padding: '12px', fontSize: '12px', color: 'var(--uui-text-tertiary)' }}>
        <Loader size={13} style={{ animation: 'spin 1s linear infinite' }} />
        Loading affected SMEs...
      </div>
    )
  }

  if (rows.length === 0) {
    return (
      <div style={{ padding: '12px', fontSize: '12px', color: 'var(--uui-text-tertiary)' }}>
        No matching SMEs found in portfolio.
      </div>
    )
  }

  return (
    <div>
      {/* Header row */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '10px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <Users size={13} style={{ color: 'var(--uui-text-tertiary)' }} />
          <span style={{ fontSize: '11px', fontWeight: 600, color: 'var(--uui-text-tertiary)', textTransform: 'uppercase' }}>
            {rows.length} Affected SME{rows.length !== 1 ? 's' : ''} — Impact Preview
          </span>
        </div>
        <Button
          variant="secondary" size="sm"
          onClick={analyseAll}
          disabled={isAnalysingAll || analysedAll}
        >
          {isAnalysingAll
            ? <><Loader size={11} style={{ animation: 'spin 1s linear infinite' }} /> Analysing...</>
            : analysedAll
              ? '✓ Analysis Complete'
              : '🤖 Analyse All'}
        </Button>
      </div>

      {/* Column headers */}
      <div style={{
        display: 'grid', gridTemplateColumns: '180px 80px 60px 1fr 80px',
        padding: '6px 10px',
        background: 'var(--uui-neutral-80)',
        borderRadius: 'var(--uui-border-radius) var(--uui-border-radius) 0 0',
        borderBottom: '1px solid var(--uui-neutral-60)',
      }}>
        {['SME', 'Score', 'Est. Δ', 'Agent Analysis', ''].map((h, i) => (
          <div key={i} style={{ fontSize: '10px', fontWeight: 600, color: 'var(--uui-text-tertiary)', textTransform: 'uppercase', textAlign: i === 2 ? 'center' : 'left' }}>
            {h}
          </div>
        ))}
      </div>

      {/* SME rows */}
      <div style={{ border: '1px solid var(--uui-neutral-60)', borderTop: 'none', borderRadius: '0 0 var(--uui-border-radius) var(--uui-border-radius)', overflow: 'hidden' }}>
        {visibleRows.map((row, idx) => {
          const { sme, estimatedImpact, agentAnalysis, isAnalysing } = row
          const categoryColor = sme.riskCategory === 'critical' ? 'var(--uui-critical-60)' : sme.riskCategory === 'medium' ? 'var(--uui-warning-60)' : 'var(--uui-success-60)'
          return (
            <div
              key={sme.id}
              style={{
                display: 'grid', gridTemplateColumns: '180px 80px 60px 1fr 80px',
                padding: '9px 10px', alignItems: 'flex-start',
                borderBottom: idx < visibleRows.length - 1 ? '1px solid var(--uui-neutral-60)' : 'none',
                background: sme.riskCategory === 'critical' ? 'rgba(239,68,68,0.03)' : 'transparent',
              }}
            >
              {/* SME name */}
              <div>
                <div style={{ fontSize: '12px', fontWeight: 600, color: 'var(--uui-text-primary)', marginBottom: '2px', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                  {sme.name}
                </div>
                <div style={{ fontSize: '10px', color: 'var(--uui-text-tertiary)', fontFamily: 'var(--uui-font-mono)' }}>
                  {sme.id}
                </div>
              </div>

              {/* Risk score */}
              <div style={{ display: 'flex', alignItems: 'center', gap: '5px' }}>
                <span style={{ fontSize: '14px', fontWeight: 700, fontFamily: 'var(--uui-font-mono)', color: categoryColor }}>
                  {sme.riskScore}
                </span>
                <span style={{ fontSize: '9px', color: 'var(--uui-text-tertiary)', textTransform: 'uppercase' }}>
                  {sme.riskCategory}
                </span>
              </div>

              {/* Estimated delta */}
              <div style={{ textAlign: 'center' }}>
                <span style={{
                  fontSize: '12px', fontWeight: 700, fontFamily: 'var(--uui-font-mono)',
                  color: estimatedImpact > 0 ? accentColor : 'var(--uui-success-60)',
                  padding: '2px 5px',
                  background: estimatedImpact > 0 ? `${accentColor}18` : 'rgba(34,197,94,0.1)',
                  borderRadius: '3px',
                }}>
                  +{estimatedImpact}
                </span>
              </div>

              {/* Agent analysis */}
              <div style={{ paddingRight: '8px' }}>
                {isAnalysing && (
                  <div style={{ display: 'flex', alignItems: 'center', gap: '5px', fontSize: '11px', color: 'var(--uui-text-tertiary)' }}>
                    <Loader size={11} style={{ animation: 'spin 1s linear infinite' }} />
                    Analysing...
                  </div>
                )}
                {agentAnalysis && !isAnalysing && (
                  <p style={{ fontSize: '11px', color: 'var(--uui-text-secondary)', lineHeight: 1.5, margin: 0 }}>
                    {agentAnalysis}
                  </p>
                )}
                {!agentAnalysis && !isAnalysing && (
                  <span style={{ fontSize: '11px', color: 'var(--uui-text-tertiary)', fontStyle: 'italic' }}>—</span>
                )}
              </div>

              {/* Drill-down button */}
              <div>
                <button
                  onClick={() => analyseOne(idx)}
                  disabled={isAnalysing || !!agentAnalysis}
                  style={{
                    fontSize: '11px', fontWeight: 600,
                    padding: '3px 8px', borderRadius: 'var(--uui-border-radius)',
                    border: `1px solid var(--uui-neutral-50)`,
                    background: 'transparent',
                    color: isAnalysing || agentAnalysis ? 'var(--uui-text-tertiary)' : 'var(--uui-text-secondary)',
                    cursor: isAnalysing || agentAnalysis ? 'default' : 'pointer',
                    fontFamily: 'var(--uui-font)',
                    whiteSpace: 'nowrap' as const,
                  }}
                >
                  {isAnalysing ? '...' : agentAnalysis ? '✓' : 'Analyse'}
                </button>
              </div>
            </div>
          )
        })}
      </div>

      {/* Show more / less toggle */}
      {rows.length > 5 && (
        <button
          onClick={() => setShowAll(v => !v)}
          style={{
            width: '100%', marginTop: '6px', padding: '7px',
            fontSize: '11px', fontWeight: 600, color: 'var(--uui-text-tertiary)',
            background: 'transparent', border: '1px solid var(--uui-neutral-60)',
            borderRadius: 'var(--uui-border-radius)', cursor: 'pointer',
            display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '5px',
            fontFamily: 'var(--uui-font)',
          }}
        >
          {showAll
            ? <><ChevronUp size={12} /> Show fewer</>
            : <><ChevronDown size={12} /> Show all {rows.length} SMEs</>}
        </button>
      )}
    </div>
  )
}


// ── Main component ─────────────────────────────────────────────────────────────

const AlertsTab = () => {
  const dispatch = useDispatch()
  const [alerts, setAlerts] = useState<Alert[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [isSimulating, setIsSimulating] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [expandedId, setExpandedId] = useState<string | null>(null)
  const [affectedOpenId, setAffectedOpenId] = useState<string | null>(null)

  // Per-alert task draft state — persists while panel is open
  const [taskDrafts, setTaskDrafts] = useState<Record<string, TaskDraft>>({})

  const patchDraft = (alertId: string, patch: Partial<TaskDraft>) =>
    setTaskDrafts(prev => ({
      ...prev,
      [alertId]: { assignee: '', priority: 'medium', ...prev[alertId], ...patch },
    }))

  const getDraft = (alertId: string): TaskDraft =>
    taskDrafts[alertId] ?? { assignee: '', priority: 'medium' }

  const loadAlerts = () => {
    setIsLoading(true)
    setError(null)
    alertAPI.getAlertHistory()
      .then(items => setAlerts(items.sort((a, b) => new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime())))
      .catch(err => setError(err.message || 'Failed to load alerts'))
      .finally(() => setIsLoading(false))
  }

  useEffect(() => { loadAlerts() }, [])

  const handleSimulate = async () => {
    setIsSimulating(true)
    try {
      const newAlert = await alertAPI.simulateFeed()
      setAlerts(prev => [newAlert, ...prev])
    } catch (err: any) {
      setError(err.message || 'Simulation failed')
    } finally {
      setIsSimulating(false)
    }
  }

  const handleRunScenario = (alert: Alert) => {
    dispatch(addScenario({
      id: `scenario_${Date.now()}`,
      name: `${alert.smeName} — ${alert.title}`,
      status: 'in_progress',
      progress: 0,
      createdAt: new Date().toISOString(),
    }))
    dispatch(setActiveTab('scenarios'))
  }

  // ── Fully-wired task creation ─────────────────────────────────────────────
  // Pre-populates title, description, priority, and assignee from alert data.
  // Description includes signal summary + recommended action so the credit
  // officer has full context without reopening the alert.
  const handleCreateTask = (alert: Alert) => {
    const draft = getDraft(alert.id)
    const priority = alert.severity === 'critical' ? 'high' : draft.priority

    dispatch(addTask({
      id: `task_${Date.now()}`,
      title: `Follow up: ${alert.smeName} — ${alert.title}`,
      smeId: alert.smeId,
      smeName: alert.smeName,
      exposure: alert.exposure,
      assignee: draft.assignee || 'Unassigned',
      priority,
      dueDate: new Date(
        Date.now() + (priority === 'high' ? 1 : priority === 'medium' ? 3 : 7) * 24 * 60 * 60 * 1000
      ).toISOString(),
      status: 'upcoming',
      description: buildTaskDescription(alert),
      source: `Alert · ${alert.severity.toUpperCase()} · ${formatRelativeTime(alert.timestamp)}`,
      createdAt: new Date().toISOString(),
    }))
    dispatch(setActiveTab('tasks'))
  }

  const handleViewSME = (alert: Alert) => {
    dispatch(setSelectedSME({
      id: alert.smeId,
      name: alert.smeName,
      riskScore: 68,
      riskCategory: 'critical',
      exposure: alert.exposure,
      sector: 'Software/Technology',
      geography: 'UK',
      trend: 'up',
      trendValue: 14,
    } as any))
    dispatch(setActiveTab('home'))
  }

  const selectStyle: React.CSSProperties = {
    width: '100%', padding: '6px 9px', fontSize: '12px',
    background: 'var(--uui-neutral-80)',
    border: '1px solid var(--uui-neutral-60)',
    borderRadius: 'var(--uui-border-radius)',
    color: 'var(--uui-text-primary)',
    fontFamily: 'var(--uui-font)',
    outline: 'none',
  }

  const criticalCount = alerts.filter(a => a.severity === 'critical').length

  return (
    <Card style={{ height: 'calc(100vh - 200px)', display: 'flex', flexDirection: 'column' }}>
      <CardHeader>
        <CardTitle>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', width: '100%' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '9px' }}>
              <Bell size={20} style={{ color: 'var(--uui-warning-60)' }} />
              <div>
                <div style={{ fontSize: '14px', fontWeight: 600, color: 'var(--uui-text-primary)' }}>
                  Alerts
                  {criticalCount > 0 && (
                    <span style={{
                      marginLeft: '8px', padding: '1px 7px',
                      background: 'var(--uui-critical-60)', color: 'white',
                      fontSize: '10px', fontWeight: 700,
                      borderRadius: '999px',
                    }}>
                      {criticalCount} CRITICAL
                    </span>
                  )}
                </div>
                <div style={{ fontSize: '11px', color: 'var(--uui-text-tertiary)', fontWeight: 400 }}>
                  AI-detected risk signals from alternative data sources
                </div>
              </div>
            </div>
            <div style={{ display: 'flex', gap: '8px' }}>
              <Button variant="secondary" size="sm" onClick={loadAlerts} title="Refresh">
                <RefreshCw size={13} />
              </Button>
              <Button variant="primary" size="sm" onClick={handleSimulate} disabled={isSimulating}>
                {isSimulating
                  ? <><Loader size={13} style={{ animation: 'spin 1s linear infinite' }} /> Detecting...</>
                  : '⚡ Simulate Live Feed'}
              </Button>
            </div>
          </div>
        </CardTitle>
      </CardHeader>

      <CardContent style={{ flex: 1, overflowY: 'auto' }}>
        {isLoading && (
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', padding: '48px', gap: '12px' }}>
            <Loader size={20} style={{ animation: 'spin 1s linear infinite', color: 'var(--uui-primary-60)' }} />
            <span style={{ fontSize: '13px', color: 'var(--uui-text-tertiary)' }}>Loading alerts...</span>
          </div>
        )}

        {error && !isLoading && (
          <div style={{ margin: '12px', padding: '12px', background: 'rgba(229,98,72,0.1)', border: '1px solid var(--uui-critical-60)', borderRadius: 'var(--uui-border-radius)' }}>
            <p style={{ fontSize: '13px', color: 'var(--uui-critical-60)' }}>⚠️ {error}</p>
          </div>
        )}

        {!isLoading && !error && (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
            {alerts.map((alert) => {
              const isCritical = alert.severity === 'critical'
              const accentColor = isCritical ? 'var(--uui-critical-60)' : 'var(--uui-warning-60)'
              const isExpanded = expandedId === alert.id
              const isIndustry = alert.scope !== 'sme'
              const affectedOpen = affectedOpenId === alert.id
              const draft = getDraft(alert.id)

              return (
                <div key={alert.id} style={{
                  background: 'var(--uui-neutral-70)',
                  border: `1px solid var(--uui-neutral-60)`,
                  borderLeft: `3px solid ${accentColor}`,
                  borderRadius: 'var(--uui-border-radius)',
                  overflow: 'hidden',
                }}>
                  <div style={{ padding: '12px' }}>

                    {/* Meta row */}
                    <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '6px' }}>
                      <span style={{ fontSize: '11px', fontFamily: 'var(--uui-font-mono)', color: 'var(--uui-text-tertiary)' }}>
                        {(SCOPE_META[alert.scope] ?? SCOPE_META.sme)(alert)}
                      </span>
                      <Badge variant={isCritical ? 'critical' : 'warning'}>
                        {alert.severity.toUpperCase()}
                      </Badge>
                    </div>

                    {/* Title */}
                    <div style={{ fontSize: '14px', fontWeight: 700, color: 'var(--uui-text-primary)', marginBottom: '6px' }}>
                      {alert.title}
                    </div>

                    {/* Time + Exposure */}
                    <div style={{ display: 'flex', alignItems: 'center', gap: '8px', fontSize: '11px', color: 'var(--uui-text-tertiary)', marginBottom: '9px' }}>
                      <Clock size={11} />
                      <span>{formatRelativeTime(alert.timestamp)}</span>
                      <span>•</span>
                      <span style={{ fontFamily: 'var(--uui-font-mono)' }}>{alert.exposure} exposure</span>
                    </div>

                    {/* Summary */}
                    <p style={{ fontSize: '13px', color: 'var(--uui-text-secondary)', marginBottom: '12px', lineHeight: 1.5 }}>
                      {alert.summary}
                    </p>

                    {/* Expanded — Signals */}
                    {isExpanded && alert.signals.length > 0 && (
                      <div style={{ marginBottom: '12px', paddingTop: '12px', borderTop: '1px solid var(--uui-neutral-60)' }}>
                        <div style={{ fontSize: '11px', fontWeight: 600, color: 'var(--uui-text-tertiary)', textTransform: 'uppercase', marginBottom: '9px' }}>
                          Data Signals
                        </div>
                        <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
                          {alert.signals.map((signal, idx) => (
                            <div key={idx} style={{ display: 'flex', alignItems: 'flex-start', gap: '8px', fontSize: '12px', background: 'var(--uui-neutral-80)', padding: '8px', borderRadius: 'var(--uui-border-radius)' }}>
                              <AlertCircle size={12} style={{ color: 'var(--uui-text-tertiary)', marginTop: '2px', flexShrink: 0 }} />
                              <div style={{ color: 'var(--uui-text-secondary)' }}>
                                <strong style={{ color: 'var(--uui-text-primary)' }}>{signal.source}:</strong> {signal.detail}
                              </div>
                            </div>
                          ))}
                        </div>
                        {alert.recommendation && (
                          <div style={{ marginTop: '9px', padding: '9px 12px', background: 'rgba(244,184,58,0.1)', border: '1px solid var(--uui-warning-60)', borderRadius: 'var(--uui-border-radius)', fontSize: '12px', color: 'var(--uui-text-secondary)' }}>
                            <strong style={{ color: 'var(--uui-warning-70)' }}>💡 Recommendation:</strong> {alert.recommendation}
                          </div>
                        )}
                      </div>
                    )}

                    {/* ── Industry-wide affected SME list ────────────────────────────────
                        Shown for sector / geography / macro alerts.
                        Toggled by "Affected SMEs" button.
                        Contains: impact preview table → per-SME or bulk agent analysis.  */}
                    {isExpanded && isIndustry && (
                      <div style={{ marginBottom: '12px', paddingTop: '12px', borderTop: '1px solid var(--uui-neutral-60)' }}>
                        {/* Toggle header */}
                        <button
                          onClick={() => setAffectedOpenId(affectedOpen ? null : alert.id)}
                          style={{
                            display: 'flex', alignItems: 'center', justifyContent: 'space-between',
                            width: '100%', padding: '9px 12px',
                            background: affectedOpen ? 'var(--uui-neutral-80)' : 'transparent',
                            border: '1px solid var(--uui-neutral-60)',
                            borderRadius: affectedOpen
                              ? 'var(--uui-border-radius) var(--uui-border-radius) 0 0'
                              : 'var(--uui-border-radius)',
                            cursor: 'pointer', fontFamily: 'var(--uui-font)',
                          }}
                        >
                          <div style={{ display: 'flex', alignItems: 'center', gap: '7px' }}>
                            <Users size={13} style={{ color: accentColor }} />
                            <span style={{ fontSize: '12px', fontWeight: 600, color: 'var(--uui-text-secondary)' }}>
                              View {alert.affected_count} Affected SMEs — Impact Preview &amp; Agent Analysis
                            </span>
                          </div>
                          {affectedOpen
                            ? <ChevronUp size={14} style={{ color: 'var(--uui-text-tertiary)' }} />
                            : <ChevronDown size={14} style={{ color: 'var(--uui-text-tertiary)' }} />}
                        </button>

                        {/* Affected SME list body */}
                        {affectedOpen && (
                          <div style={{
                            padding: '12px',
                            border: '1px solid var(--uui-neutral-60)',
                            borderTop: 'none',
                            borderRadius: '0 0 var(--uui-border-radius) var(--uui-border-radius)',
                            background: 'var(--uui-neutral-80)',
                          }}>
                            <AffectedSMEList alert={alert} accentColor={accentColor} />
                          </div>
                        )}
                      </div>
                    )}

                    {/* Expanded — fully-wired task creation panel */}
                    {isExpanded && (
                      <div style={{ marginBottom: '12px', paddingTop: '12px', borderTop: '1px solid var(--uui-neutral-60)' }}>
                        <div style={{ fontSize: '11px', fontWeight: 600, color: 'var(--uui-text-tertiary)', textTransform: 'uppercase', marginBottom: '9px' }}>
                          Create Task
                        </div>

                        {/* Task preview — what will be created */}
                        <div style={{
                          padding: '10px 12px', marginBottom: '10px',
                          background: 'var(--uui-neutral-80)',
                          border: '1px solid var(--uui-neutral-60)',
                          borderRadius: 'var(--uui-border-radius)',
                          fontSize: '11px', color: 'var(--uui-text-tertiary)', lineHeight: 1.6,
                        }}>
                          <div style={{ fontWeight: 600, color: 'var(--uui-text-secondary)', marginBottom: '4px' }}>
                            Follow up: {alert.smeName} — {alert.title}
                          </div>
                          <div>
                            Priority: <span style={{ color: isCritical ? 'var(--uui-critical-60)' : 'var(--uui-warning-60)', fontWeight: 600 }}>
                              {isCritical ? 'High (auto — critical alert)' : draft.priority}
                            </span>
                            {' · '}
                            Due: {isCritical ? '1 day' : draft.priority === 'high' ? '1 day' : draft.priority === 'low' ? '7 days' : '3 days'}
                          </div>
                          {alert.signals.length > 0 && (
                            <div style={{ marginTop: '4px', color: 'var(--uui-text-tertiary)' }}>
                              Signals attached: {alert.signals.map(s => s.source).join(', ')}
                            </div>
                          )}
                          {alert.recommendation && (
                            <div style={{ marginTop: '4px', color: 'var(--uui-text-tertiary)' }}>
                              Action: {alert.recommendation}
                            </div>
                          )}
                        </div>

                        {/* Assignment + priority selectors */}
                        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '9px' }}>
                          <div>
                            <label style={{ fontSize: '11px', color: 'var(--uui-text-tertiary)', display: 'block', marginBottom: '4px' }}>
                              Credit Officer
                            </label>
                            <select
                              value={draft.assignee}
                              onChange={e => patchDraft(alert.id, { assignee: e.target.value })}
                              style={selectStyle}
                            >
                              <option value="">Select officer...</option>
                              {CREDIT_OFFICERS.map(o => (
                                <option key={o.value} value={o.label}>{o.label}</option>
                              ))}
                            </select>
                          </div>
                          <div>
                            <label style={{ fontSize: '11px', color: 'var(--uui-text-tertiary)', display: 'block', marginBottom: '4px' }}>
                              Priority {isCritical && <span style={{ color: 'var(--uui-critical-60)' }}>(auto-set)</span>}
                            </label>
                            <select
                              value={isCritical ? 'high' : draft.priority}
                              disabled={isCritical}
                              onChange={e => patchDraft(alert.id, { priority: e.target.value as TaskDraft['priority'] })}
                              style={{ ...selectStyle, opacity: isCritical ? 0.6 : 1 }}
                            >
                              <option value="high">High</option>
                              <option value="medium">Medium</option>
                              <option value="low">Low</option>
                            </select>
                          </div>
                        </div>
                      </div>
                    )}

                    {/* Action buttons */}
                    <div style={{ display: 'flex', alignItems: 'center', gap: '6px', flexWrap: 'wrap' }}>
                      <Button variant="secondary" size="sm" onClick={() => handleCreateTask(alert)}>
                        📋 Create Task
                      </Button>
                      <Button variant="secondary" size="sm" onClick={() => handleRunScenario(alert)}>
                        🎯 Run Scenario
                      </Button>
                      {alert.scope === 'sme' && (
                        <Button variant="secondary" size="sm" onClick={() => handleViewSME(alert)}>
                          👁️ View SME
                        </Button>
                      )}
                      {isIndustry && (
                        <Button
                          variant="secondary" size="sm"
                          onClick={() => {
                            setExpandedId(alert.id)
                            setAffectedOpenId(affectedOpen ? null : alert.id)
                          }}
                        >
                          <Users size={12} style={{ marginRight: '4px' }} />
                          Affected SMEs
                        </Button>
                      )}
                      <Button variant="secondary" size="sm" onClick={() => setExpandedId(isExpanded ? null : alert.id)}>
                        {isExpanded ? 'Less' : 'Details'}
                      </Button>
                    </div>

                  </div>
                </div>
              )
            })}

            {alerts.length === 0 && (
              <div style={{ textAlign: 'center', padding: '48px', color: 'var(--uui-text-tertiary)' }}>
                <div style={{ fontSize: '36px', marginBottom: '12px' }}>🔔</div>
                <p style={{ fontSize: '13px', marginBottom: '16px' }}>No alerts yet</p>
                <Button variant="primary" size="sm" onClick={handleSimulate} disabled={isSimulating}>
                  ⚡ Simulate Live Feed
                </Button>
              </div>
            )}
          </div>
        )}
      </CardContent>
    </Card>
  )
}

export default AlertsTab