import { CheckCircle, ExternalLink, Eye } from 'lucide-react'
import { Button } from '../common/Button'
import { Badge } from '../common/Badge'
import type { Task } from '@/services/types'

interface TaskCardProps {
  task: Task
  onComplete: () => void
  onViewSME: () => void
  onViewSource: () => void
}

const TaskCard = ({ task, onComplete, onViewSME, onViewSource }: TaskCardProps) => {

  const getBorderColor = (status: string) => {
    switch (status) {
      case 'overdue': return 'var(--uui-critical-60)'
      case 'due_today': return 'var(--uui-warning-60)'
      default: return 'var(--uui-neutral-60)'
    }
  }

  const getPriorityVariant = (priority: string) => {
    switch (priority) {
      case 'high': return 'critical'
      case 'medium': return 'warning'
      case 'low': return 'info'
      default: return 'info'
    }
  }

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-GB', {
      year: 'numeric', month: 'short', day: 'numeric'
    })
  }

  return (
    <div style={{
      background: 'var(--uui-neutral-70)',
      border: `1px solid var(--uui-neutral-60)`,
      borderLeft: `3px solid ${getBorderColor(task.status)}`,
      borderRadius: 'var(--uui-border-radius)',
      padding: '12px',
    }}>

      {/* Header Row */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '9px' }}>
        <div style={{ flex: 1 }}>
          {/* Client ID + Priority Badge */}
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '6px' }}>
            <span style={{
              fontSize: '11px',
              color: 'var(--uui-text-tertiary)',
              fontFamily: 'var(--uui-font-mono)',
            }}>
              {task.smeId} {task.smeName}
            </span>
            <Badge variant={getPriorityVariant(task.priority) as any}>
              {task.priority.toUpperCase()}
            </Badge>
          </div>

          {/* Task Title */}
          <div style={{
            fontSize: '13px',
            fontWeight: 600,
            color: 'var(--uui-text-primary)',
            marginBottom: '4px',
          }}>
            {task.title}
          </div>

          {/* Meta info */}
          <div style={{
            fontSize: '11px',
            color: 'var(--uui-text-tertiary)',
            display: 'flex',
            gap: '12px',
            flexWrap: 'wrap' as const,
          }}>
            <span><strong style={{ color: 'var(--uui-text-secondary)' }}>Due:</strong> {formatDate(task.dueDate)}</span>
            <span><strong style={{ color: 'var(--uui-text-secondary)' }}>Assigned:</strong> {task.assignee}</span>
            <span><strong style={{ color: 'var(--uui-text-secondary)' }}>Exposure:</strong>
              <span style={{ fontFamily: 'var(--uui-font-mono)', marginLeft: '4px' }}>{task.exposure}</span>
            </span>
          </div>
        </div>
      </div>

      {/* Description */}
      {task.description && (
        <div style={{
          fontSize: '12px',
          color: 'var(--uui-text-secondary)',
          marginBottom: '9px',
          lineHeight: 1.5,
        }}>
          {task.description}
        </div>
      )}

      {/* Source */}
      <div style={{
        fontSize: '11px',
        color: 'var(--uui-text-tertiary)',
        marginBottom: '12px',
        display: 'flex',
        alignItems: 'center',
        gap: '4px',
        fontStyle: 'italic',
      }}>
        <ExternalLink size={11} />
        <span><strong>Created from:</strong> {task.source}</span>
      </div>

      {/* Actions */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '6px', flexWrap: 'wrap' as const }}>
        <Button variant="primary" size="sm" onClick={onComplete}>
          <CheckCircle size={13} />
          Mark Complete
        </Button>
        <Button variant="secondary" size="sm" onClick={onViewSME}>
          <Eye size={13} />
          View SME Details
        </Button>
        <Button variant="secondary" size="sm" onClick={onViewSource}>
          <ExternalLink size={13} />
          View Source Event
        </Button>
      </div>

    </div>
  )
}

export default TaskCard