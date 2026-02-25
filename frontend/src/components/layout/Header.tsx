import { Clock, UserCircle } from 'lucide-react'

const MOCK_USER = {
  name: 'Sarah Chen',
}

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
      {/* Left — logo + title */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
        <img
          src="/cymbal.png"
          alt="EPAM"
          style={{ height: '48px' }}
        />
        <div>
          <div style={{ fontSize: '16px', fontWeight: 600, color: 'var(--uui-text-primary)' }}>
            Credit Risk Intelligence Platform
          </div>
          <div style={{ fontSize: '11px', color: 'var(--uui-text-tertiary)' }}>
            for SMEs
          </div>
        </div>
      </div>

      {/* Right — timestamp + user */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '20px' }}>
        <div style={{ fontSize: '12px', color: 'var(--uui-text-tertiary)', display: 'flex', alignItems: 'center', gap: '6px' }}>
          <Clock size={14} />
          Last Updated: {currentTime}
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <span style={{ fontSize: '12px', fontWeight: 600, color: 'var(--uui-text-primary)' }}>
            {MOCK_USER.name}
          </span>
          <UserCircle size={28} style={{ color: 'var(--uui-primary-60)' }} />
        </div>
      </div>
    </header>
  )
}

export default Header