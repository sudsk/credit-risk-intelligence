import { Info } from 'lucide-react'
import { useDispatch } from 'react-redux'
import { usePortfolio } from '@/hooks/usePortfolio'
import { openBreakdownModal } from '@/store/uiSlice'
import { setFilter } from '@/store/portfolioSlice'
import { cn, formatCurrency, formatPercent } from '@/utils/formatters'

const PortfolioMetrics = () => {
  const dispatch = useDispatch()
  const { metrics, isLoading } = usePortfolio()

  if (isLoading || !metrics) {
    return <div className="text-center py-12">Loading portfolio metrics...</div>
  }

  const handleCardClick = (filter: 'critical' | 'medium' | 'stable') => {
    dispatch(setFilter(filter))
  }

  const handleInfoClick = (
    e: React.MouseEvent,
    riskLevel: 'critical' | 'medium' | 'stable'
  ) => {
    e.stopPropagation()
    // This will be implemented with breakdown data
    dispatch(openBreakdownModal({ riskLevel }))
  }

  return (
    <div className="grid grid-cols-5 gap-4">
      {/* Critical Risk */}
      <div
        onClick={() => handleCardClick('critical')}
        className="relative bg-neutral-800 rounded-lg border-2 border-critical-60 p-4 cursor-pointer hover:shadow-lg transition-shadow"
      >
        <button
          onClick={(e) => handleInfoClick(e, 'critical')}
          className="absolute top-4 right-4 w-6 h-6 rounded-full bg-neutral-300 hover:bg-primary-60 hover:text-white transition-all flex items-center justify-center"
          title="View breakdown"
        >
          <Info className="w-3.5 h-3.5" />
        </button>

        <div className="text-sm text-neutral-600 mb-1">Critical Risk (80-100)</div>
        <div className="text-3xl font-bold text-critical-60 mb-2">
          {metrics.criticalCount}
        </div>
        <div className="text-xs text-neutral-500 font-mono">
          €42M | 12.8% | <span className="text-critical-60">↑ 5</span>
        </div>
      </div>

      {/* Medium Risk */}
      <div
        onClick={() => handleCardClick('medium')}
        className="relative bg-white rounded-lg border-2 border-warning-60 p-4 cursor-pointer hover:shadow-lg transition-shadow"
      >
        <button
          onClick={(e) => handleInfoClick(e, 'medium')}
          className="absolute top-4 right-4 w-6 h-6 rounded-full bg-neutral-300 hover:bg-primary-60 hover:text-white transition-all flex items-center justify-center"
          title="View breakdown"
        >
          <Info className="w-3.5 h-3.5" />
        </button>

        <div className="text-sm text-neutral-600 mb-1">Medium Risk (50-79)</div>
        <div className="text-3xl font-bold text-warning-60 mb-2">
          {metrics.mediumCount}
        </div>
        <div className="text-xs text-neutral-500 font-mono">
          €98M | 29.9% | <span className="text-warning-60">↑ 8</span>
        </div>
      </div>

      {/* Low Risk */}
      <div
        onClick={() => handleCardClick('stable')}
        className="relative bg-white rounded-lg border-2 border-success-60 p-4 cursor-pointer hover:shadow-lg transition-shadow"
      >
        <button
          onClick={(e) => handleInfoClick(e, 'stable')}
          className="absolute top-4 right-4 w-6 h-6 rounded-full bg-neutral-300 hover:bg-primary-60 hover:text-white transition-all flex items-center justify-center"
          title="View breakdown"
        >
          <Info className="w-3.5 h-3.5" />
        </button>

        <div className="text-sm text-neutral-600 mb-1">Low Risk (0-49)</div>
        <div className="text-3xl font-bold text-success-60 mb-2">
          {metrics.stableCount}
        </div>
        <div className="text-xs text-neutral-500 font-mono">
          €188M | 57.3% | <span className="text-success-60">↓ 13</span>
        </div>
      </div>

      {/* Total Portfolio */}
      <div className="bg-white rounded-lg border border-neutral-300 p-4">
        <div className="text-sm text-neutral-600 mb-1">Total Portfolio</div>
        <div className="text-3xl font-bold text-neutral-800 mb-2">
          {metrics.totalSMEs}
        </div>
        <div className="text-xs text-neutral-500 font-mono">
          {formatCurrency(metrics.totalExposure)}
        </div>
      </div>

      {/* Default Probability */}
      <div className="bg-white rounded-lg border border-neutral-300 p-4">
        <div className="text-sm text-neutral-600 mb-1">Default Probability</div>
        <div className="text-3xl font-bold text-neutral-800 mb-2">
          {formatPercent(metrics.defaultProbability)}
        </div>
        <div className="text-xs text-neutral-500 font-mono">
          Avg Score: {metrics.avgRiskScore}
        </div>
      </div>
    </div>
  )
}

export default PortfolioMetrics
