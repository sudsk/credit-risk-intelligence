import { Info } from 'lucide-react'
import { useDispatch } from 'react-redux'
import { usePortfolio } from '@/hooks/usePortfolio'
import { openBreakdownModal } from '@/store/uiSlice'
import { setFilter } from '@/store/portfolioSlice'

const MetricCard = ({ children, borderColor, onClick }: any) => (
  <div onClick={onClick} style={{
    background: 'var(--uui-surface-main)',
    border: `1px solid var(--uui-neutral-60)`,
    borderRadius: 'var(--uui-border-radius)',
    padding: '18px',
    position: 'relative',
    cursor: 'pointer',
    borderLeft: `3px solid ${borderColor}`,
    transition: 'all 0.2s',
  }}>
    {children}
  </div>
)

const PortfolioMetrics = () => {
  const dispatch = useDispatch()
  const { metrics, isLoading } = usePortfolio()

  if (isLoading || !metrics) {
    return <div style={{ color: 'var(--uui-text-tertiary)', padding: '48px', textAlign: 'center' }}>Loading...</div>
  }

  const label = (text: string) => (
    <div style={{ fontSize: '11px', color: 'var(--uui-text-tertiary)', textTransform: 'uppercase', fontWeight: 600, marginBottom: '6px' }}>{text}</div>
  )
  const value = (text: string | number, color?: string) => (
    <div style={{ fontSize: '28px', fontWeight: 600, marginBottom: '3px', color: color || 'var(--uui-text-primary)' }}>{text}</div>
  )
  const sub = (text: string) => (
    <div style={{ fontSize: '12px', color: 'var(--uui-text-tertiary)', fontFamily: 'var(--uui-font-mono)' }}>{text}</div>
  )
  const infoBtn = (riskLevel: string) => (
    <button onClick={(e) => { e.stopPropagation(); dispatch(openBreakdownModal({ riskLevel })) }} style={{
      position: 'absolute', top: '18px', right: '18px',
      width: '24px', height: '24px', borderRadius: '50%',
      background: 'var(--uui-neutral-60)', color: 'var(--uui-text-tertiary)',
      border: 'none', cursor: 'pointer', display: 'flex', alignItems: 'center', justifyContent: 'center',
    }}>
      <Info size={14} />
    </button>
  )

  return (
    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '12px', marginBottom: '18px' }}>
      <MetricCard borderColor="var(--uui-critical-60)" onClick={() => dispatch(setFilter('critical'))}>
        {infoBtn('critical')}
        {label('CRITICAL RISK (80-100)')}
        {value(metrics.criticalCount, 'var(--uui-critical-70)')}
        {sub('€42M | 12.8% | ↑ 5')}
      </MetricCard>

      <MetricCard borderColor="var(--uui-warning-60)" onClick={() => dispatch(setFilter('medium'))}>
        {infoBtn('medium')}
        {label('MEDIUM RISK (50-79)')}
        {value(metrics.mediumCount, 'var(--uui-warning-70)')}
        {sub('€98M | 29.9% | ↑ 8')}
      </MetricCard>

      <MetricCard borderColor="var(--uui-success-60)" onClick={() => dispatch(setFilter('stable'))}>
        {infoBtn('stable')}
        {label('LOW RISK (0-49)')}
        {value(metrics.stableCount, 'var(--uui-success-70)')}
        {sub('€188M | 57.3% | ↓ 13')}
      </MetricCard>

      <MetricCard borderColor="var(--uui-primary-60)" onClick={() => { }}>
        {label('TOTAL PORTFOLIO')}
        {value(metrics.totalSMEs)}
        {sub(`${metrics.totalExposure} total exposure`)}
      </MetricCard>

      <MetricCard borderColor="var(--uui-primary-60)" onClick={() => { }}>
        {label('DEFAULT PROBABILITY')}
        {value(`${metrics.defaultProbability}%`)}
        <div style={{ fontSize: '12px', color: 'var(--uui-critical-60)', fontFamily: 'var(--uui-font-mono)' }}>↑ 0.4% vs last month</div>
      </MetricCard>

      <MetricCard borderColor="var(--uui-primary-60)" onClick={() => { }}>
        {label('AVG CREDIT RISK SCORE')}
        {value(metrics.avgRiskScore)}
        {sub('↑ 3 vs last month')}
      </MetricCard>
    </div>
  )
}

export default PortfolioMetrics