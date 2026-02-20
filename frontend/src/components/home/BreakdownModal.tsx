import { X, Loader } from 'lucide-react'
import { useState, useEffect } from 'react'
import { useDispatch, useSelector } from 'react-redux'
import { RootState } from '@/store'
import { closeBreakdownModal } from '@/store/uiSlice'
import { setFilter } from '@/store/portfolioSlice'
import { setActiveTab } from '@/store/uiSlice'
import { Button } from '../common/Button'
import { portfolioAPI } from '@/services/api'

const BreakdownModal = () => {
  const dispatch = useDispatch()
  const { breakdownModalOpen, breakdownModalData } = useSelector((state: RootState) => state.ui)
  const [breakdownData, setBreakdownData] = useState<any>(null)
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const riskLevel = breakdownModalData?.riskLevel

  useEffect(() => {
    if (!breakdownModalOpen || !riskLevel) return
    setIsLoading(true)
    setError(null)
    portfolioAPI.getBreakdownData(riskLevel)
      .then(setBreakdownData)
      .catch((err) => setError(err.message || 'Failed to load breakdown data'))
      .finally(() => setIsLoading(false))
  }, [breakdownModalOpen, riskLevel])

  if (!breakdownModalOpen || !breakdownModalData) return null

  const handleClose = () => {
    setBreakdownData(null)
    dispatch(closeBreakdownModal())
  }
  const handleViewSMEs = () => {
    dispatch(closeBreakdownModal())
    dispatch(setFilter(riskLevel))
    dispatch(setActiveTab('home'))
  }

  const rowStyle: React.CSSProperties = {
    display: 'flex', alignItems: 'center', justifyContent: 'space-between',
    padding: '12px', marginBottom: '6px',
    background: 'var(--uui-neutral-70)',
    border: '1px solid var(--uui-neutral-60)',
    borderRadius: 'var(--uui-border-radius)',
  }

  const sectionTitle = (text: string) => (
    <div style={{
      fontSize: '11px', fontWeight: 600, color: 'var(--uui-text-tertiary)',
      textTransform: 'uppercase', marginBottom: '12px', paddingBottom: '9px',
      borderBottom: '1px solid var(--uui-neutral-60)',
    }}>
      {text}
    </div>
  )

  return (
    <div
      style={{ position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.7)', zIndex: 100, display: 'flex', alignItems: 'center', justifyContent: 'center', padding: '24px' }}
      onClick={handleClose}
    >
      <div
        style={{ background: 'var(--uui-surface-main)', borderRadius: 'var(--uui-border-radius)', border: '1px solid var(--uui-neutral-60)', boxShadow: 'var(--uui-shadow-level-3)', maxWidth: '760px', width: '100%', maxHeight: '80vh', overflow: 'hidden', display: 'flex', flexDirection: 'column' }}
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header */}
        <div style={{ padding: '12px 18px', background: 'var(--uui-neutral-70)', borderBottom: '1px solid var(--uui-neutral-60)', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <h3 style={{ fontSize: '14px', fontWeight: 600, color: 'var(--uui-text-primary)' }}>
            {breakdownData?.title ?? `${riskLevel?.charAt(0).toUpperCase()}${riskLevel?.slice(1)} Risk — Detailed Breakdown`}
          </h3>
          <button onClick={handleClose} style={{ width: '28px', height: '28px', borderRadius: 'var(--uui-border-radius)', background: 'var(--uui-neutral-60)', border: 'none', cursor: 'pointer', display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'var(--uui-text-primary)' }}>
            <X size={16} />
          </button>
        </div>

        {/* Body */}
        <div style={{ flex: 1, overflowY: 'auto', padding: '18px' }}>

          {/* Loading */}
          {isLoading && (
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', padding: '48px', gap: '12px' }}>
              <Loader size={20} style={{ animation: 'spin 1s linear infinite', color: 'var(--uui-primary-60)' }} />
              <span style={{ fontSize: '13px', color: 'var(--uui-text-tertiary)' }}>Loading breakdown data...</span>
            </div>
          )}

          {/* Error */}
          {error && !isLoading && (
            <div style={{ padding: '12px', background: 'rgba(229,98,72,0.1)', border: '1px solid var(--uui-critical-60)', borderRadius: 'var(--uui-border-radius)' }}>
              <p style={{ fontSize: '13px', color: 'var(--uui-critical-60)' }}>⚠️ {error}</p>
            </div>
          )}

          {/* Content */}
          {breakdownData && !isLoading && (
            <>
              {/* Summary */}
              <div style={{ marginBottom: '18px', padding: '12px', background: 'var(--uui-neutral-70)', borderRadius: 'var(--uui-border-radius)', border: '1px solid var(--uui-neutral-60)' }}>
                <div style={{ fontSize: '12px', fontWeight: 600, color: 'var(--uui-text-secondary)', marginBottom: '6px' }}>Total Portfolio Impact</div>
                <div style={{ fontSize: '12px', color: 'var(--uui-text-tertiary)', fontFamily: 'var(--uui-font-mono)' }}>
                  {breakdownData.total.smes} SMEs | {breakdownData.total.exposure} exposure | {breakdownData.total.percent} of portfolio
                </div>
              </div>

              {/* By Sector */}
              <div style={{ marginBottom: '18px' }}>
                {sectionTitle('By Sector')}
                {breakdownData.sectors.map((sector: any, idx: number) => (
                  <div key={idx} style={rowStyle}>
                    <div>
                      <div style={{ fontSize: '13px', fontWeight: 600, color: 'var(--uui-text-primary)', marginBottom: '3px' }}>
                        {sector.icon} {sector.name}
                      </div>
                      <div style={{ fontSize: '11px', color: 'var(--uui-text-tertiary)', fontFamily: 'var(--uui-font-mono)' }}>
                        {sector.smes} SMEs | {sector.exposure} | {sector.percent} of portfolio
                      </div>
                    </div>
                    <Button variant="primary" size="sm" onClick={handleViewSMEs}>View SMEs →</Button>
                  </div>
                ))}
              </div>

              {/* By Geography */}
              <div>
                {sectionTitle('By Geography')}
                {breakdownData.geographies.map((geo: any, idx: number) => (
                  <div key={idx} style={rowStyle}>
                    <div>
                      <div style={{ fontSize: '13px', fontWeight: 600, color: 'var(--uui-text-primary)', marginBottom: '3px' }}>
                        {geo.icon} {geo.name}
                      </div>
                      <div style={{ fontSize: '11px', color: 'var(--uui-text-tertiary)', fontFamily: 'var(--uui-font-mono)' }}>
                        {geo.smes} SMEs | {geo.exposure} | {geo.percent} of portfolio
                      </div>
                    </div>
                    <Button variant="primary" size="sm" onClick={handleViewSMEs}>View SMEs →</Button>
                  </div>
                ))}
              </div>
            </>
          )}
        </div>

        {/* Footer */}
        <div style={{ padding: '12px 18px', background: 'var(--uui-neutral-70)', borderTop: '1px solid var(--uui-neutral-60)', display: 'flex', justifyContent: 'flex-end', gap: '9px' }}>
          <Button variant="secondary" size="md" onClick={handleClose}>Close</Button>
          <Button variant="secondary" size="md" disabled={!breakdownData}>Export Data</Button>
        </div>
      </div>
    </div>
  )
}

export default BreakdownModal