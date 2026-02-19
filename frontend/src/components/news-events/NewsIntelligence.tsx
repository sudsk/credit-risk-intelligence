import { AlertCircle, Clock } from 'lucide-react'
import { useState } from 'react'
import { useDispatch } from 'react-redux'
import { setActiveTab } from '@/store/uiSlice'
import { setSelectedSME } from '@/store/portfolioSlice'
import { addScenario } from '@/store/scenariosSlice'
import { addTask } from '@/store/tasksSlice'
import { Button } from '../common/Button'
import { Card, CardHeader, CardTitle, CardContent } from '../common/Card'
import { Badge } from '../common/Badge'
import { formatRelativeTime } from '@/utils/formatters'

const newsItems = [
  {
    id: 'news_001',
    timestamp: '2024-11-16T14:32:17Z',
    smeId: '#0142',
    smeName: 'TechStart Solutions Ltd',
    exposure: '€250K',
    type: 'departure' as const,
    severity: 'critical' as const,
    title: 'CTO Departure Detected',
    summary: 'LinkedIn activity shows CTO Sarah Johnson departed 2 hours ago. No replacement hire detected. Sales Director also left within 2-week window.',
    signals: [
      { source: 'LinkedIn', detail: 'CTO profile updated: "Open to new opportunities"' },
      { source: 'Web Traffic', detail: '-42% QoQ decline' },
      { source: 'Client Data', detail: '2 major clients lost in past 30 days' },
    ],
    recommendation: 'Immediate management meeting recommended. High risk of further deterioration.',
  },
  {
    id: 'news_002',
    timestamp: '2024-11-16T11:15:43Z',
    smeId: '#0287',
    smeName: 'Urban Fashion Ltd',
    exposure: '€180K',
    type: 'payment_delay' as const,
    severity: 'warning' as const,
    title: 'Payment Delays to Suppliers',
    summary: 'Alternative data shows 3 suppliers reporting late payments (avg 47 days vs normal 30 days). Cash flow stress indicator.',
    signals: [
      { source: 'Trade Data', detail: '3 suppliers flagged payment delays' },
      { source: 'Banking', detail: 'Overdraft facility 85% utilized' },
      { source: 'Companies House', detail: 'No recent capital injection' },
    ],
    recommendation: 'Review cash flow forecasts. Consider covenant breach risk.',
  },
  {
    id: 'news_003',
    timestamp: '2024-11-16T08:22:11Z',
    smeId: '#0531',
    smeName: 'Digital Marketing Hub',
    exposure: '€140K',
    type: 'churn' as const,
    severity: 'warning' as const,
    title: 'Client Churn Alert',
    summary: 'Website testimonials reduced by 40%. LinkedIn shows 2 account managers left. Review scores declining (4.2 → 3.1 in 90 days).',
    signals: [
      { source: 'Reviews', detail: 'Trustpilot: 4.2 → 3.1 stars' },
      { source: 'LinkedIn', detail: '2 account managers departed' },
      { source: 'Web Traffic', detail: 'Case studies page views -60%' },
    ],
    recommendation: 'Monitor closely. Service quality deterioration pattern.',
  },
]

const NewsIntelligence = () => {
  const dispatch = useDispatch()
  const [expandedNews, setExpandedNews] = useState<string | null>(null)
  const [selectedAssignee, setSelectedAssignee] = useState<{ [key: string]: string }>({})
  const [selectedPriority, setSelectedPriority] = useState<{ [key: string]: string }>({})

  const handleRunScenario = (item: typeof newsItems[0]) => {
    dispatch(addScenario({ id: `scenario_${Date.now()}`, name: `${item.smeName} - ${item.title}`, status: 'in_progress', progress: 0, createdAt: new Date().toISOString() }))
    dispatch(setActiveTab('scenarios'))
  }

  const handleCreateTask = (item: typeof newsItems[0]) => {
    dispatch(addTask({
      id: `task_${Date.now()}`,
      title: `Follow up: ${item.smeName} - ${item.title}`,
      smeId: item.smeId, smeName: item.smeName, exposure: item.exposure,
      assignee: selectedAssignee[item.id] || 'Unassigned',
      priority: (selectedPriority[item.id] || 'medium') as 'high' | 'medium' | 'low',
      dueDate: new Date(Date.now() + 3 * 24 * 60 * 60 * 1000).toISOString(),
      status: 'upcoming', description: item.summary,
      source: `News Intelligence (${item.timestamp})`,
      createdAt: new Date().toISOString(),
    }))
    dispatch(setActiveTab('tasks'))
  }

  const handleViewSME = (smeId: string, smeName: string) => {
    dispatch(setSelectedSME({ id: smeId, name: smeName, riskScore: 68, riskCategory: 'critical', exposure: '€250K', sector: 'Software/Technology', geography: 'UK', trend: 'up', trendValue: 14 }))
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

  return (
    <Card style={{ height: 'calc(100vh - 200px)', display: 'flex', flexDirection: 'column' }}>
      <CardHeader>
        <CardTitle>
          <div style={{ display: 'flex', alignItems: 'center', gap: '9px' }}>
            <span style={{ fontSize: '20px' }}>📰</span>
            <div>
              <div style={{ fontSize: '14px', fontWeight: 600, color: 'var(--uui-text-primary)' }}>News Intelligence</div>
              <div style={{ fontSize: '11px', color: 'var(--uui-text-tertiary)', fontWeight: 400 }}>AI-Generated Insights from Alternative Data</div>
            </div>
          </div>
        </CardTitle>
      </CardHeader>

      <CardContent style={{ flex: 1, overflowY: 'auto' }}>
        <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
          {newsItems.map((item) => {
            const isCritical = item.severity === 'critical'
            const accentColor = isCritical ? 'var(--uui-critical-60)' : 'var(--uui-warning-60)'
            const isExpanded = expandedNews === item.id

            return (
              <div key={item.id} style={{
                background: 'var(--uui-neutral-70)',
                border: `1px solid var(--uui-neutral-60)`,
                borderLeft: `3px solid ${accentColor}`,
                borderRadius: 'var(--uui-border-radius)',
                overflow: 'hidden',
              }}>
                <div style={{ padding: '12px' }}>
                  {/* Meta */}
                  <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '6px' }}>
                    <span style={{ fontSize: '11px', fontFamily: 'var(--uui-font-mono)', color: 'var(--uui-text-tertiary)' }}>
                      {item.smeId} {item.smeName}
                    </span>
                    <Badge variant={isCritical ? 'critical' : 'warning'}>
                      {item.severity.toUpperCase()}
                    </Badge>
                  </div>

                  {/* Title */}
                  <div style={{ fontSize: '14px', fontWeight: 700, color: 'var(--uui-text-primary)', marginBottom: '6px' }}>
                    {item.title}
                  </div>

                  {/* Time + Exposure */}
                  <div style={{ display: 'flex', alignItems: 'center', gap: '8px', fontSize: '11px', color: 'var(--uui-text-tertiary)', marginBottom: '9px' }}>
                    <Clock size={11} />
                    <span>{formatRelativeTime(item.timestamp)}</span>
                    <span>•</span>
                    <span style={{ fontFamily: 'var(--uui-font-mono)' }}>{item.exposure} exposure</span>
                  </div>

                  {/* Summary */}
                  <p style={{ fontSize: '13px', color: 'var(--uui-text-secondary)', marginBottom: '12px', lineHeight: 1.5 }}>
                    {item.summary}
                  </p>

                  {/* Expanded: Signals */}
                  {isExpanded && (
                    <div style={{ marginBottom: '12px', paddingTop: '12px', borderTop: '1px solid var(--uui-neutral-60)' }}>
                      <div style={{ fontSize: '11px', fontWeight: 600, color: 'var(--uui-text-tertiary)', textTransform: 'uppercase', marginBottom: '9px' }}>
                        Data Signals
                      </div>
                      <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
                        {item.signals.map((signal, idx) => (
                          <div key={idx} style={{ display: 'flex', alignItems: 'flex-start', gap: '8px', fontSize: '12px', background: 'var(--uui-neutral-80)', padding: '8px', borderRadius: 'var(--uui-border-radius)' }}>
                            <AlertCircle size={12} style={{ color: 'var(--uui-text-tertiary)', marginTop: '2px', flexShrink: 0 }} />
                            <div style={{ color: 'var(--uui-text-secondary)' }}>
                              <strong style={{ color: 'var(--uui-text-primary)' }}>{signal.source}:</strong> {signal.detail}
                            </div>
                          </div>
                        ))}
                      </div>
                      {/* Recommendation */}
                      <div style={{ marginTop: '9px', padding: '9px 12px', background: 'rgba(244,184,58,0.1)', border: '1px solid var(--uui-warning-60)', borderRadius: 'var(--uui-border-radius)', fontSize: '12px', color: 'var(--uui-text-secondary)' }}>
                        <strong style={{ color: 'var(--uui-warning-70)' }}>💡 Recommendation:</strong> {item.recommendation}
                      </div>
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
                          <select value={selectedAssignee[item.id] || ''} onChange={(e) => setSelectedAssignee({ ...selectedAssignee, [item.id]: e.target.value })} style={selectStyle}>
                            <option value="">Select assignee...</option>
                            <option value="John Smith">John Smith</option>
                            <option value="Jane Doe">Jane Doe</option>
                            <option value="Sarah Chen">Sarah Chen</option>
                            <option value="Mike Wilson">Mike Wilson</option>
                          </select>
                        </div>
                        <div>
                          <label style={{ fontSize: '11px', color: 'var(--uui-text-tertiary)', display: 'block', marginBottom: '4px' }}>Priority</label>
                          <select value={selectedPriority[item.id] || 'medium'} onChange={(e) => setSelectedPriority({ ...selectedPriority, [item.id]: e.target.value })} style={selectStyle}>
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
                    <Button variant="secondary" size="sm" onClick={() => handleCreateTask(item)}>📋 Create Task</Button>
                    <Button variant="secondary" size="sm" onClick={() => handleRunScenario(item)}>🎯 Run Scenario</Button>
                    <Button variant="secondary" size="sm" onClick={() => handleViewSME(item.smeId, item.smeName)}>👁️ View SME</Button>
                    <Button variant="secondary" size="sm" onClick={() => setExpandedNews(isExpanded ? null : item.id)}>
                      {isExpanded ? 'Less' : 'Details'}
                    </Button>
                  </div>
                </div>
              </div>
            )
          })}

          {newsItems.length === 0 && (
            <div style={{ textAlign: 'center', padding: '48px', color: 'var(--uui-text-tertiary)' }}>
              <div style={{ fontSize: '36px', marginBottom: '12px' }}>📰</div>
              <p style={{ fontSize: '13px' }}>No news intelligence in the last 24 hours</p>
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  )
}

export default NewsIntelligence