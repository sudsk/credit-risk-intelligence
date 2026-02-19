import { Clock } from 'lucide-react'

const Header = () => {
  const currentTime = new Date().toLocaleString('en-GB', {
    weekday: 'long', year: 'numeric', month: 'long',
    day: 'numeric', hour: '2-digit', minute: '2-digit',
  })

  return (
    <header style={{
      background: 'var(--uui-neutral-70)',
      borderBottom: '1px solid var(--uui-neutral-60)',
      position: 'sticky', top: 0, zIndex: 100, height: '48px',
      display: 'flex', alignItems: 'center',
      justifyContent: 'space-between', padding: '0 24px'
    }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
        <svg width="32" height="32" viewBox="0 0 32 32" fill="none">
          <rect width="32" height="32" rx="6" fill="#48a4d0" />
          <path d="M16 8L22 12V20L16 24L10 20V12L16 8Z" fill="white" fillOpacity="0.9" />
          <path d="M16 12L19 14V18L16 20L13 18V14L16 12Z" fill="#1a1a1a" />
        </svg>
        <div>
          <div style={{ fontSize: '16px', fontWeight: 600, color: 'var(--uui-text-primary)' }}>
            Foresight AI
          </div>
          <div style={{ fontSize: '11px', color: 'var(--uui-text-tertiary)' }}>
            SME Credit Risk Intelligence Platform
          </div>
        </div>
      </div>
      <div style={{ fontSize: '12px', color: 'var(--uui-text-tertiary)', display: 'flex', alignItems: 'center', gap: '6px' }}>
        <Clock size={14} />
        Last Updated: {currentTime}
      </div>
    </header>
  )
}

export default Header