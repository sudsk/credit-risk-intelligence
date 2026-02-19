import { useState } from 'react'
import { Shield, TrendingDown, Clock } from 'lucide-react'
import { Button } from '../common/Button'
import type { ScenarioRecommendation } from '@/services/types'

interface RecommendationsTabsProps {
  recommendations: ScenarioRecommendation
  scenarioName: string
}

const tabs = [
  { id: 'ultraConservative' as const, label: 'Ultra-Conservative', color: 'var(--uui-critical-60)' },
  { id: 'conservative' as const, label: 'Conservative', color: 'var(--uui-warning-60)' },
  { id: 'moderate' as const, label: 'Moderate', color: 'var(--uui-primary-60)' },
]

const RecommendationsTabs = ({ recommendations, scenarioName }: RecommendationsTabsProps) => {
  const [activeTab, setActiveTab] = useState<'ultraConservative' | 'conservative' | 'moderate'>('conservative')

  const activeData = recommendations[activeTab]
  const activeColor = tabs.find(t => t.id === activeTab)?.color || 'var(--uui-primary-60)'

  return (
    <div style={{ background: 'var(--uui-neutral-70)', border: '1px solid var(--uui-neutral-60)', borderRadius: 'var(--uui-border-radius)', padding: '16px' }}>
      {/* Title */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '8px', fontSize: '12px', fontWeight: 600, color: 'var(--uui-text-tertiary)', textTransform: 'uppercase', marginBottom: '12px' }}>
        <Shield size={14} />
        Recommended Actions
      </div>

      {/* Tab Buttons */}
      <div style={{ display: 'flex', gap: '6px', marginBottom: '16px' }}>
        {tabs.map((tab) => {
          const isActive = activeTab === tab.id
          return (
            <button key={tab.id} onClick={() => setActiveTab(tab.id)} style={{
              flex: 1, padding: '8px', fontSize: '12px', fontWeight: 600,
              borderRadius: 'var(--uui-border-radius)',
              border: `2px solid ${tab.color}`,
              background: isActive ? tab.color : 'transparent',
              color: isActive ? 'white' : 'var(--uui-text-secondary)',
              cursor: 'pointer', transition: 'all 0.2s',
              fontFamily: 'var(--uui-font)',
            }}>
              {tab.label}
            </button>
          )
        })}
      </div>

      {/* Content */}
      {activeData && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '9px' }}>
          {/* Reserve Increase */}
          <div style={{ background: 'var(--uui-neutral-80)', border: '1px solid var(--uui-neutral-60)', borderRadius: 'var(--uui-border-radius)', padding: '12px', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <Shield size={16} style={{ color: 'var(--uui-text-tertiary)' }} />
              <span style={{ fontSize: '13px', fontWeight: 600, color: 'var(--uui-text-secondary)' }}>Reserve Increase</span>
            </div>
            <div style={{ textAlign: 'right' }}>
              <div style={{ fontSize: '22px', fontWeight: 700, color: activeColor, fontFamily: 'var(--uui-font-mono)' }}>
                {activeData.reserveIncrease}
              </div>
              <div style={{ fontSize: '11px', color: 'var(--uui-text-tertiary)' }}>{activeData.riskMitigation} risk coverage</div>
            </div>
          </div>

          {/* Sector Adjustments */}
          {activeData.sectorAdjustments.length > 0 && (
            <div style={{ background: 'var(--uui-neutral-80)', border: '1px solid var(--uui-neutral-60)', borderRadius: 'var(--uui-border-radius)', padding: '12px' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '9px' }}>
                <TrendingDown size={16} style={{ color: 'var(--uui-text-tertiary)' }} />
                <span style={{ fontSize: '13px', fontWeight: 600, color: 'var(--uui-text-secondary)' }}>Portfolio Adjustments</span>
              </div>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
                {activeData.sectorAdjustments.map((adj, idx) => (
                  <div key={idx} style={{ display: 'flex', alignItems: 'flex-start', gap: '8px', fontSize: '12px', color: 'var(--uui-text-secondary)' }}>
                    <span style={{ color: activeColor, marginTop: '2px', flexShrink: 0 }}>•</span>
                    <span>{adj}</span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Timeline */}
          <div style={{ background: 'var(--uui-neutral-80)', border: '1px solid var(--uui-neutral-60)', borderRadius: 'var(--uui-border-radius)', padding: '12px', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <Clock size={16} style={{ color: 'var(--uui-text-tertiary)' }} />
              <span style={{ fontSize: '13px', fontWeight: 600, color: 'var(--uui-text-secondary)' }}>Implementation Timeline</span>
            </div>
            <span style={{ fontSize: '13px', fontFamily: 'var(--uui-font-mono)', color: 'var(--uui-text-primary)' }}>
              {activeData.timeline}
            </span>
          </div>

          {/* Actions */}
          <div style={{ display: 'flex', gap: '9px', paddingTop: '4px' }}>
            <Button variant="primary" size="sm">
              📄 Export {tabs.find(t => t.id === activeTab)?.label} Plan
            </Button>
            <Button variant="secondary" size="sm">
              📋 Create Tasks from Actions
            </Button>
          </div>
        </div>
      )}
    </div>
  )
}

export default RecommendationsTabs