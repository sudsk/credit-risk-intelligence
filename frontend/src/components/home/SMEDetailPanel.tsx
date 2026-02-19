import { AlertCircle, TrendingUp, TrendingDown, Minus } from 'lucide-react'
import { useSelector } from 'react-redux'
import { RootState } from '@/store'
import { cn } from '@/utils/formatters'
import { Badge } from '../common/Badge'
import { Button } from '../common/Button'

const SMEDetailPanel = () => {
  const selectedSME = useSelector((state: RootState) => state.portfolio.selectedSME)

  if (!selectedSME) {
    return (
      <div className="bg-neutral-800 rounded-lg border border-neutral-600 shadow-sm h-[calc(100vh-320px)] flex items-center justify-center">
        <div className="text-center text-neutral-500">
          <div className="text-4xl mb-4">📊</div>
          <p className="text-lg font-medium">Select an SME to view details</p>
          <p className="text-sm mt-2">Click on any SME from the list to see comprehensive analysis</p>
        </div>
      </div>
    )
  }

  const getRiskBadgeVariant = (category: string) => {
    switch (category) {
      case 'critical':
        return 'critical'
      case 'medium':
        return 'warning'
      case 'stable':
        return 'success'
      default:
        return 'info'
    }
  }

  const getTrendIcon = (trend: string) => {
    switch (trend) {
      case 'up':
        return <TrendingUp className="w-4 h-4 text-critical-60" />
      case 'down':
        return <TrendingDown className="w-4 h-4 text-success-60" />
      default:
        return <Minus className="w-4 h-4 text-neutral-500" />
    }
  }

  // Mock detailed data (will come from API in real implementation)
  const detailedData = {
    financials: {
      revenue: '€2.4M',
      ebitda: '€420K',
      debtServiceCoverage: '1.8x',
      cashReserves: '€180K',
    },
    riskDrivers: [
      { label: 'CTO Departure', impact: '+6', source: 'LinkedIn' },
      { label: 'Web Traffic Decline -42%', impact: '+5', source: 'Google Analytics' },
      { label: 'Client Loss (2 major)', impact: '+3', source: 'CRM Data' },
    ],
    externalFactors: {
      sectorHealth: 'Medium Risk',
      geographyRisk: 'Low',
      compliance: 'Good Standing',
    },
  }

  return (
    <div className="bg-neutral-800 rounded-lg border border-neutral-600 shadow-sm h-[calc(100vh-320px)] overflow-y-auto">
      {/* Header */}
      <div className="sticky top-0 bg-neutral-800 border-b border-neutral-600 px-6 py-4 z-10">
        <div className="flex items-start justify-between">
          <div className="flex-1">
            <div className="flex items-center gap-3 mb-2">
              <span className="text-sm font-mono text-neutral-500">
                {selectedSME.id}
              </span>
              <Badge variant={getRiskBadgeVariant(selectedSME.riskCategory)}>
                {selectedSME.riskCategory.toUpperCase()}
              </Badge>
            </div>
            <h2 className="text-xl font-bold text-neutral-50">
              {selectedSME.name}
            </h2>
            <div className="flex items-center gap-4 mt-2 text-sm text-neutral-600">
              <span>💼 {selectedSME.sector}</span>
              <span>📍 {selectedSME.geography}</span>
              <span className="font-mono font-semibold">{selectedSME.exposure}</span>
            </div>
          </div>

          <div className="text-right">
            <div className="text-4xl font-bold text-neutral-50">
              {selectedSME.riskScore}
            </div>
            <div className="flex items-center justify-end gap-1 mt-1">
              {getTrendIcon(selectedSME.trend)}
              <span className={cn(
                'text-sm font-mono font-semibold',
                selectedSME.trend === 'up' && 'text-critical-60',
                selectedSME.trend === 'down' && 'text-success-60',
                selectedSME.trend === 'stable' && 'text-neutral-500'
              )}>
                {selectedSME.trendValue > 0 ? '+' : ''}{selectedSME.trendValue} this quarter
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* Content */}
      <div className="p-6 space-y-6">
        {/* Risk Drivers */}
        <section>
          <h3 className="text-sm font-semibold text-neutral-700 uppercase mb-3 flex items-center gap-2">
            <AlertCircle className="w-4 h-4" />
            Key Risk Drivers
          </h3>
          <div className="space-y-2">
            {detailedData.riskDrivers.map((driver, idx) => (
              <div
                key={idx}
                className="flex items-center justify-between p-3 bg-neutral-700 rounded border border-neutral-200"
              >
                <div className="flex-1">
                  <div className="font-medium text-sm text-neutral-50">
                    {driver.label}
                  </div>
                  <div className="text-xs text-neutral-500 mt-1">
                    Source: {driver.source}
                  </div>
                </div>
                <div className="text-right">
                  <span className="text-lg font-bold text-critical-60">
                    {driver.impact}
                  </span>
                  <div className="text-xs text-neutral-500">points</div>
                </div>
              </div>
            ))}
          </div>
        </section>

        {/* Financial Metrics */}
        <section>
          <h3 className="text-sm font-semibold text-neutral-700 uppercase mb-3">
            Financial Metrics
          </h3>
          <div className="grid grid-cols-2 gap-4">
            <div className="p-3 bg-neutral-700 rounded border border-neutral-200">
              <div className="text-xs text-neutral-500 mb-1">Annual Revenue</div>
              <div className="text-lg font-bold text-neutral-50">
                {detailedData.financials.revenue}
              </div>
            </div>
            <div className="p-3 bg-neutral-700 rounded border border-neutral-200">
              <div className="text-xs text-neutral-500 mb-1">EBITDA</div>
              <div className="text-lg font-bold text-neutral-50">
                {detailedData.financials.ebitda}
              </div>
            </div>
            <div className="p-3 bg-neutral-700 rounded border border-neutral-200">
              <div className="text-xs text-neutral-500 mb-1">Debt Service Coverage</div>
              <div className="text-lg font-bold text-neutral-50">
                {detailedData.financials.debtServiceCoverage}
              </div>
            </div>
            <div className="p-3 bg-neutral-700 rounded border border-neutral-200">
              <div className="text-xs text-neutral-500 mb-1">Cash Reserves</div>
              <div className="text-lg font-bold text-neutral-50">
                {detailedData.financials.cashReserves}
              </div>
            </div>
          </div>
        </section>

        {/* External Risk Factors */}
        <section>
          <h3 className="text-sm font-semibold text-neutral-700 uppercase mb-3">
            External Risk Factors
          </h3>
          <div className="space-y-2">
            <div className="flex items-center justify-between p-3 bg-neutral-700 rounded border border-neutral-200">
              <span className="text-sm text-neutral-700">Sector Health</span>
              <Badge variant="warning">{detailedData.externalFactors.sectorHealth}</Badge>
            </div>
            <div className="flex items-center justify-between p-3 bg-neutral-700 rounded border border-neutral-200">
              <span className="text-sm text-neutral-700">Geography Risk</span>
              <Badge variant="success">{detailedData.externalFactors.geographyRisk}</Badge>
            </div>
            <div className="flex items-center justify-between p-3 bg-neutral-700 rounded border border-neutral-200">
              <span className="text-sm text-neutral-700">Compliance Status</span>
              <Badge variant="success">{detailedData.externalFactors.compliance}</Badge>
            </div>
          </div>
        </section>

        {/* Actions */}
        <section className="pt-4 border-t border-neutral-200">
          <div className="grid grid-cols-2 gap-3">
            <Button variant="primary" size="md">
              Create Task
            </Button>
            <Button variant="secondary" size="md">
              Run Scenario
            </Button>
            <Button variant="secondary" size="md" fullWidth className="col-span-2">
              View Full History
            </Button>
          </div>
        </section>
      </div>
    </div>
  )
}

export default SMEDetailPanel
