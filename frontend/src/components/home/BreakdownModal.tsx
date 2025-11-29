import { X } from 'lucide-react'
import { useDispatch, useSelector } from 'react-redux'
import { RootState } from '@/store'
import { closeBreakdownModal } from '@/store/uiSlice'
import { setFilter } from '@/store/portfolioSlice'
import { setActiveTab } from '@/store/uiSlice'
import { Button } from '../common/Button'

// Mock breakdown data (will come from API in real implementation)
const breakdownData = {
  critical: {
    title: 'Critical Risk (80-100) - Detailed Breakdown',
    total: { smes: 23, exposure: '€42M', percent: '12.8%' },
    sectors: [
      { icon: '💻', name: 'Software/Technology', smes: 8, exposure: '€18M', percent: '6.2%' },
      { icon: '🛍️', name: 'Retail/Fashion', smes: 6, exposure: '€12M', percent: '4.1%' },
      { icon: '📢', name: 'Marketing Services', smes: 4, exposure: '€7M', percent: '2.4%' },
      { icon: '🍔', name: 'Food/Hospitality', smes: 3, exposure: '€3M', percent: '1.0%' },
      { icon: '📦', name: 'Other', smes: 2, exposure: '€2M', percent: '0.5%' },
    ],
    geographies: [
      { icon: '🇬🇧', name: 'UK', smes: 15, exposure: '€28M', percent: '9.6%' },
      { icon: '🇪🇺', name: 'EU', smes: 5, exposure: '€9M', percent: '3.1%' },
      { icon: '🇺🇸', name: 'NA', smes: 2, exposure: '€3M', percent: '1.0%' },
      { icon: '🌏', name: 'APAC', smes: 1, exposure: '€2M', percent: '0.7%' },
      { icon: '🌍', name: 'MEA', smes: 0, exposure: '€0M', percent: '0.0%' },
      { icon: '📍', name: 'Others', smes: 0, exposure: '€0M', percent: '0.0%' },
    ],
  },
  medium: {
    title: 'Medium Risk (50-79) - Detailed Breakdown',
    total: { smes: 142, exposure: '€98M', percent: '29.9%' },
    sectors: [
      { icon: '💻', name: 'Software/Technology', smes: 42, exposure: '€28M', percent: '9.6%' },
      { icon: '🛍️', name: 'Retail/Fashion', smes: 38, exposure: '€24M', percent: '8.2%' },
      { icon: '📢', name: 'Marketing Services', smes: 28, exposure: '€18M', percent: '6.2%' },
      { icon: '🏗️', name: 'Construction', smes: 18, exposure: '€14M', percent: '4.8%' },
      { icon: '📦', name: 'Other', smes: 16, exposure: '€14M', percent: '4.8%' },
    ],
    geographies: [
      { icon: '🇬🇧', name: 'UK', smes: 95, exposure: '€66M', percent: '22.6%' },
      { icon: '🇪🇺', name: 'EU', smes: 32, exposure: '€22M', percent: '7.5%' },
      { icon: '🇺🇸', name: 'NA', smes: 9, exposure: '€6M', percent: '2.1%' },
      { icon: '🌏', name: 'APAC', smes: 4, exposure: '€3M', percent: '1.0%' },
      { icon: '🌍', name: 'MEA', smes: 2, exposure: '€1M', percent: '0.3%' },
      { icon: '📍', name: 'Others', smes: 0, exposure: '€0M', percent: '0.0%' },
    ],
  },
  stable: {
    title: 'Low Risk (0-49) - Detailed Breakdown',
    total: { smes: 1119, exposure: '€188M', percent: '57.3%' },
    sectors: [
      { icon: '💻', name: 'Software/Technology', smes: 197, exposure: '€36M', percent: '11.0%' },
      { icon: '🛍️', name: 'Retail/Fashion', smes: 145, exposure: '€22M', percent: '6.7%' },
      { icon: '🍔', name: 'Food/Hospitality', smes: 131, exposure: '€35M', percent: '10.7%' },
      { icon: '📢', name: 'Marketing Services', smes: 124, exposure: '€16M', percent: '4.9%' },
      { icon: '🏗️', name: 'Construction', smes: 72, exposure: '€14M', percent: '4.3%' },
      { icon: '🏭', name: 'Manufacturing', smes: 64, exposure: '€18M', percent: '5.5%' },
      { icon: '📦', name: 'Other', smes: 386, exposure: '€47M', percent: '14.3%' },
    ],
    geographies: [
      { icon: '🇬🇧', name: 'UK', smes: 745, exposure: '€125M', percent: '38.1%' },
      { icon: '🇪🇺', name: 'EU', smes: 258, exposure: '€42M', percent: '12.8%' },
      { icon: '🇺🇸', name: 'NA', smes: 78, exposure: '€14M', percent: '4.3%' },
      { icon: '🌏', name: 'APAC', smes: 28, exposure: '€5M', percent: '1.5%' },
      { icon: '🌍', name: 'MEA', smes: 8, exposure: '€1M', percent: '0.3%' },
      { icon: '📍', name: 'Others', smes: 2, exposure: '€1M', percent: '0.3%' },
    ],
  },
}

const BreakdownModal = () => {
  const dispatch = useDispatch()
  const { breakdownModalOpen, breakdownModalData } = useSelector(
    (state: RootState) => state.ui
  )

  if (!breakdownModalOpen || !breakdownModalData) {
    return null
  }

  const { riskLevel } = breakdownModalData
  const data = breakdownData[riskLevel as keyof typeof breakdownData]

  const handleClose = () => {
    dispatch(closeBreakdownModal())
  }

  const handleViewSMEs = (filter: string) => {
    // Close modal and filter SME list
    dispatch(closeBreakdownModal())
    dispatch(setFilter(riskLevel))
    dispatch(setActiveTab('home'))
    // In real implementation, would also filter by sector/geography
  }

  return (
    <div
      className="fixed inset-0 bg-black bg-opacity-70 z-[100] flex items-center justify-center p-6"
      onClick={handleClose}
    >
      <div
        className="bg-white rounded-lg shadow-2xl max-w-3xl w-full max-h-[80vh] overflow-hidden flex flex-col"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header */}
        <div className="px-6 py-4 bg-neutral-100 border-b border-neutral-300 flex items-center justify-between">
          <h3 className="text-lg font-semibold text-neutral-800">{data.title}</h3>
          <button
            onClick={handleClose}
            className="w-8 h-8 rounded hover:bg-neutral-200 flex items-center justify-center transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Body */}
        <div className="flex-1 overflow-y-auto p-6">
          {/* Summary */}
          <div className="mb-6 p-4 bg-neutral-50 rounded border border-neutral-200">
            <div className="text-sm font-semibold text-neutral-700 mb-2">
              Total Portfolio Impact
            </div>
            <div className="text-xs text-neutral-600 font-mono">
              {data.total.smes} SMEs | {data.total.exposure} exposure | {data.total.percent} of portfolio
            </div>
          </div>

          {/* By Sector */}
          <div className="mb-6">
            <h4 className="text-xs font-semibold text-neutral-500 uppercase mb-3 pb-2 border-b border-neutral-200">
              By Sector
            </h4>
            <div className="space-y-2">
              {data.sectors.map((sector, idx) => (
                <div
                  key={idx}
                  className="flex items-center justify-between p-3 bg-neutral-50 rounded border border-neutral-200 hover:border-primary-60 transition-colors"
                >
                  <div>
                    <div className="font-semibold text-sm text-neutral-800 mb-1">
                      {sector.icon} {sector.name}
                    </div>
                    <div className="text-xs text-neutral-600 font-mono">
                      {sector.smes} SMEs | {sector.exposure} | {sector.percent} of portfolio
                    </div>
                  </div>
                  <Button
                    variant="primary"
                    size="sm"
                    onClick={() => handleViewSMEs(sector.name)}
                  >
                    View SMEs →
                  </Button>
                </div>
              ))}
            </div>
          </div>

          {/* By Geography */}
          <div>
            <h4 className="text-xs font-semibold text-neutral-500 uppercase mb-3 pb-2 border-b border-neutral-200">
              By Geography
            </h4>
            <div className="space-y-2">
              {data.geographies.map((geo, idx) => (
                <div
                  key={idx}
                  className="flex items-center justify-between p-3 bg-neutral-50 rounded border border-neutral-200 hover:border-primary-60 transition-colors"
                >
                  <div>
                    <div className="font-semibold text-sm text-neutral-800 mb-1">
                      {geo.icon} {geo.name}
                    </div>
                    <div className="text-xs text-neutral-600 font-mono">
                      {geo.smes} SMEs | {geo.exposure} | {geo.percent} of portfolio
                    </div>
                  </div>
                  <Button
                    variant="primary"
                    size="sm"
                    onClick={() => handleViewSMEs(geo.name)}
                  >
                    View SMEs →
                  </Button>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Footer */}
        <div className="px-6 py-4 bg-neutral-100 border-t border-neutral-300 flex items-center justify-end gap-3">
          <Button variant="secondary" size="md" onClick={handleClose}>
            Close
          </Button>
          <Button variant="secondary" size="md">
            Export Data
          </Button>
        </div>
      </div>
    </div>
  )
}

export default BreakdownModal
