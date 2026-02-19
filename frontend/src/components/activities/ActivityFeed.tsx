import { AlertCircle, Info, CheckCircle, AlertTriangle, Clock } from 'lucide-react'
import { formatRelativeTime } from '@/utils/formatters'
import type { Activity } from '@/services/types'

const mockActivities: Activity[] = [
  { id: 'act_001', timestamp: '2024-11-16T14:32:17Z', type: 'alert', message: 'TechStart Solutions risk score increased to 68 (CRITICAL). CTO departure detected via LinkedIn.' },
  { id: 'act_002', timestamp: '2024-11-16T12:15:00Z', type: 'info', message: 'Q3 financial estimates batch updated for 1,284 SMEs. Average processing time: 23 seconds.' },
  { id: 'act_003', timestamp: '2024-11-16T10:45:32Z', type: 'success', message: 'Credit application #0823 GreenTech Energy approved at €300K facility.' },
  { id: 'act_004', timestamp: '2024-11-16T09:22:18Z', type: 'warning', message: 'Urban Fashion Ltd payment delays detected. 3 suppliers flagged (avg 47 days late).' },
  { id: 'act_005', timestamp: '2024-11-16T08:10:45Z', type: 'info', message: 'Daily portfolio risk recalculation completed. 1,284 SMEs processed in 2 minutes.' },
  { id: 'act_006', timestamp: '2024-11-15T16:50:12Z', type: 'alert', message: 'Portfolio default probability increased: 2.8% → 3.2% (+0.4%). Review critical SMEs.' },
  { id: 'act_007', timestamp: '2024-11-15T14:30:00Z', type: 'success', message: 'Scenario "Interest Rate +1%" completed. 15 SMEs moved to critical category.' },
  { id: 'act_008', timestamp: '2024-11-15T11:15:22Z', type: 'info', message: 'Weekly report generated: 47 new intelligence alerts, 23 tasks created, 18 completed.' },
  { id: 'act_009', timestamp: '2024-11-15T09:05:33Z', type: 'warning', message: 'Digital Marketing Hub client churn detected. Review scores: 4.2 → 3.1 stars.' },
  { id: 'act_010', timestamp: '2024-11-14T17:40:19Z', type: 'alert', message: 'Predicted Event: UK Hemp Ban vote on Dec 1 (75% probability). 8 SMEs affected.' },
]

const typeConfig: Record<string, { icon: React.ReactNode; borderColor: string; bg: string }> = {
  alert: {
    icon: <AlertCircle size={16} style={{ color: 'var(--uui-critical-60)' }} />,
    borderColor: 'var(--uui-critical-60)',
    bg: 'rgba(229,98,72,0.08)',
  },
  warning: {
    icon: <AlertTriangle size={16} style={{ color: 'var(--uui-warning-60)' }} />,
    borderColor: 'var(--uui-warning-60)',
    bg: 'rgba(244,184,58,0.08)',
  },
  success: {
    icon: <CheckCircle size={16} style={{ color: 'var(--uui-success-60)' }} />,
    borderColor: 'var(--uui-success-60)',
    bg: 'rgba(131,185,24,0.08)',
  },
  info: {
    icon: <Info size={16} style={{ color: 'var(--uui-primary-60)' }} />,
    borderColor: 'var(--uui-primary-60)',
    bg: 'rgba(72,164,208,0.08)',
  },
}

interface ActivityFeedProps {
  activities: Activity[]
}

const ActivityFeed = ({ activities }: ActivityFeedProps) => {
  const displayActivities = activities.length > 0 ? activities : mockActivities

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '9px' }}>
      {displayActivities.map((activity) => {
        const config = typeConfig[activity.type] || typeConfig.info
        return (
          <div key={activity.id} style={{
            display: 'flex', alignItems: 'flex-start', gap: '12px',
            padding: '12px',
            background: config.bg,
            borderLeft: `3px solid ${config.borderColor}`,
            borderRadius: 'var(--uui-border-radius)',
            border: `1px solid var(--uui-neutral-60)`,
            borderLeftWidth: '3px',
            borderLeftColor: config.borderColor,
          }}>
            <div style={{ marginTop: '2px', flexShrink: 0 }}>{config.icon}</div>
            <div style={{ flex: 1 }}>
              <p style={{ fontSize: '13px', color: 'var(--uui-text-primary)', marginBottom: '4px' }}>{activity.message}</p>
              <div style={{ display: 'flex', alignItems: 'center', gap: '4px', fontSize: '11px', color: 'var(--uui-text-tertiary)' }}>
                <Clock size={11} />
                <span>{formatRelativeTime(activity.timestamp)}</span>
              </div>
            </div>
          </div>
        )
      })}

      {displayActivities.length === 0 && (
        <div style={{ textAlign: 'center', padding: '48px', color: 'var(--uui-text-tertiary)' }}>
          <div style={{ fontSize: '36px', marginBottom: '12px' }}>🔔</div>
          <p style={{ fontSize: '13px' }}>No activities to display</p>
        </div>
      )}
    </div>
  )
}

export default ActivityFeed