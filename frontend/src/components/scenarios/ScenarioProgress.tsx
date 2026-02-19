import { Loader } from 'lucide-react'
import { formatRelativeTime } from '@/utils/formatters'
import type { Scenario } from '@/services/types'

interface ScenarioProgressProps {
  scenario: Scenario
}

const ScenarioProgress = ({ scenario }: ScenarioProgressProps) => {
  const progress = scenario.progress || 0

  return (
    <div style={{
      background: 'var(--uui-neutral-70)',
      border: `1px solid var(--uui-neutral-60)`,
      borderLeft: '3px solid var(--uui-primary-60)',
      borderRadius: 'var(--uui-border-radius)',
      padding: '16px',
    }}>
      <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', marginBottom: '12px' }}>
        <div style={{ flex: 1 }}>
          <div style={{ fontSize: '14px', fontWeight: 700, color: 'var(--uui-text-primary)', marginBottom: '4px' }}>
            {scenario.name}
          </div>
          <div style={{ fontSize: '11px', color: 'var(--uui-text-tertiary)' }}>
            Started {formatRelativeTime(scenario.createdAt)}
          </div>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', color: 'var(--uui-primary-60)' }}>
          <Loader size={18} style={{ animation: 'spin 1s linear infinite' }} />
          <span style={{ fontSize: '13px', fontWeight: 600, fontFamily: 'var(--uui-font-mono)' }}>{progress}%</span>
        </div>
      </div>

      {/* Progress Bar */}
      <div style={{ width: '100%', height: '6px', background: 'var(--uui-neutral-60)', borderRadius: '3px', overflow: 'hidden', marginBottom: '8px' }}>
        <div style={{ height: '100%', width: `${progress}%`, background: 'var(--uui-primary-60)', transition: 'width 0.5s ease', borderRadius: '3px' }} />
      </div>

      <div style={{ fontSize: '11px', color: 'var(--uui-text-tertiary)' }}>
        Processing {Math.floor((progress / 100) * 1284).toLocaleString()} / 1,284 SMEs...
      </div>
    </div>
  )
}

export default ScenarioProgress