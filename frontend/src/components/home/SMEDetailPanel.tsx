import { AlertCircle, TrendingUp, TrendingDown, Minus } from 'lucide-react'
import { useSelector } from 'react-redux'
import { RootState } from '@/store'
import { Badge } from '../common/Badge'
import { Button } from '../common/Button'

const SMEDetailPanel = () => {
  const selectedSME = useSelector((state: RootState) => state.portfolio.selectedSME)

  if (!selectedSME) {
    return (
      <div style={{
        background: 'var(--uui-surface-main)',
        border: '1px solid var(--uui-neutral-60)',
        borderRadius: 'var(--uui-border-radius)',
        height: 'calc(100vh - 320px)',
        display: 'flex', alignItems: 'center', justifyContent: 'center'
      }}>
        <div style={{ textAlign: 'center' }}>
          <div style={{ fontSize: '48px', marginBottom: '16px' }}>📊</div>
          <p style={{ fontSize: '16px', fontWeight: 600, color: 'var(--uui-text-secondary)' }}>
            Select an SME to view details
          </p>
          <p style={{ fontSize: '13px', marginTop: '8px', color: 'var(--uui-text-tertiary)' }}>
            Click on any SME from the list to see comprehensive analysis
          </p>
        </div>
      </div>
    )
  }

  const getRiskBadgeVariant = (category: string) => {
    switch (category) {
      case 'critical': return 'critical'
      case 'medium': return 'warning'
      case 'stable': return 'success'
      default: return 'info'
    }
  }

  const getTrendIcon = (trend: string) => {
    switch (trend) {
      case 'up': return <TrendingUp size={16} style={{ color: 'var(--uui-critical-60)' }} />
      case 'down': return <TrendingDown size={16} style={{ color: 'var(--uui-success-60)' }} />
      default: return <Minus size={16} style={{ color: 'var(--uui-text-tertiary)' }} />
    }
  }

  const getTrendColor = (trend: string) => {
    switch (trend) {
      case 'up': return 'var(--uui-critical-60)'
      case 'down': return 'var(--uui-success-60)'
      default: return 'var(--uui-text-tertiary)'
    }
  }

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

  const sectionTitle = (text: string, icon?: React.ReactNode) => (
    <div style={{
      display: 'flex', alignItems: 'center', gap: '6px',
      fontSize: '12px', fontWeight: 600,
      color: 'var(--uui-text-tertiary)',
      textTransform: 'uppercase' as const,
      marginBottom: '9px',
    }}>
      {icon}
      {text}
    </div>
  )

  const infoBox = (label: string, value: string) => (
    <div style={{
      padding: '9px 12px',
      background: 'var(--uui-neutral-70)',
      borderRadius: 'var(--uui-border-radius)',
    }}>
      <div style={{ fontSize: '10px', color: 'var(--uui-text-tertiary)', textTransform: 'uppercase', marginBottom: '3px' }}>
        {label}
      </div>
      <div style={{ fontSize: '14px', fontWeight: 600, color: 'var(--uui-text-primary)' }}>
        {value}
      </div>
    </div>
  )

  return (
    <div style={{
      background: 'var(--uui-surface-main)',
      border: '1px solid var(--uui-neutral-60)',
      borderRadius: 'var(--uui-border-radius)',
      height: 'calc(100vh - 320px)',
      overflowY: 'auto',
    }}>
      {/* Sticky Header */}
      <div style={{
        position: 'sticky', top: 0, zIndex: 10,
        background: 'var(--uui-neutral-70)',
        borderBottom: '1px solid var(--uui-neutral-60)',
        padding: '12px 18px',
      }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
          {/* Left */}
          <div style={{ flex: 1 }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '6px' }}>
              <span style={{ fontSize: '11px', color: 'var(--uui-text-tertiary)', fontFamily: 'var(--uui-font-mono)' }}>
                {selectedSME.id}
              </span>
              <Badge variant={getRiskBadgeVariant(selectedSME.riskCategory) as any}>
                {selectedSME.riskCategory.toUpperCase()}
              </Badge>
            </div>
            <h2 style={{ fontSize: '18px', fontWeight: 700, color: 'var(--uui-text-primary)', marginBottom: '6px' }}>
              {selectedSME.name}
            </h2>
            <div style={{ display: 'flex', alignItems: 'center', gap: '16px', fontSize: '13px', color: 'var(--uui-text-secondary)' }}>
              <span>💼 {selectedSME.sector}</span>
              <span>📍 {selectedSME.geography}</span>
              <span style={{ fontFamily: 'var(--uui-font-mono)', fontWeight: 600 }}>{selectedSME.exposure}</span>
            </div>
          </div>

          {/* Right - Score */}
          <div style={{ textAlign: 'right' }}>
            <div style={{ fontSize: '36px', fontWeight: 700, fontFamily: 'var(--uui-font-mono)', color: 'var(--uui-text-primary)' }}>
              {selectedSME.riskScore}
            </div>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'flex-end', gap: '4px', marginTop: '4px' }}>
              {getTrendIcon(selectedSME.trend)}
              <span style={{ fontSize: '12px', fontFamily: 'var(--uui-font-mono)', fontWeight: 600, color: getTrendColor(selectedSME.trend) }}>
                {selectedSME.trendValue > 0 ? '+' : ''}{selectedSME.trendValue} this quarter
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* Content */}
      <div style={{ padding: '18px', display: 'flex', flexDirection: 'column', gap: '18px' }}>

        {/* Risk Drivers */}
        <section>
          {sectionTitle('Key Risk Drivers', <AlertCircle size={14} />)}
          <div style={{ display: 'flex', flexDirection: 'column', gap: '9px' }}>
            {detailedData.riskDrivers.map((driver, idx) => (
              <div key={idx} style={{
                display: 'flex', alignItems: 'center', justifyContent: 'space-between',
                padding: '12px',
                background: 'var(--uui-neutral-70)',
                borderRadius: 'var(--uui-border-radius)',
                borderLeft: '3px solid var(--uui-critical-60)',
              }}>
                <div style={{ flex: 1 }}>
                  <div style={{ fontSize: '13px', fontWeight: 600, color: 'var(--uui-text-primary)', marginBottom: '3px' }}>
                    {driver.label}
                  </div>
                  <div style={{ fontSize: '11px', color: 'var(--uui-text-tertiary)' }}>
                    Source: {driver.source}
                  </div>
                </div>
                <div style={{ textAlign: 'right' }}>
                  <div style={{ fontSize: '18px', fontWeight: 700, color: 'var(--uui-critical-60)' }}>
                    {driver.impact}
                  </div>
                  <div style={{ fontSize: '11px', color: 'var(--uui-text-tertiary)' }}>points</div>
                </div>
              </div>
            ))}
          </div>
        </section>

        {/* Financial Metrics */}
        <section>
          {sectionTitle('Financial Metrics')}
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px' }}>
            {infoBox('Annual Revenue', detailedData.financials.revenue)}
            {infoBox('EBITDA', detailedData.financials.ebitda)}
            {infoBox('Debt Service Coverage', detailedData.financials.debtServiceCoverage)}
            {infoBox('Cash Reserves', detailedData.financials.cashReserves)}
          </div>
        </section>

        {/* External Risk Factors */}
        <section>
          {sectionTitle('External Risk Factors')}
          <div style={{ display: 'flex', flexDirection: 'column', gap: '9px' }}>
            {[
              { label: 'Sector Health', value: detailedData.externalFactors.sectorHealth, variant: 'warning' },
              { label: 'Geography Risk', value: detailedData.externalFactors.geographyRisk, variant: 'success' },
              { label: 'Compliance Status', value: detailedData.externalFactors.compliance, variant: 'success' },
            ].map((item, idx) => (
              <div key={idx} style={{
                display: 'flex', alignItems: 'center', justifyContent: 'space-between',
                padding: '9px 12px',
                background: 'var(--uui-neutral-70)',
                borderRadius: 'var(--uui-border-radius)',
              }}>
                <span style={{ fontSize: '13px', color: 'var(--uui-text-secondary)' }}>{item.label}</span>
                <Badge variant={item.variant as any}>{item.value}</Badge>
              </div>
            ))}
          </div>
        </section>

        {/* Actions */}
        <section style={{ paddingTop: '12px', borderTop: '1px solid var(--uui-neutral-60)' }}>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '9px' }}>
            <Button variant="primary" size="md">Create Task</Button>
            <Button variant="secondary" size="md">Run Scenario</Button>
            <div style={{ gridColumn: '1 / -1' }}>
              <Button variant="secondary" size="md" fullWidth>View Full History</Button>
            </div>
          </div>
        </section>

      </div>
    </div>
  )
}

export default SMEDetailPanel