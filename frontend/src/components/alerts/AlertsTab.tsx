import { AlertCircle, Bell, Clock, Loader, RefreshCw } from 'lucide-react'
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
import { alertAPI } from '@/services/api'
import type { Alert } from '@/services/types'

const AlertsTab = () => {
  const dispatch = useDispatch()
  const [alerts, setAlerts] = useState<Alert[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [isSimulating, setIsSimulating] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [expandedId, setExpandedId] = useState<string | null>(null)
  const [selectedAssignee, setSelectedAssignee] = useState<{ [key: string]: string }>({})
  const [selectedPriority, setSelectedPriority] = useState<{ [key: string]: string }>({})

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

  const handleCreateTask = (alert: Alert) => {
    dispatch(addTask({
      id: `task_${Date.now()}`,
      title: `Follow up: ${alert.smeName} — ${alert.title}`,
      smeId: alert.smeId,
      smeName: alert.smeName,
      exposure: alert.exposure,
      assignee: selectedAssignee[alert.id] || 'Unassigned',
      priority: (selectedPriority[alert.id] || 'medium') as 'high' | 'medium' | 'low',
      dueDate: new Date(Date.now() + 3 * 24 * 60 * 60 * 1000).toISOString(),
      status: 'upcoming',
      description: alert.summary,
      source: `Alert (${formatRelativeTime(alert.timestamp)})`,
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
    }))
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
              <Button
                variant="primary"
                size="sm"
                onClick={handleSimulate}
                disabled={isSimulating}
              >
                {isSimulating ? (
                  <><Loader size={13} style={{ animation: 'spin 1s linear infinite' }} /> Detecting...</>
                ) : (
                  '⚡ Simulate Live Feed'
                )}
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

              return (
                <div key={alert.id} style={{
                  background: 'var(--uui-neutral-70)',
                  border: `1px solid var(--uui-neutral-60)`,
                  borderLeft: `3px solid ${accentColor}`,
                  borderRadius: 'var(--uui-border-radius)',
                  overflow: 'hidden',
                }}>
                  <div style={{ padding: '12px' }}>
                    {/* Meta row — scope-aware */}
                    <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '6px' }}>
                      {alert.scope === 'sme' && (
                        <span style={{ fontSize: '11px', fontFamily: 'var(--uui-font-mono)', color: 'var(--uui-text-tertiary)' }}>
                          {alert.smeId} {alert.smeName}
                        </span>
                      )}
                      {alert.scope === 'sector' && (
                        <span style={{ fontSize: '11px', color: 'var(--uui-text-tertiary)' }}>
                          🏭 <strong>Sector</strong> · {alert.smeName} · {alert.affected_count} SMEs affected
                        </span>
                      )}
                      {alert.scope === 'geography' && (
                        <span style={{ fontSize: '11px', color: 'var(--uui-text-tertiary)' }}>
                          📍 <strong>Geography</strong> · {alert.smeName} · {alert.affected_count} SMEs affected
                        </span>
                      )}
                      {alert.scope === 'macro' && (
                        <span style={{ fontSize: '11px', color: 'var(--uui-text-tertiary)' }}>
                          🌐 <strong>Macro</strong> · Portfolio-wide · {alert.affected_count} SMEs affected
                        </span>
                      )}
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

                    {/* Expanded: Signals */}
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

                    {/* Expanded: Task Creation */}
                    {isExpanded && (
                      <div style={{ marginBottom: '12px', paddingTop: '12px', borderTop: '1px solid var(--uui-neutral-60)' }}>
                        <div style={{ fontSize: '11px', fontWeight: 600, color: 'var(--uui-text-tertiary)', textTransform: 'uppercase', marginBottom: '9px' }}>
                          Create Task
                        </div>
                        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '9px' }}>
                          <div>
                            <label style={{ fontSize: '11px', color: 'var(--uui-text-tertiary)', display: 'block', marginBottom: '4px' }}>Assign to</label>
                            <select value={selectedAssignee[alert.id] || ''} onChange={e => setSelectedAssignee({ ...selectedAssignee, [alert.id]: e.target.value })} style={selectStyle}>
                              <option value="">Select assignee...</option>
                              <option value="John Smith">John Smith</option>
                              <option value="Jane Doe">Jane Doe</option>
                              <option value="Sarah Chen">Sarah Chen</option>
                              <option value="Mike Wilson">Mike Wilson</option>
                            </select>
                          </div>
                          <div>
                            <label style={{ fontSize: '11px', color: 'var(--uui-text-tertiary)', display: 'block', marginBottom: '4px' }}>Priority</label>
                            <select value={selectedPriority[alert.id] || 'medium'} onChange={e => setSelectedPriority({ ...selectedPriority, [alert.id]: e.target.value })} style={selectStyle}>
                              <option value="high">High</option>
                              <option value="medium">Medium</option>
                              <option value="low">Low</option>
                            </select>
                          </div>
                        </div>
                      </div>
                    )}

                    {/* Actions */}
                    <div style={{ display: 'flex', alignItems: 'center', gap: '6px', flexWrap: 'wrap' }}>
                      <Button variant="secondary" size="sm" onClick={() => handleCreateTask(alert)}>📋 Create Task</Button>
                      <Button variant="secondary" size="sm" onClick={() => handleRunScenario(alert)}>🎯 Run Scenario</Button>
                      {alert.scope === 'sme' && (
                        <Button variant="secondary" size="sm" onClick={() => handleViewSME(alert)}>👁️ View SME</Button>
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