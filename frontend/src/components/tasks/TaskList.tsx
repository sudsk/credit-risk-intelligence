import { useState } from 'react'
import { useDispatch, useSelector } from 'react-redux'
import { RootState } from '@/store'
import { updateTask } from '@/store/tasksSlice'
import { setActiveTab } from '@/store/uiSlice'
import { setSelectedSME } from '@/store/portfolioSlice'
import TaskCard from './TaskCard'
import { Button } from '../common/Button'
import { Plus } from 'lucide-react'
import { portfolioAPI } from '@/services/api'

const TaskList = () => {
  const dispatch = useDispatch()
  const tasks = useSelector((state: RootState) => state.tasks.tasks)
  const [showAllUpcoming, setShowAllUpcoming] = useState(false)

  const overdueTasks = tasks.filter((t) => t.status === 'overdue')
  const dueTodayTasks = tasks.filter((t) => t.status === 'due_today')
  const upcomingTasks = tasks.filter((t) => t.status === 'upcoming')

  const displayedUpcoming = showAllUpcoming ? upcomingTasks : upcomingTasks.slice(0, 3)

  const handleCompleteTask = (taskId: string) => {
    const task = tasks.find((t) => t.id === taskId)
    if (task) {
      dispatch(updateTask({ ...task, status: 'completed' }))
    }
  }

  const handleViewSME = async (task: typeof tasks[0]) => {
    try {
      const sme = await portfolioAPI.getSMEById(task.smeId)
      dispatch(setSelectedSME({
        id: sme.id,
        name: sme.name,
        riskScore: sme.risk_score,
        riskCategory: sme.risk_category,
        exposure: `€${(sme.exposure / 1000).toFixed(0)}K`,
        sector: sme.sector,
        geography: sme.geography,
        trend: sme.trend,
        trendValue: sme.trend_value,
      }))
      dispatch(setActiveTab('home'))
    } catch (err) {
      console.error('Failed to load SME:', err)
    }
  }

  const handleViewSource = (task: typeof tasks[0]) => {
    if (task.source.includes('Predicted Event') || task.source.includes('News Intelligence')) {
      dispatch(setActiveTab('news'))
    }
  }

  return (
    <div className="space-y-6">
      {/* Overdue Tasks */}
      {overdueTasks.length > 0 && (
        <section>
          <h3 style={{ fontSize: '16px', fontWeight: 600, color: 'var(--uui-critical-60)', marginBottom: '12px' }}>
            ⚠️ Overdue Tasks ({overdueTasks.length})
          </h3>
          <div className="space-y-3">
            {overdueTasks.map((task) => (
              <TaskCard
                key={task.id}
                task={task}
                onComplete={() => handleCompleteTask(task.id)}
                onViewSME={() => handleViewSME(task)}
                onViewSource={() => handleViewSource(task)}
              />
            ))}
          </div>
        </section>
      )}

      {/* Due Today */}
      {dueTodayTasks.length > 0 && (
        <section>
          <h3 style={{ fontSize: '16px', fontWeight: 600, color: 'var(--uui-warning-60)', marginBottom: '12px' }}>
            📅 Due Today ({dueTodayTasks.length})
          </h3>
          <div className="space-y-3">
            {dueTodayTasks.map((task) => (
              <TaskCard
                key={task.id}
                task={task}
                onComplete={() => handleCompleteTask(task.id)}
                onViewSME={() => handleViewSME(task)}
                onViewSource={() => handleViewSource(task)}
              />
            ))}
          </div>
        </section>
      )}

      {/* Upcoming Tasks */}
      {upcomingTasks.length > 0 && (
        <section>
          <h3 style={{ fontSize: '16px', fontWeight: 600, color: 'var(--uui-primary-60)', marginBottom: '12px' }}>
            📋 Upcoming Tasks ({upcomingTasks.length})
          </h3>
          <div className="space-y-3">
            {displayedUpcoming.map((task) => (
              <TaskCard
                key={task.id}
                task={task}
                onComplete={() => handleCompleteTask(task.id)}
                onViewSME={() => handleViewSME(task)}
                onViewSource={() => handleViewSource(task)}
              />
            ))}
          </div>
          {upcomingTasks.length > 3 && !showAllUpcoming && (
            <div className="mt-3">
              <Button variant="secondary" size="md" fullWidth onClick={() => setShowAllUpcoming(true)}>
                Show All {upcomingTasks.length} Upcoming Tasks
              </Button>
            </div>
          )}
        </section>
      )}

      {/* Empty State */}
      {tasks.length === 0 && (
        <div style={{ textAlign: 'center', padding: '48px', background: 'var(--uui-surface-main)', border: '1px solid var(--uui-neutral-60)', borderRadius: 'var(--uui-border-radius)' }}>
          <div style={{ fontSize: '36px', marginBottom: '12px' }}>📋</div>
          <p style={{ fontSize: '16px', fontWeight: 500, color: 'var(--uui-text-secondary)', marginBottom: '8px' }}>No tasks yet</p>
          <p style={{ fontSize: '13px', color: 'var(--uui-text-tertiary)', marginBottom: '24px' }}>Create tasks from news events or scenarios</p>
          <Button variant="primary" size="md"><Plus size={14} />Create New Task</Button>
        </div>
      )}
    </div>
  )
}

export default TaskList