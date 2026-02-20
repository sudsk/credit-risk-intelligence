import { AlertCircle, Info, CheckCircle, AlertTriangle, Clock } from 'lucide-react'
import { formatRelativeTime } from '@/utils/formatters'
import type { Activity } from '@/services/types'

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
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '9px' }}>
      {activities.map((activity) => {
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

      {activities.length === 0 && (
        <div style={{ textAlign: 'center', padding: '48px', color: 'var(--uui-text-tertiary)' }}>
          <div style={{ fontSize: '36px', marginBottom: '12px' }}>🔔</div>
          <p style={{ fontSize: '13px' }}>No activities to display</p>
        </div>
      )}
    </div>
  )
}

export default ActivityFeed