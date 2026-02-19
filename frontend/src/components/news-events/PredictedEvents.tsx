import { Calendar, Eye } from 'lucide-react'
import { useState } from 'react'
import { useDispatch } from 'react-redux'
import { setActiveTab } from '@/store/uiSlice'
import { addScenario } from '@/store/scenariosSlice'
import { addTask } from '@/store/tasksSlice'
import { Button } from '../common/Button'
import { Card, CardHeader, CardTitle, CardContent } from '../common/Card'

const predictedEvents = [
  {
    id: 'evt_001', date: '2024-12-01', daysUntil: 17,
    title: 'UK Hemp Products Ban', probability: 75,
    affects: { smes: 8, exposure: '€12M' },
    impact: '+12 to +18 avg score increase',
    keySMEs: ['#0445 GreenLeaf Products', '#0672 Natural Wellness Ltd'],
    source: 'UK Parliament Calendar',
    description: 'Parliamentary vote expected Dec 1. 75% probability of ban passing based on committee support.',
  },
  {
    id: 'evt_002', date: '2024-12-15', daysUntil: 31,
    title: 'BoE Interest Rate Decision', probability: 60,
    affects: { smes: 487, exposure: '€142M' },
    impact: 'Expected +0.25% increase',
    keySMEs: [],
    source: 'Bank of England Schedule',
    description: 'MPC meeting Dec 15. Market pricing in 60% chance of 25bps hike to combat inflation.',
  },
  {
    id: 'evt_003', date: '2025-01-10', daysUntil: 57,
    title: 'EU Data Privacy Regulation', probability: 40,
    affects: { smes: 34, exposure: '€18M' },
    impact: 'Compliance costs €50K-200K per SME',
    keySMEs: ['#0142 TechStart Solutions'],
    source: 'EU Commission Filings',
    description: 'New GDPR enforcement rules. Tech companies face increased compliance burden.',
  },
]

const PredictedEvents = () => {
  const dispatch = useDispatch()
  const [expandedEvent, setExpandedEvent] = useState<string | null>(null)

  const handleRunScenario = (event: typeof predictedEvents[0]) => {
    dispatch(addScenario({ id: `scenario_${Date.now()}`, name: `${event.title} Impact`, status: 'in_progress', progress: 0, createdAt: new Date().toISOString() }))
    dispatch(setActiveTab('scenarios'))
  }

  const handleCreateTask = (event: typeof predictedEvents[0]) => {
    dispatch(addTask({
      id: `task_${Date.now()}`,
      title: `Review Impact: ${event.title}`,
      smeId: event.keySMEs[0]?.split(' ')[0] || '',
      smeName: event.keySMEs[0] || 'Multiple SMEs',
      exposure: event.affects.exposure,
      assignee: 'Unassigned', priority: 'high',
      dueDate: event.date, status: 'upcoming',
      description: `Predicted event: ${event.title}. ${event.description}`,
      source: `Predicted Event - ${event.title}`,
      createdAt: new Date().toISOString(),
    }))
    dispatch(setActiveTab('tasks'))
  }

  return (
    <Card style={{ height: 'calc(100vh - 200px)', display: 'flex', flexDirection: 'column' }}>
      <CardHeader>
        <CardTitle>
          <div style={{ display: 'flex', alignItems: 'center', gap: '9px' }}>
            <span style={{ fontSize: '20px' }}>🔮</span>
            <div>
              <div style={{ fontSize: '14px', fontWeight: 600, color: 'var(--uui-text-primary)' }}>Predicted Events</div>
              <div style={{ fontSize: '11px', color: 'var(--uui-text-tertiary)', fontWeight: 400 }}>AI-Predicted Future Events (Next 90 Days)</div>
            </div>
          </div>
        </CardTitle>
      </CardHeader>

      <CardContent style={{ flex: 1, overflowY: 'auto' }}>
        <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
          {predictedEvents.map((event) => {
            const isExpanded = expandedEvent === event.id
            const probColor = event.probability >= 70 ? 'var(--uui-critical-60)' : event.probability >= 50 ? 'var(--uui-warning-60)' : 'var(--uui-primary-60)'

            return (
              <div key={event.id} style={{
                background: 'var(--uui-neutral-70)',
                border: `1px solid var(--uui-neutral-60)`,
                borderLeft: `3px solid ${probColor}`,
                borderRadius: 'var(--uui-border-radius)',
                overflow: 'hidden',
              }}>
                <div style={{ padding: '12px' }}>
                  {/* Date + Probability */}
                  <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '6px' }}>
                    <Calendar size={13} style={{ color: 'var(--uui-warning-60)' }} />
                    <span style={{ fontSize: '12px', fontWeight: 600, color: 'var(--uui-warning-70)' }}>
                      {event.date} ({event.daysUntil} days)
                    </span>
                    <span style={{ padding: '2px 8px', background: probColor, color: 'white', fontSize: '10px', fontWeight: 700, borderRadius: 'var(--uui-border-radius)' }}>
                      {event.probability}% Probability
                    </span>
                  </div>

                  {/* Title */}
                  <div style={{ fontSize: '14px', fontWeight: 700, color: 'var(--uui-text-primary)', marginBottom: '9px' }}>
                    {event.title}
                  </div>

                  {/* Stats */}
                  <div style={{ fontSize: '12px', color: 'var(--uui-text-secondary)', display: 'flex', flexDirection: 'column', gap: '3px', marginBottom: '12px' }}>
                    <div><strong style={{ color: 'var(--uui-text-primary)' }}>Affects:</strong> {event.affects.smes} SMEs | {event.affects.exposure} exposure</div>
                    <div><strong style={{ color: 'var(--uui-text-primary)' }}>Impact:</strong> {event.impact}</div>
                    {event.keySMEs.length > 0 && (
                      <div><strong style={{ color: 'var(--uui-text-primary)' }}>Key SMEs:</strong> {event.keySMEs.join(', ')}</div>
                    )}
                  </div>

                  {/* Expanded Description */}
                  {isExpanded && (
                    <div style={{ marginBottom: '12px', paddingTop: '12px', borderTop: '1px solid var(--uui-neutral-60)' }}>
                      <p style={{ fontSize: '13px', color: 'var(--uui-text-secondary)', marginBottom: '6px', lineHeight: 1.5 }}>
                        {event.description}
                      </p>
                      <div style={{ fontSize: '11px', color: 'var(--uui-text-tertiary)' }}>
                        <strong>Source:</strong> {event.source}
                      </div>
                    </div>
                  )}

                  {/* Actions */}
                  <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                    <Button variant="primary" size="sm" onClick={() => handleRunScenario(event)}>🎯 Run Scenario</Button>
                    <Button variant="secondary" size="sm" onClick={() => handleCreateTask(event)}>📋 Create Task</Button>
                    <Button variant="secondary" size="sm" onClick={() => setExpandedEvent(isExpanded ? null : event.id)}>
                      <Eye size={13} />
                      {isExpanded ? 'Less' : 'More'}
                    </Button>
                  </div>
                </div>
              </div>
            )
          })}

          {predictedEvents.length === 0 && (
            <div style={{ textAlign: 'center', padding: '48px', color: 'var(--uui-text-tertiary)' }}>
              <div style={{ fontSize: '36px', marginBottom: '12px' }}>🔮</div>
              <p style={{ fontSize: '13px' }}>No predicted events in the next 90 days</p>
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  )
}

export default PredictedEvents