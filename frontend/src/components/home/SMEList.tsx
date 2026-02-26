import { useState } from 'react'
import { Search } from 'lucide-react'
import { useDispatch } from 'react-redux'
import { usePortfolio } from '@/hooks/usePortfolio'
import { setSelectedSME, setSearchQuery } from '@/store/portfolioSlice'

const riskColors: Record<string, string> = {
  critical: 'var(--uui-critical-60)',
  medium: 'var(--uui-warning-60)',
  stable: 'var(--uui-success-60)',
}

const scoreColors: Record<string, string> = {
  critical: 'var(--uui-critical-70)',
  medium: 'var(--uui-warning-70)',
  stable: 'var(--uui-success-70)',
}

const SMEList = () => {
  const dispatch = useDispatch()
  const { smes, selectedSME, filter, searchQuery } = usePortfolio()
  const [localSearch, setLocalSearch] = useState(searchQuery)

  const handleSearch = (e: React.ChangeEvent<HTMLInputElement>) => {
    setLocalSearch(e.target.value)
    dispatch(setSearchQuery(e.target.value))
  }

  const CATEGORY_CONFIG = {
    critical: { icon: '🚨', label: 'Critical Risk', badge: 'Requires Action', badgeColor: 'var(--uui-critical-60)' },
    medium: { icon: '⚠️', label: 'Medium Risk', badge: 'Monitor Closely', badgeColor: 'var(--uui-warning-60)' },
    stable: { icon: '✅', label: 'Low Risk', badge: 'Stable', badgeColor: 'var(--uui-primary-60)' },
  }
  const config = CATEGORY_CONFIG[filter as keyof typeof CATEGORY_CONFIG] ?? CATEGORY_CONFIG.critical

  return (
    <div style={{
      background: 'var(--uui-surface-main)',
      border: '1px solid var(--uui-neutral-60)',
      borderRadius: 'var(--uui-border-radius)',
      height: 'calc(100vh - 320px)',
      display: 'flex', flexDirection: 'column',
    }}>
      {/* Header */}
      <div style={{ padding: '12px 18px', borderBottom: '1px solid var(--uui-neutral-60)', background: 'var(--uui-neutral-70)' }}>
        <div style={{ fontSize: '14px', fontWeight: 600, marginBottom: '12px', color: 'var(--uui-text-primary)' }}>
          {config.icon} {config.label} SMEs ({smes.length})
          <span style={{ marginLeft: '8px', fontSize: '11px', background: config.badgeColor, color: 'white', padding: '2px 8px', borderRadius: 'var(--uui-border-radius)' }}>
            {config.badge}
          </span>
        </div>
        <div style={{ position: 'relative' }}>
          <Search size={14} style={{ position: 'absolute', left: '10px', top: '50%', transform: 'translateY(-50%)', color: 'var(--uui-text-tertiary)' }} />
          <input
            type="text"
            placeholder="Search SME by name or client ID..."
            value={localSearch}
            onChange={handleSearch}
            style={{
              width: '100%', paddingLeft: '32px', paddingRight: '12px',
              paddingTop: '6px', paddingBottom: '6px',
              background: 'var(--uui-neutral-80)',
              border: '1px solid var(--uui-neutral-60)',
              borderRadius: 'var(--uui-border-radius)',
              color: 'var(--uui-text-primary)',
              fontSize: '13px', outline: 'none',
              fontFamily: 'var(--uui-font)',
            }}
          />
        </div>
      </div>

      {/* List */}
      <div style={{ flex: 1, overflowY: 'auto', padding: '9px' }}>
        {smes.length === 0 ? (
          <div style={{ textAlign: 'center', padding: '48px', color: 'var(--uui-text-tertiary)' }}>
            No SMEs found matching your criteria
          </div>
        ) : (
          smes.map((sme) => (
            <div
              key={sme.id}
              onClick={() => dispatch(setSelectedSME(sme))}
              style={{
                background: 'var(--uui-neutral-70)',
                border: `1px solid ${selectedSME?.id === sme.id ? 'var(--uui-primary-60)' : 'var(--uui-neutral-60)'}`,
                borderLeft: `3px solid ${riskColors[sme.riskCategory]}`,
                borderRadius: 'var(--uui-border-radius)',
                padding: '12px',
                marginBottom: '9px',
                cursor: 'pointer',
                boxShadow: selectedSME?.id === sme.id ? '0 0 0 2px rgba(72,164,208,0.2)' : 'none',
                transition: 'all 0.2s',
              }}
            >
              <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '9px' }}>
                <div>
                  <div style={{ fontSize: '11px', color: 'var(--uui-text-tertiary)', fontFamily: 'var(--uui-font-mono)' }}>{sme.id}</div>
                  <div style={{ fontWeight: 600, fontSize: '13px', margin: '3px 0', color: 'var(--uui-text-primary)' }}>{sme.name}</div>
                </div>
                <div style={{ textAlign: 'right' }}>
                  <div style={{ fontSize: '10px', color: 'var(--uui-text-tertiary)', fontWeight: 400, marginBottom: '2px' }}>Risk Score</div>
                  <div style={{ fontSize: '20px', fontWeight: 700, fontFamily: 'var(--uui-font-mono)', color: scoreColors[sme.riskCategory] }}>
                    {sme.riskScore}
                  </div>
                </div>
              </div>
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: '9px', fontSize: '11px' }}>
                <div>
                  <div style={{ color: 'var(--uui-text-tertiary)' }}>Credit Line</div>
                  <div style={{ fontWeight: 600, color: 'var(--uui-text-primary)' }}>{sme.exposure}</div>
                </div>
                <div>
                  <div style={{ color: 'var(--uui-text-tertiary)' }}>Drawn Credit</div>
                  <div style={{ fontWeight: 600, color: 'var(--uui-text-primary)' }}>{sme.drawnAmount}</div>
                </div>
                <div>
                  <div style={{ color: 'var(--uui-text-tertiary)' }}>Sector</div>
                  <div style={{ fontWeight: 600, color: 'var(--uui-text-primary)' }}>{sme.sector}</div>
                </div>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  )
}

export default SMEList