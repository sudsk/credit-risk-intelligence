import { useEffect } from 'react'
import { useDispatch, useSelector } from 'react-redux'
import { X, AlertCircle, AlertTriangle } from 'lucide-react'
import { RootState } from '@/store'
import { dismissAlert, addToHistory } from '@/store/alertSlice'
import { setSelectedSME } from '@/store/portfolioSlice'
import { setActiveTab } from '@/store/uiSlice'
import { Button } from './Button'
import { cn } from '@/utils/formatters'

const AlertToast = () => {
  const dispatch = useDispatch()
  const { currentAlert, showAlert } = useSelector((state: RootState) => state.alerts)

  useEffect(() => {
    if (showAlert && currentAlert) {
      // Auto-dismiss after 10 seconds
      const timer = setTimeout(() => {
        handleDismiss()
      }, 10000)

      return () => clearTimeout(timer)
    }
  }, [showAlert, currentAlert])

  const handleDismiss = () => {
    if (currentAlert) {
      dispatch(addToHistory(currentAlert))
    }
    dispatch(dismissAlert())
  }

  const handleViewDetails = () => {
    if (!currentAlert) return

    // Create SME object and navigate
    const sme = {
      id: currentAlert.smeId,
      name: currentAlert.smeName,
      riskScore: 68, // Will be fetched from API in real implementation
      riskCategory: 'critical' as const,
      exposure: currentAlert.exposure,
      sector: 'Software/Technology',
      geography: 'UK',
      trend: 'up' as const,
      trendValue: 14,
    }

    dispatch(setSelectedSME(sme))
    dispatch(setActiveTab('home'))
    dispatch(dismissAlert())
  }

  if (!showAlert || !currentAlert) {
    return null
  }

  const getIcon = () => {
    return currentAlert.severity === 'critical' ? (
      <AlertCircle className="w-5 h-5 text-critical-60" />
    ) : (
      <AlertTriangle className="w-5 h-5 text-warning-60" />
    )
  }

  return (
    <div
      className={cn(
        'fixed top-20 right-6 z-[60] w-[420px] bg-white rounded-lg shadow-2xl border-l-4 animate-slideIn',
        currentAlert.severity === 'critical' ? 'border-l-critical-60' : 'border-l-warning-60'
      )}
    >
      {/* Header */}
      <div className="px-4 py-3 border-b border-neutral-200 flex items-center justify-between">
        <div className="flex items-center gap-2">
          {getIcon()}
          <span className="font-semibold text-sm text-neutral-800">
            {currentAlert.severity === 'critical' ? 'Critical Alert' : 'Warning Alert'}
          </span>
        </div>
        <button
          onClick={handleDismiss}
          className="w-6 h-6 rounded hover:bg-neutral-100 flex items-center justify-center transition-colors"
        >
          <X className="w-4 h-4 text-neutral-600" />
        </button>
      </div>

      {/* Body */}
      <div className="p-4">
        <div className="mb-3">
          <div className="text-xs font-mono text-neutral-500 mb-1">
            {currentAlert.smeId} • {currentAlert.exposure}
          </div>
          <h4 className="font-bold text-base text-neutral-800 mb-2">
            {currentAlert.smeName}
          </h4>
          <p className="text-sm text-neutral-700">{currentAlert.eventSummary}</p>
        </div>

        {/* Data Sources */}
        <div className="mb-4">
          <div className="text-xs font-semibold text-neutral-600 uppercase mb-2">
            Data Sources
          </div>
          <div className="flex flex-wrap gap-2">
            {currentAlert.dataSources.map((source, idx) => (
              <span
                key={idx}
                className="px-2 py-1 bg-neutral-100 text-neutral-700 text-xs rounded"
              >
                {source}
              </span>
            ))}
          </div>
        </div>

        {/* Actions */}
        <div className="flex items-center gap-2">
          <Button variant="primary" size="sm" onClick={handleViewDetails} fullWidth>
            View SME Details
          </Button>
          <Button variant="secondary" size="sm" onClick={handleDismiss}>
            Dismiss
          </Button>
        </div>
      </div>
    </div>
  )
}

export default AlertToast
