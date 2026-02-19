import { X } from 'lucide-react'
import { useDispatch, useSelector } from 'react-redux'
import { RootState } from '@/store'
import { closeBreakdownModal } from '@/store/uiSlice'
import { setFilter } from '@/store/portfolioSlice'
import { setActiveTab } from '@/store/uiSlice'
import { Button } from '../common/Button'

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
  const { breakdownModalOpen, breakdownModalData } = useSelector((state: RootState) => state.ui)

  if (!breakdownModalOpen || !breakdownModalData) return null

  const { riskLevel } = breakdownModalData
  const data = breakdownData[riskLevel as keyof typeof breakdownData]

  const handleClose = () => dispatch(closeBreakdownModal())
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
          <h3 style={{ fontSize: '14px', fontWeight: 600, color: 'var(--uui-text-primary)' }}>{data.title}</h3>
          <button onClick={handleClose} style={{ width: '28px', height: '28px', borderRadius: 'var(--uui-border-radius)', background: 'var(--uui-neutral-60)', border: 'none', cursor: 'pointer', display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'var(--uui-text-primary)' }}>
            <X size={16} />
          </button>
        </div>

        {/* Body */}
        <div style={{ flex: 1, overflowY: 'auto', padding: '18px' }}>
          {/* Summary */}
          <div style={{ marginBottom: '18px', padding: '12px', background: 'var(--uui-neutral-70)', borderRadius: 'var(--uui-border-radius)', border: '1px solid var(--uui-neutral-60)' }}>
            <div style={{ fontSize: '12px', fontWeight: 600, color: 'var(--uui-text-secondary)', marginBottom: '6px' }}>Total Portfolio Impact</div>
            <div style={{ fontSize: '12px', color: 'var(--uui-text-tertiary)', fontFamily: 'var(--uui-font-mono)' }}>
              {data.total.smes} SMEs | {data.total.exposure} exposure | {data.total.percent} of portfolio
            </div>
          </div>

          {/* By Sector */}
          <div style={{ marginBottom: '18px' }}>
            {sectionTitle('By Sector')}
            {data.sectors.map((sector, idx) => (
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
            {data.geographies.map((geo, idx) => (
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
        </div>

        {/* Footer */}
        <div style={{ padding: '12px 18px', background: 'var(--uui-neutral-70)', borderTop: '1px solid var(--uui-neutral-60)', display: 'flex', justifyContent: 'flex-end', gap: '9px' }}>
          <Button variant="secondary" size="md" onClick={handleClose}>Close</Button>
          <Button variant="secondary" size="md">Export Data</Button>
        </div>
      </div>
    </div>
  )
}

export default BreakdownModal