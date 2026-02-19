import { CheckCircle, ExternalLink, Eye, MessageSquare, User } from 'lucide-react'
import { formatDate } from '@/utils/formatters'
import { Button } from '../common/Button'
import { Badge } from '../common/Badge'
import { cn } from '@/utils/formatters'
import type { Task } from '@/services/types'

interface TaskCardProps {
  task: Task
  onComplete: () => void
  onViewSME: () => void
  onViewSource: () => void
}

const TaskCard = ({ task, onComplete, onViewSME, onViewSource }: TaskCardProps) => {
  const getStatusColor = (status: string) => {
    switch (status) {
      case 'overdue':
        return 'border-critical-60 bg-critical-50'
      case 'due_today':
        return 'border-warning-60 bg-warning-50'
      case 'upcoming':
        return 'border-primary-60 bg-white'
      default:
        return 'border-neutral-300 bg-white'
    }
  }

  const getPriorityBadge = (priority: string) => {
    switch (priority) {
      case 'high':
        return <Badge variant="critical">HIGH</Badge>
      case 'medium':
        return <Badge variant="warning">MEDIUM</Badge>
      case 'low':
        return <Badge variant="info">LOW</Badge>
      default:
        return null
    }
  }

  return (
    style = {{ background: 'var(--uui-neutral-70)', border: `1px solid var(--uui-neutral-60)`, borderLeft: task.status === 'overdue' ? '3px solid var(--uui-critical-60)' : task.status === 'due_today' ? '3px solid var(--uui-warning-60)' : '1px solid var(--uui-neutral-60)', borderRadius: 'var(--uui-border-radius)', padding: '12px' }
}
{/* Header */ }
<div className="flex items-start justify-between mb-3">
  <div className="flex-1">
    <div className="flex items-center gap-2 mb-2">
      <span className="text-xs font-mono text-neutral-600">
        {task.smeId} {task.smeName}
      </span>
      {getPriorityBadge(task.priority)}
    </div>
    <h4 className="text-base font-bold text-neutral-800 mb-1">{task.title}</h4>
    <div className="text-xs text-neutral-600">
      <strong>Due:</strong> {formatDate(task.dueDate)} •{' '}
      <strong>Assigned to:</strong> {task.assignee} •{' '}
      <strong>Exposure:</strong> <span className="font-mono">{task.exposure}</span>
    </div>
  </div>
</div>

{/* Description */ }
{
  task.description && (
    <p className="text-sm text-neutral-700 mb-3">{task.description}</p>
  )
}

{/* Source */ }
<div className="text-xs text-neutral-500 mb-3 flex items-center gap-1">
  <ExternalLink className="w-3 h-3" />
  <span>
    <strong>Created from:</strong> {task.source}
  </span>
</div>

{/* Actions */ }
<div className="flex items-center gap-2">
  <Button variant="primary" size="sm" onClick={onComplete}>
    <CheckCircle className="w-3.5 h-3.5" />
    Mark Complete
  </Button>
  <Button variant="secondary" size="sm" onClick={onViewSME}>
    <Eye className="w-3.5 h-3.5" />
    View SME Details
  </Button>
  <Button variant="secondary" size="sm" onClick={onViewSource}>
    <ExternalLink className="w-3.5 h-3.5" />
    View Source Event
  </Button>
</div>
    </div >
  )
}

export default TaskCard
