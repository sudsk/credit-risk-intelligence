import { useDispatch, useSelector } from 'react-redux'
import { RootState } from '@/store'
import { setActiveTab } from '@/store/uiSlice'

const tabs = [
  { id: 'home', label: 'Home', icon: '🏠', badge: null, badgeType: null },
  { id: 'alerts', label: 'Alerts', icon: '📰', badge: null, badgeType: 'warning' },
  { id: 'scenarios', label: 'Scenarios', icon: '🎯', badge: null, badgeType: 'info' },
] as const

const badgeColors: Record<string, string> = {
  critical: 'var(--uui-critical-60)',
  warning: 'var(--uui-warning-60)',
  info: 'var(--uui-primary-60)',
}

const TabNavigation = () => {
  const dispatch = useDispatch()
  const activeTab = useSelector((state: RootState) => state.ui.activeTab)

  return (
    <div style={{
      background: 'var(--uui-neutral-80)',
      borderBottom: '1px solid var(--uui-neutral-60)',
      position: 'sticky', top: '48px', zIndex: 99
    }}>
      <div style={{ maxWidth: '1600px', margin: '0 auto', padding: '0 18px', display: 'flex' }}>
        {tabs.map((tab) => {
          const isActive = activeTab === tab.id
          return (
            <button
              key={tab.id}
              onClick={() => dispatch(setActiveTab(tab.id))}
              style={{
                padding: '12px 24px',
                background: isActive ? 'var(--uui-neutral-70)' : 'transparent',
                border: 'none',
                borderBottom: isActive ? '3px solid var(--uui-primary-60)' : '3px solid transparent',
                color: isActive ? 'var(--uui-primary-60)' : 'var(--uui-text-tertiary)',
                cursor: 'pointer',
                fontSize: '14px',
                fontWeight: 600,
                display: 'flex',
                alignItems: 'center',
                gap: '9px',
                transition: 'all 0.2s',
                fontFamily: 'var(--uui-font)',
              }}
            >
              <span>{tab.icon}</span>
              <span>{tab.label}</span>
              {tab.badge !== null && (
                <span style={{
                  background: badgeColors[tab.badgeType!] || 'var(--uui-primary-60)',
                  color: 'white',
                  fontSize: '10px',
                  fontWeight: 700,
                  padding: '2px 6px',
                  borderRadius: '10px',
                  minWidth: '18px',
                  textAlign: 'center',
                }}>
                  {tab.badge}
                </span>
              )}
            </button>
          )
        })}
      </div>
    </div>
  )
}

export default TabNavigation