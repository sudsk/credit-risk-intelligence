import { useEffect } from 'react'
import { useDispatch, useSelector } from 'react-redux'
import Header from './components/layout/Header'
import TabNavigation from './components/layout/TabNavigation'
import ChatFloatingButton from './components/layout/ChatFloatingButton'
import HomeTab from './components/home/HomeTab'
import NewsEventsTab from './components/news-events/NewsEventsTab'
import TasksTab from './components/tasks/TasksTab'
import ScenariosTab from './components/scenarios/ScenariosTab'
import ActivitiesTab from './components/activities/ActivitiesTab'
import ChatModal from './components/chat/ChatModal'
import BreakdownModal from './components/home/BreakdownModal'
import { RootState } from './store'
import { useWebSocket } from './hooks/useWebSocket'
import { updateScenario } from './store/scenariosSlice'
import { addTask } from './store/tasksSlice'
import type { Scenario, Task } from './services/types'

function App() {
  const dispatch = useDispatch()
  const activeTab = useSelector((state: RootState) => state.ui.activeTab)
  const chatOpen = useSelector((state: RootState) => state.chat.isOpen)

  return (
    <div style={{ background: 'var(--uui-app-bg)', minHeight: '100vh' }}>
      <Header />
      <TabNavigation />

      <main style={{ maxWidth: '1600px', margin: '0 auto', padding: '18px' }}>
        {/* Tab Content */}
        {activeTab === 'home' && <HomeTab />}
        {activeTab === 'news' && <NewsEventsTab />}
        {activeTab === 'tasks' && <TasksTab />}
        {activeTab === 'scenarios' && <ScenariosTab />}
        {activeTab === 'activities' && <ActivitiesTab />}
      </main>

      {/* Modals & Floating Elements */}
      <ChatFloatingButton />
      {chatOpen && <ChatModal />}
      <BreakdownModal />
    </div>
  )
}

export default App
