import { useState } from 'react'
import { Search, Filter } from 'lucide-react'
import { useDispatch } from 'react-redux'
import { usePortfolio } from '@/hooks/usePortfolio'
import { setSelectedSME, setSearchQuery } from '@/store/portfolioSlice'
import { cn, getRiskCategory } from '@/utils/formatters'

const SMEList = () => {
  const dispatch = useDispatch()
  const { smes, selectedSME, filter, searchQuery } = usePortfolio()
  const [localSearch, setLocalSearch] = useState(searchQuery)

  const handleSearchChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value
    setLocalSearch(value)
    dispatch(setSearchQuery(value))
  }

  const handleSMEClick = (sme: typeof smes[0]) => {
    dispatch(setSelectedSME(sme))
  }

  const getRiskColor = (category: string) => {
    switch (category) {
      case 'critical':
        return 'border-critical-60 bg-critical-50'
      case 'medium':
        return 'border-warning-60 bg-warning-50'
      case 'stable':
        return 'border-success-60 bg-success-50'
      default:
        return 'border-neutral-300 bg-white'
    }
  }

  const getTrendIcon = (trend: string) => {
    switch (trend) {
      case 'up':
        return <span className="text-critical-60">↑</span>
      case 'down':
        return <span className="text-success-60">↓</span>
      default:
        return <span className="text-neutral-500">→</span>
    }
  }

  return (
    <div className="bg-white rounded-lg border border-neutral-300 shadow-sm h-[calc(100vh-320px)] flex flex-col">
      {/* Header */}
      <div className="px-4 py-3 border-b border-neutral-300">
        <h2 className="text-lg font-semibold text-neutral-800 mb-3">
          SME Portfolio
          <span className="ml-2 text-sm font-normal text-neutral-500">
            ({smes.length} {filter !== 'all' ? filter : 'total'})
          </span>
        </h2>

        {/* Search */}
        <div className="relative">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-neutral-400" />
          <input
            type="text"
            placeholder="Search by ID, name, or sector..."
            value={localSearch}
            onChange={handleSearchChange}
            className="w-full pl-10 pr-4 py-2 text-sm border border-neutral-300 rounded focus:outline-none focus:ring-2 focus:ring-primary-60"
          />
        </div>
      </div>

      {/* SME List */}
      <div className="flex-1 overflow-y-auto">
        {smes.length === 0 ? (
          <div className="text-center py-12 text-neutral-500">
            No SMEs found matching your criteria
          </div>
        ) : (
          <div className="p-2 space-y-2">
            {smes.map((sme) => (
              <div
                key={sme.id}
                onClick={() => handleSMEClick(sme)}
                className={cn(
                  'p-3 rounded border-2 cursor-pointer transition-all',
                  getRiskColor(sme.riskCategory),
                  selectedSME?.id === sme.id
                    ? 'ring-2 ring-primary-60 shadow-md'
                    : 'hover:shadow-md'
                )}
              >
                {/* SME Header */}
                <div className="flex items-start justify-between mb-2">
                  <div className="flex-1">
                    <div className="flex items-center gap-2">
                      <span className="text-xs font-mono text-neutral-500">
                        {sme.id}
                      </span>
                      {getTrendIcon(sme.trend)}
                      <span className="text-xs font-mono text-neutral-500">
                        {sme.trendValue > 0 ? '+' : ''}{sme.trendValue}
                      </span>
                    </div>
                    <h3 className="font-semibold text-sm text-neutral-800 mt-1">
                      {sme.name}
                    </h3>
                  </div>
                  <div className="text-right">
                    <div className="text-xl font-bold text-neutral-800">
                      {sme.riskScore}
                    </div>
                    <div className="text-xs text-neutral-500">Score</div>
                  </div>
                </div>

                {/* SME Details */}
                <div className="flex items-center justify-between text-xs text-neutral-600">
                  <div className="flex items-center gap-3">
                    <span>💼 {sme.sector}</span>
                    <span>📍 {sme.geography}</span>
                  </div>
                  <div className="font-mono font-semibold">
                    {sme.exposure}
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}

export default SMEList
