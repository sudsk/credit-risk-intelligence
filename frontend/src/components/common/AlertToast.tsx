import { useEffect } from 'react'
import { useDispatch, useSelector } from 'react-redux'
import { X, AlertCircle, AlertTriangle } from 'lucide-react'
import { RootState } from '@/store'
import { dismissAlert, addToHistory } from '@/store/alertSlice'
import { setSelectedSME } from '@/store/portfolioSlice'
import { setActiveTab } from '@/store/uiSlice'
import { Button } from './Button'

const AlertToast = () => {
  const dispatch = useDispatch()
  const { currentAlert, showAlert } = useSelector((state: RootState) => state.alerts)

  useEffect(() => {
    if (showAlert && currentAlert) {
      const timer = setTimeout(() => handleDismiss(), 10000)
      return () => clearTimeout(timer)
    }
  }, [showAlert, currentAlert])

  const handleDismiss = () => {
    if (currentAlert) dispatch(addToHistory(currentAlert))
    dispatch(dismissAlert())
  }

  const handleViewDetails = () => {
    if (!currentAlert) return
    const sme = {
      id: currentAlert.smeId,
      name: currentAlert.smeName,
      riskScore: 68,
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

  if (!showAlert || !currentAlert) return null

  const isCritical = currentAlert.severity === 'critical'
  const accentColor = isCritical ? 'var(--uui-critical-60)' : 'var(--uui-warning-60)'

  return (
    <div style={{
      position: 'fixed', top: '72px', right: '24px', zIndex: 60,
      width: '420px',
      background: 'var(--uui-surface-main)',
      border: '1px solid var(--uui-neutral-60)',
      borderLeft: `4px solid ${accentColor}`,
      borderRadius: 'var(--uui-border-radius)',
      boxShadow: 'var(--uui-shadow-level-3)',
      animation: 'slideIn 0.3s ease-out',
    }}>
      {/* Header */}
      <div style={{ padding: '12px 18px', borderBottom: '1px solid var(--uui-neutral-60)', background: 'var(--uui-neutral-70)', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          {isCritical
            ? <AlertCircle size={16} style={{ color: 'var(--uui-critical-60)' }} />
            : <AlertTriangle size={16} style={{ color: 'var(--uui-warning-60)' }} />}
          <span style={{ fontSize: '13px', fontWeight: 600, color: 'var(--uui-text-primary)' }}>
            {isCritical ? 'Critical Alert' : 'Warning Alert'}
          </span>
        </div>
        <button onClick={handleDismiss} style={{ width: '24px', height: '24px', borderRadius: 'var(--uui-border-radius)', background: 'var(--uui-neutral-60)', border: 'none', cursor: 'pointer', display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'var(--uui-text-primary)' }}>
          <X size={14} />
        </button>
      </div>

      {/* Body */}
      <div style={{ padding: '18px' }}>
        <div style={{ marginBottom: '12px' }}>
          <div style={{ fontSize: '11px', fontFamily: 'var(--uui-font-mono)', color: 'var(--uui-text-tertiary)', marginBottom: '6px' }}>
            {currentAlert.smeId} • {currentAlert.exposure}
          </div>
          <h4 style={{ fontSize: '14px', fontWeight: 700, color: 'var(--uui-text-primary)', marginBottom: '6px' }}>
            {currentAlert.smeName}
          </h4>
          <p style={{ fontSize: '13px', color: 'var(--uui-text-secondary)' }}>{currentAlert.eventSummary}</p>
        </div>

        {/* Data Sources */}
        <div style={{ marginBottom: '18px' }}>
          <div style={{ fontSize: '11px', fontWeight: 600, color: 'var(--uui-text-tertiary)', textTransform: 'uppercase', marginBottom: '9px' }}>
            Data Sources
          </div>
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px' }}>
            {currentAlert.dataSources.map((source, idx) => (
              <span key={idx} style={{ padding: '3px 9px', background: 'var(--uui-neutral-70)', border: '1px solid var(--uui-neutral-60)', borderRadius: 'var(--uui-border-radius)', fontSize: '11px', color: 'var(--uui-text-secondary)' }}>
                {source}
              </span>
            ))}
          </div>
        </div>

        {/* Actions */}
        <div style={{ display: 'flex', gap: '9px' }}>
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