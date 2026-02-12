import { useState } from 'react'
import { Shield, TrendingDown, Clock, BarChart3 } from 'lucide-react'
import { Button } from '../common/Button'
import { cn } from '@/utils/formatters'
import type { ScenarioRecommendation } from '@/services/types'

interface RecommendationsTabsProps {
  recommendations: ScenarioRecommendation
  scenarioName: string
}

const RecommendationsTabs = ({ recommendations, scenarioName }: RecommendationsTabsProps) => {
  const [activeTab, setActiveTab] = useState<'ultra' | 'conservative' | 'moderate'>('conservative')

  const tabs = [
    {
      id: 'ultra' as const,
      label: 'Ultra-Conservative',
      color: 'critical',
      data: recommendations.ultraConservative,
    },
    {
      id: 'conservative' as const,
      label: 'Conservative',
      color: 'warning',
      data: recommendations.conservative,
    },
    {
      id: 'moderate' as const,
      label: 'Moderate',
      color: 'primary',
      data: recommendations.moderate,
    },
  ]

  const activeData = tabs.find(t => t.id === activeTab)?.data

  const handleExport = () => {
    console.log('Exporting recommendations for:', activeTab)
    // TODO: Implement PDF export
  }

  return (
    <div className="bg-neutral-50 rounded-lg border border-neutral-300 p-4">
      <h4 className="text-sm font-semibold text-neutral-700 uppercase mb-3 flex items-center gap-2">
        <Shield className="w-4 h-4" />
        Recommended Actions
      </h4>

      {/* Tabs */}
      <div className="flex gap-2 mb-4">
        {tabs.map((tab) => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id)}
            className={cn(
              'flex-1 px-4 py-2 text-sm font-semibold rounded transition-all border-2',
              activeTab === tab.id
                ? cn(
                    'text-white',
                    tab.color === 'critical' && 'bg-critical-60 border-critical-60',
                    tab.color === 'warning' && 'bg-warning-60 border-warning-60',
                    tab.color === 'primary' && 'bg-primary-60 border-primary-60'
                  )
                : cn(
                    'bg-white text-neutral-700 hover:bg-neutral-50',
                    tab.color === 'critical' && 'border-critical-60',
                    tab.color === 'warning' && 'border-warning-60',
                    tab.color === 'primary' && 'border-primary-60'
                  )
            )}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {/* Content */}
      {activeData && (
        <div className="space-y-4">
          {/* Reserve Increase */}
          <div className="bg-white p-4 rounded border border-neutral-200">
            <div className="flex items-start justify-between mb-2">
              <div className="flex items-center gap-2">
                <Shield className="w-5 h-5 text-neutral-600" />
                <span className="font-semibold text-sm text-neutral-700">
                  Reserve Increase
                </span>
              </div>
              <div className="text-right">
                <div className="text-2xl font-bold text-neutral-800">
                  {activeData.reserveIncrease}
                </div>
                <div className="text-xs text-neutral-500">
                  {activeData.riskMitigation} risk coverage
                </div>
              </div>
            </div>
          </div>

          {/* Sector Adjustments */}
          {activeData.sectorAdjustments.length > 0 && (
            <div className="bg-white p-4 rounded border border-neutral-200">
              <div className="flex items-center gap-2 mb-3">
                <TrendingDown className="w-5 h-5 text-neutral-600" />
                <span className="font-semibold text-sm text-neutral-700">
                  Portfolio Adjustments
                </span>
              </div>
              <ul className="space-y-2">
                {activeData.sectorAdjustments.map((adjustment, idx) => (
                  <li
                    key={idx}
                    className="flex items-start gap-2 text-sm text-neutral-700"
                  >
                    <span className="text-primary-60 mt-0.5">•</span>
                    <span>{adjustment}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}

          {/* Timeline */}
          <div className="bg-white p-4 rounded border border-neutral-200">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <Clock className="w-5 h-5 text-neutral-600" />
                <span className="font-semibold text-sm text-neutral-700">
                  Implementation Timeline
                </span>
              </div>
              <span className="text-sm font-mono text-neutral-800">
                {activeData.timeline}
              </span>
            </div>
          </div>

          {/* Actions */}
          <div className="flex items-center gap-2 pt-2">
            <Button variant="primary" size="sm" onClick={handleExport}>
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
