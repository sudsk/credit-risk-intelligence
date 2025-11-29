import TaskSummary from './TaskSummary'
import TaskList from './TaskList'

const TasksTab = () => {
  return (
    <div className="space-y-6">
      {/* Task Summary at Top */}
      <TaskSummary />

      {/* Task Lists */}
      <TaskList />
    </div>
  )
}

export default TasksTab
