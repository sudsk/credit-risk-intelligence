import { AlertCircle, Clock, Calendar, CheckCircle } from 'lucide-react'
import { useSelector } from 'react-redux'
import { RootState } from '@/store'

const TaskSummary = () => {
  const tasks = useSelector((state: RootState) => state.tasks.tasks)

  const overdueTasks = tasks.filter((t) => t.status === 'overdue')
  const dueTodayTasks = tasks.filter((t) => t.status === 'due_today')
  const upcomingTasks = tasks.filter((t) => t.status === 'upcoming')
  const completedThisWeek = tasks.filter((t) => t.status === 'completed')

  const metrics = [
    { icon: <AlertCircle size={24} style={{ color: 'white' }} />, bg: 'var(--uui-critical-60)', count: overdueTasks.length, label: 'Overdue' },
    { icon: <Clock size={24} style={{ color: 'white' }} />, bg: 'var(--uui-warning-60)', count: dueTodayTasks.length, label: 'Due Today' },
    { icon: <Calendar size={24} style={{ color: 'white' }} />, bg: 'var(--uui-primary-60)', count: upcomingTasks.length, label: 'Upcoming' },
    { icon: <CheckCircle size={24} style={{ color: 'white' }} />, bg: 'var(--uui-success-60)', count: completedThisWeek.length, label: 'Completed This Week' },
  ]

  return (
    <div style={{
      background: 'var(--uui-neutral-70)',
      borderRadius: 'var(--uui-border-radius)',
      padding: '18px',
      border: '1px solid var(--uui-neutral-60)',
    }}>
      <div style={{
        fontSize: '12px', fontWeight: 600,
        color: 'var(--uui-text-tertiary)',
        textTransform: 'uppercase',
        marginBottom: '18px',
      }}>
        Task Summary
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '24px' }}>
        {metrics.map((m) => (
          <div key={m.label} style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
            <div style={{
              width: '48px', height: '48px', borderRadius: '50%',
              background: m.bg,
              display: 'flex', alignItems: 'center', justifyContent: 'center',
              flexShrink: 0,
            }}>
              {m.icon}
            </div>
            <div>
              <div style={{ fontSize: '24px', fontWeight: 700, color: 'var(--uui-text-primary)' }}>
                {m.count}
              </div>
              <div style={{ fontSize: '11px', color: 'var(--uui-text-tertiary)' }}>
                {m.label}
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}

export default TaskSummary