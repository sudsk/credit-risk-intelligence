import { useState } from 'react'
import { ChevronDown, ChevronUp, TrendingUp, TrendingDown } from 'lucide-react'
import { formatRelativeTime, formatPercent } from '@/utils/formatters'
import { Button } from '../common/Button'
import RecommendationsTabs from './RecommendationsTabs'
import type { Scenario } from '@/services/types'

interface ScenarioResultsProps {
  scenario: Scenario
}

const ScenarioResults = ({ scenario }: ScenarioResultsProps) => {
  const [expanded, setExpanded] = useState(false)

  // Mock results - in real app would come from scenario.results
  const mockResults = {
    portfolioImpact: {
      criticalBefore: 23,
      criticalAfter: 25,
      defaultProbBefore: 2.8,
      defaultProbAfter: 3.1,
      avgScoreBefore: 64,
      avgScoreAfter: 66,
    },
    sectorImpact: [
      { sector: 'Construction', smes: 8, avgChange: 8 },
      { sector: 'Retail', smes: 12, avgChange: 6 },
      { sector: 'Manufacturing', smes: 5, avgChange: 4 },
    ],
    topImpacted: [
      {
        smeId: '#0445',
        smeName: 'GreenLeaf Products',
        scoreBefore: 72,
        scoreAfter: 87,
        change: 15,
        reason: 'Revenue drop due to product ban',
      },
      {
        smeId: '#0672',
        smeName: 'Natural Wellness Ltd',
        scoreBefore: 68,
        scoreAfter: 82,
        change: 14,
        reason: 'Market contraction impact',
      },
    ],
  }

  const results = scenario.results || mockResults

  return (
    <div className="bg-white border border-neutral-300 rounded-lg overflow-hidden">
      {/* Header */}
      <div
        className="p-4 cursor-pointer hover:bg-neutral-50 transition-colors"
        onClick={() => setExpanded(!expanded)}
      >
        <div className="flex items-start justify-between">
          <div className="flex-1">
            <h4 className="text-base font-bold text-neutral-800 mb-1">{scenario.name}</h4>
            <div className="text-xs text-neutral-500">
              Completed {formatRelativeTime(scenario.completedAt!)} •{' '}
              Duration: {scenario.duration}s
            </div>
          </div>
          <div className="flex items-center gap-3">
            <div className="text-right">
              <div className="text-sm font-semibold text-neutral-700">
                Critical: {results.portfolioImpact.criticalBefore} → {results.portfolioImpact.criticalAfter}
              </div>
              <div className="text-xs text-critical-60">
                +{results.portfolioImpact.criticalAfter - results.portfolioImpact.criticalBefore} SMEs
              </div>
            </div>
            {expanded ? (
              <ChevronUp className="w-5 h-5 text-neutral-500" />
            ) : (
              <ChevronDown className="w-5 h-5 text-neutral-500" />
            )}
          </div>
        </div>
      </div>

      {/* Expanded Results */}
      {expanded && (
        <div className="border-t border-neutral-300 p-4 bg-neutral-50">
          {/* Portfolio Impact Summary */}
          <div className="mb-4">
            <h5 className="text-sm font-semibold text-neutral-700 uppercase mb-3">
              Portfolio Impact Summary
            </h5>
            <div className="grid grid-cols-3 gap-4">
              <div className="bg-white p-3 rounded border border-neutral-200">
                <div className="text-xs text-neutral-500 mb-1">Critical SMEs</div>
                <div className="text-lg font-bold text-neutral-800">
                  {results.portfolioImpact.criticalBefore} → {results.portfolioImpact.criticalAfter}
                </div>
                <div className="text-xs text-critical-60 flex items-center gap-1">
                  <TrendingUp className="w-3 h-3" />
                  +{results.portfolioImpact.criticalAfter - results.portfolioImpact.criticalBefore}
                </div>
              </div>
              <div className="bg-white p-3 rounded border border-neutral-200">
                <div className="text-xs text-neutral-500 mb-1">Default Probability</div>
                <div className="text-lg font-bold text-neutral-800">
                  {formatPercent(results.portfolioImpact.defaultProbBefore)} →{' '}
                  {formatPercent(results.portfolioImpact.defaultProbAfter)}
                </div>
                <div className="text-xs text-critical-60 flex items-center gap-1">
                  <TrendingUp className="w-3 h-3" />
                  +{formatPercent(
                    results.portfolioImpact.defaultProbAfter - results.portfolioImpact.defaultProbBefore
                  )}
                </div>
              </div>
              <div className="bg-white p-3 rounded border border-neutral-200">
                <div className="text-xs text-neutral-500 mb-1">Avg Risk Score</div>
                <div className="text-lg font-bold text-neutral-800">
                  {results.portfolioImpact.avgScoreBefore} → {results.portfolioImpact.avgScoreAfter}
                </div>
                <div className="text-xs text-warning-60 flex items-center gap-1">
                  <TrendingUp className="w-3 h-3" />
                  +{results.portfolioImpact.avgScoreAfter - results.portfolioImpact.avgScoreBefore}
                </div>
              </div>
            </div>
          </div>

          {/* ADD THIS: Recommendations Section */}
          {scenario.recommendations && (
            <div className="mb-4">
              <RecommendationsTabs
                recommendations={scenario.recommendations}
                scenarioName={scenario.name}
              />
            </div>
          )}
          
          {/* Top Impacted SMEs */}
          <div className="mb-4">
            <h5 className="text-sm font-semibold text-neutral-700 uppercase mb-3">
              Top Impacted SMEs
            </h5>
            <div className="space-y-2">
              {results.topImpacted.map((sme, idx) => (
                <div
                  key={idx}
                  className="bg-white p-3 rounded border border-neutral-200 flex items-center justify-between"
                >
                  <div className="flex-1">
                    <div className="font-semibold text-sm text-neutral-800 mb-1">
                      {sme.smeId} {sme.smeName}
                    </div>
                    <div className="text-xs text-neutral-600">{sme.reason}</div>
                  </div>
                  <div className="text-right">
                    <div className="text-sm font-mono text-neutral-700">
                      {sme.scoreBefore} → {sme.scoreAfter}
                    </div>
                    <div className="text-xs text-critical-60 font-semibold">+{sme.change}</div>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Actions */}
          <div className="flex items-center gap-2">
            <Button variant="primary" size="sm">
              📋 Create Tasks for Top SMEs
            </Button>
            <Button variant="secondary" size="sm">
              📊 Export Full Report
            </Button>
            <Button variant="secondary" size="sm">
              🗑️ Delete Scenario
            </Button>
          </div>
        </div>
      )}
    </div>
  )
}

export default ScenarioResults
