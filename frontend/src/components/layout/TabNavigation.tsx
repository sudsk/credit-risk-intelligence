import { useDispatch, useSelector } from 'react-redux'
import { RootState } from '@/store'
import { setActiveTab } from '@/store/uiSlice'
import { cn } from '@/utils/formatters'

const tabs = [
  { id: 'home', label: 'Home', icon: '🏠', badge: null },
  { id: 'news', label: 'News & Events', icon: '📰', badge: 11, badgeType: 'warning' },
  { id: 'tasks', label: 'Tasks', icon: '📋', badge: 12, badgeType: 'critical' },
  { id: 'scenarios', label: 'Scenarios', icon: '🎯', badge: 3, badgeType: 'info' },
  { id: 'activities', label: 'Activities', icon: '🔔', badge: 47, badgeType: 'info' },
] as const

const TabNavigation = () => {
  const dispatch = useDispatch()
  const activeTab = useSelector((state: RootState) => state.ui.activeTab)

  const handleTabClick = (tabId: typeof tabs[number]['id']) => {
    dispatch(setActiveTab(tabId))
  }

  return (
    <div className="sticky top-12 z-40 bg-neutral-800 border-b border-neutral-600">
      <div className="max-w-[1600px] mx-auto px-4">
        <div className="flex gap-0">
          {tabs.map((tab) => (
            <button
              key={tab.id}
              onClick={() => handleTabClick(tab.id)}
              className={cn(
                'px-6 py-3 text-sm font-semibold transition-all border-b-3 flex items-center gap-2',
                'hover:bg-neutral-70 hover:text-white',
                activeTab === tab.id
                  ? 'text-primary-60 border-b-primary-60 bg-neutral-70'
                  : 'text-neutral-400 border-b-transparent'
              )}
            >
              <span>{tab.icon}</span>
              <span>{tab.label}</span>
              {tab.badge !== null && (
                <span
                  className={cn(
                    'px-2 py-0.5 text-[10px] font-bold rounded-full min-w-[18px] text-center',
                    tab.badgeType === 'critical' && 'bg-critical-60 text-white',
                    tab.badgeType === 'warning' && 'bg-warning-60 text-white',
                    tab.badgeType === 'info' && 'bg-primary-60 text-white'
                  )}
                >
                  {tab.badge}
                </span>
              )}
            </button>
          ))}
        </div>
      </div>
    </div>
  )
}

export default TabNavigation
