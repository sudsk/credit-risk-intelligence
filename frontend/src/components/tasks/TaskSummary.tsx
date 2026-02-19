import { AlertCircle, Clock, Calendar, CheckCircle } from 'lucide-react'
import { useSelector } from 'react-redux'
import { RootState } from '@/store'

const TaskSummary = () => {
  const tasks = useSelector((state: RootState) => state.tasks.tasks)

  const overdueTasks = tasks.filter((t) => t.status === 'overdue')
  const dueTodayTasks = tasks.filter((t) => t.status === 'due_today')
  const upcomingTasks = tasks.filter((t) => t.status === 'upcoming')
  const completedThisWeek = tasks.filter((t) => t.status === 'completed')

  return (
    <div style={{ background: 'var(--uui-neutral-70)', borderRadius: 'var(--uui-border-radius)', padding: '18px', border: '1px solid var(--uui-neutral-60)' }}>
      <h3 style={{ fontSize: '12px', fontWeight: 600, color: 'var(--uui-text-tertiary)', textTransform: 'uppercase', marginBottom: '18px' }}>
        Task Summary
      </h3>
      <div className="grid grid-cols-4 gap-6">
        {/* Overdue */}
        <div className="flex items-center gap-3">
          <div className="w-12 h-12 rounded-full bg-critical-60 flex items-center justify-center">
            <AlertCircle className="w-6 h-6 text-white" />
          </div>
          <div>
            <div className="text-2xl font-bold text-white">{overdueTasks.length}</div>
            <div className="text-xs text-neutral-400">Overdue</div>
          </div>
        </div>

        {/* Due Today */}
        <div className="flex items-center gap-3">
          <div className="w-12 h-12 rounded-full bg-warning-60 flex items-center justify-center">
            <Clock className="w-6 h-6 text-white" />
          </div>
          <div>
            <div className="text-2xl font-bold text-white">{dueTodayTasks.length}</div>
            <div className="text-xs text-neutral-400">Due Today</div>
          </div>
        </div>

        {/* Upcoming */}
        <div className="flex items-center gap-3">
          <div className="w-12 h-12 rounded-full bg-primary-60 flex items-center justify-center">
            <Calendar className="w-6 h-6 text-white" />
          </div>
          <div>
            <div className="text-2xl font-bold text-white">{upcomingTasks.length}</div>
            <div className="text-xs text-neutral-400">Upcoming</div>
          </div>
        </div>

        {/* Completed This Week */}
        <div className="flex items-center gap-3">
          <div className="w-12 h-12 rounded-full bg-success-60 flex items-center justify-center">
            <CheckCircle className="w-6 h-6 text-white" />
          </div>
          <div>
            <div className="text-2xl font-bold text-white">{completedThisWeek.length}</div>
            <div className="text-xs text-neutral-400">Completed This Week</div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default TaskSummary
