import { AlertCircle, Info, CheckCircle, AlertTriangle, Clock } from 'lucide-react'
import { formatRelativeTime } from '@/utils/formatters'
import { cn } from '@/utils/formatters'
import type { Activity } from '@/services/types'

// Mock data
const mockActivities: Activity[] = [
  {
    id: 'act_001',
    timestamp: '2024-11-16T14:32:17Z',
    type: 'alert',
    message: 'TechStart Solutions risk score increased to 68 (CRITICAL). CTO departure detected via LinkedIn.',
  },
  {
    id: 'act_002',
    timestamp: '2024-11-16T12:15:00Z',
    type: 'info',
    message: 'Q3 financial estimates batch updated for 1,284 SMEs. Average processing time: 23 seconds.',
  },
  {
    id: 'act_003',
    timestamp: '2024-11-16T10:45:32Z',
    type: 'success',
    message: 'Credit application #0823 GreenTech Energy approved at €300K facility.',
  },
  {
    id: 'act_004',
    timestamp: '2024-11-16T09:22:18Z',
    type: 'warning',
    message: 'Urban Fashion Ltd payment delays detected. 3 suppliers flagged (avg 47 days late).',
  },
  {
    id: 'act_005',
    timestamp: '2024-11-16T08:10:45Z',
    type: 'info',
    message: 'Daily portfolio risk recalculation completed. 1,284 SMEs processed in 2 minutes.',
  },
  {
    id: 'act_006',
    timestamp: '2024-11-15T16:50:12Z',
    type: 'alert',
    message: 'Portfolio default probability increased: 2.8% → 3.2% (+0.4%). Review critical SMEs.',
  },
  {
    id: 'act_007',
    timestamp: '2024-11-15T14:30:00Z',
    type: 'success',
    message: 'Scenario "Interest Rate +1%" completed. 15 SMEs moved to critical category.',
  },
  {
    id: 'act_008',
    timestamp: '2024-11-15T11:15:22Z',
    type: 'info',
    message: 'Weekly report generated: 47 new intelligence alerts, 23 tasks created, 18 completed.',
  },
  {
    id: 'act_009',
    timestamp: '2024-11-15T09:05:33Z',
    type: 'warning',
    message: 'Digital Marketing Hub client churn detected. Review scores: 4.2 → 3.1 stars.',
  },
  {
    id: 'act_010',
    timestamp: '2024-11-14T17:40:19Z',
    type: 'alert',
    message: 'Predicted Event: UK Hemp Ban vote on Dec 1 (75% probability). 8 SMEs affected.',
  },
]

interface ActivityFeedProps {
  activities: Activity[]
}

const ActivityFeed = ({ activities }: ActivityFeedProps) => {
  const displayActivities = activities.length > 0 ? activities : mockActivities

  const getActivityIcon = (type: string) => {
    switch (type) {
      case 'alert':
        return <AlertCircle className="w-4 h-4 text-critical-60" />
      case 'warning':
        return <AlertTriangle className="w-4 h-4 text-warning-60" />
      case 'success':
        return <CheckCircle className="w-4 h-4 text-success-60" />
      case 'info':
      default:
        return <Info className="w-4 h-4 text-primary-60" />
    }
  }

  const getActivityColor = (type: string) => {
    switch (type) {
      case 'alert':
        return 'border-l-critical-60 bg-critical-50'
      case 'warning':
        return 'border-l-warning-60 bg-warning-50'
      case 'success':
        return 'border-l-success-60 bg-success-50'
      case 'info':
      default:
        return 'border-l-primary-60 bg-neutral-50'
    }
  }

  return (
    <div className="space-y-3">
      {displayActivities.map((activity) => (
        <div
          key={activity.id}
          className={cn(
            'border-l-4 rounded p-4 flex items-start gap-3',
            getActivityColor(activity.type)
          )}
        >
          <div className="mt-0.5">{getActivityIcon(activity.type)}</div>
          <div className="flex-1">
            <p className="text-sm text-neutral-800">{activity.message}</p>
            <div className="flex items-center gap-1 text-xs text-neutral-500 mt-1">
              <Clock className="w-3 h-3" />
              <span>{formatRelativeTime(activity.timestamp)}</span>
            </div>
          </div>
        </div>
      ))}

      {/* Empty State */}
      {displayActivities.length === 0 && (
        <div className="text-center py-12 text-neutral-500">
          <div className="text-4xl mb-3">🔔</div>
          <p className="text-sm">No activities to display</p>
        </div>
      )}
    </div>
  )
}

export default ActivityFeed
