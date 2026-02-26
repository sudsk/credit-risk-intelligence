import { useState } from 'react'
import { useScenarios } from '@/hooks/useScenarios'
import ScenarioProgress from './ScenarioProgress'
import ScenarioResults from './ScenarioResults'
import { Button } from '../common/Button'
import { Play, Info } from 'lucide-react'

// ── Scenario templates aligned to ESRB/EBA scenarios ──────────────────────
const SCENARIO_TEMPLATES = [
  {
    id: 'eba_2025_adverse',
    label: '🏦 EBA 2025 Adverse — Higher for Longer',
    description: 'Replicates the official EBA 2025 EU-wide banking stress test adverse scenario.',
    params: { rate_change: 200, gdp_change: -6.0, unemployment_change: 5.0, real_estate_shock: -35 },
    paramLabels: ['rate_change', 'gdp_change', 'unemployment_change', 'real_estate_shock'],
  },
  {
    id: 'interest_rate',
    label: '📈 Interest Rate Shock (Custom)',
    description: 'Model the impact of a central bank rate change on your portfolio. Variable-rate SME loans are most exposed. Adjust the basis points to match your scenario.',
    params: { rate_change: 150, gdp_change: 0, unemployment_change: 0, real_estate_shock: 0 },
    paramLabels: ['rate_change'],
  },
  {
    id: 'sector_shock',
    label: '🏭 Sector Shock',
    description: 'A sudden contraction in a specific sector — regulation, demand collapse, supply chain disruption. Impacts all SMEs in the selected sector.',
    params: { rate_change: 0, gdp_change: -2.0, unemployment_change: 1.5, real_estate_shock: 0, severity: 0.7 },
    paramLabels: ['gdp_change', 'unemployment_change', 'severity'],
    hasSector: true,
  },
  {
    id: 'recession',
    label: '📉 Recession / GDP Contraction',
    description: 'Broad economic downturn affecting all sectors. Models credit deterioration across the portfolio as growth turns negative and unemployment rises.',
    params: { rate_change: 50, gdp_change: -3.5, unemployment_change: 3.0, real_estate_shock: -15 },
    paramLabels: ['rate_change', 'gdp_change', 'unemployment_change', 'real_estate_shock'],
  },
  {
    id: 'geopolitical',
    label: '🌍 Geopolitical / Trade Tariffs',
    description: 'Impact of trade disruption, sanctions, or tariff regimes on export-exposed SMEs. Particularly relevant for UK/EU cross-border trade and US tariff scenarios.',
    params: { rate_change: 0, gdp_change: -2.0, unemployment_change: 1.0, real_estate_shock: -10 },
    paramLabels: ['gdp_change', 'unemployment_change', 'real_estate_shock'],
  },
  {
    id: 'climate_transition',
    label: '🌱 Climate Transition Shock (Fit-for-55)',
    description: 'ESRB Fit-for-55 scenario: carbon pricing shock affecting fossil fuel dependent sectors. Construction, logistics and manufacturing most exposed.',
    params: { rate_change: 0, gdp_change: -1.5, unemployment_change: 0.8, real_estate_shock: -10, severity: 0.5 },
    paramLabels: ['gdp_change', 'unemployment_change', 'real_estate_shock', 'severity'],
  },
  {
    id: 'custom',
    label: '✏️ Custom Scenario',
    description: 'Build your own scenario by setting any combination of macro parameters, or describe it in natural language.',
    params: { rate_change: 0, gdp_change: 0, unemployment_change: 0, real_estate_shock: 0 },
    paramLabels: ['rate_change', 'gdp_change', 'unemployment_change', 'real_estate_shock'],
    isCustom: true,
  },
]

const SECTORS = [
  'Construction', 'Retail/Fashion', 'Food/Hospitality', 'Manufacturing',
  'Software/Technology', 'Healthcare', 'Energy/Utilities', 'Marketing Services',
  'Professional Services', 'Logistics',
]

const PARAM_META: Record<string, { label: string; unit: string; min: number; max: number; step: number }> = {
  rate_change: { label: 'Rate Change', unit: 'bps', min: -200, max: 500, step: 25 },
  gdp_change: { label: 'GDP Change', unit: '%', min: -10, max: 5, step: 0.5 },
  unemployment_change: { label: 'Unemployment Δ', unit: 'pp', min: -2, max: 10, step: 0.5 },
  real_estate_shock: { label: 'Real Estate Shock', unit: '%', min: -60, max: 20, step: 5 },
  severity: { label: 'Shock Severity', unit: '', min: 0.1, max: 1.0, step: 0.1 },
}

// Build a natural-language description from structured params
function buildDescription(template: typeof SCENARIO_TEMPLATES[0], params: Record<string, number>, sector?: string): string {
  if (template.isCustom) return `Custom scenario: rate ${params.rate_change > 0 ? '+' : ''}${params.rate_change}bps, GDP ${params.gdp_change}%, unemployment ${params.unemployment_change > 0 ? '+' : ''}${params.unemployment_change}pp`
  const parts: string[] = [`Run ${template.label.replace(/^[^\w]+/, '').trim()}`]
  if (params.rate_change) parts.push(`rate change ${params.rate_change > 0 ? '+' : ''}${params.rate_change}bps`)
  if (params.gdp_change) parts.push(`GDP ${params.gdp_change}%`)
  if (params.unemployment_change) parts.push(`unemployment ${params.unemployment_change > 0 ? '+' : ''}${params.unemployment_change}pp`)
  if (params.real_estate_shock) parts.push(`real estate ${params.real_estate_shock}%`)
  if (sector) parts.push(`sector: ${sector}`)
  return parts.join(', ')
}

// ── Component ──────────────────────────────────────────────────────────────
const ScenariosTab = () => {
  const { scenarios, isLoading, createScenario } = useScenarios()

  const [selectedTemplateId, setSelectedTemplateId] = useState('eba_2025_adverse')
  const [params, setParams] = useState<Record<string, number>>(SCENARIO_TEMPLATES[0].params)
  const [sector, setSector] = useState(SECTORS[0])
  const [customText, setCustomText] = useState('')
  const [isRunning, setIsRunning] = useState(false)

  const template = SCENARIO_TEMPLATES.find(t => t.id === selectedTemplateId)!

  const handleTemplateChange = (id: string) => {
    const t = SCENARIO_TEMPLATES.find(tt => tt.id === id)!
    setSelectedTemplateId(id)
    setParams({ ...t.params })
  }

  const handleParamChange = (key: string, value: number) => {
    setParams(prev => ({ ...prev, [key]: value }))
  }

  const handleRun = async () => {
    const description = template.isCustom
      ? (customText.trim() || buildDescription(template, params, template.hasSector ? sector : undefined))
      : buildDescription(template, params, template.hasSector ? sector : undefined)
    if (!description.trim()) return
    setIsRunning(true)
    try {
      await createScenario(description)
    } catch (e) {
      console.error('Scenario failed:', e)
    } finally {
      setIsRunning(false)
    }
  }

  const inProgress = scenarios.filter(s => s.status === 'in_progress')
  const completed = scenarios.filter(s => s.status === 'completed')

  const sectionTitle = (text: string) => (
    <div style={{ fontSize: '13px', fontWeight: 700, color: 'var(--uui-text-tertiary)', textTransform: 'uppercase', letterSpacing: '0.06em', marginBottom: '12px' }}>
      {text}
    </div>
  )

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '18px' }}>

      {/* ── SCENARIO BUILDER ─────────────────────────────────────────── */}
      <div style={{ background: 'var(--uui-surface-main)', border: '1px solid var(--uui-neutral-60)', borderRadius: 'var(--uui-border-radius)', overflow: 'hidden' }}>

        {/* Header */}
        <div style={{ padding: '16px 20px', borderBottom: '1px solid var(--uui-neutral-60)', background: 'var(--uui-neutral-70)' }}>
          <div style={{ fontSize: '15px', fontWeight: 700, color: 'var(--uui-text-primary)' }}>
            📊 Run New Stress Test
          </div>
          <div style={{ fontSize: '12px', color: 'var(--uui-text-tertiary)', marginTop: '3px' }}>
            ESRB / EBA aligned scenarios — models impact across all SMEs in portfolio
          </div>
        </div>

        <div style={{ padding: '20px', display: 'flex', flexDirection: 'column', gap: '20px' }}>

          {/* Template selector + description row */}
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px' }}>

            {/* Left: template dropdown */}
            <div>
              {sectionTitle('Scenario Template')}
              <select
                value={selectedTemplateId}
                onChange={e => handleTemplateChange(e.target.value)}
                style={{
                  width: '100%', padding: '10px 14px',
                  background: 'var(--uui-neutral-70)',
                  border: '1px solid var(--uui-neutral-50)',
                  borderRadius: 'var(--uui-border-radius)',
                  color: 'var(--uui-text-primary)',
                  fontSize: '13px', fontFamily: 'var(--uui-font)',
                  cursor: 'pointer', outline: 'none',
                  appearance: 'none',
                  backgroundImage: `url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='8' viewBox='0 0 12 8'%3E%3Cpath d='M1 1l5 5 5-5' stroke='%23888' stroke-width='1.5' fill='none' stroke-linecap='round'/%3E%3C/svg%3E")`,
                  backgroundRepeat: 'no-repeat',
                  backgroundPosition: 'right 14px center',
                  paddingRight: '36px',
                }}
              >
                {SCENARIO_TEMPLATES.map(t => (
                  <option key={t.id} value={t.id}>{t.label}</option>
                ))}
              </select>
            </div>

            {/* Right: description */}
            <div>
              {sectionTitle('About This Scenario')}
              <div style={{
                padding: '10px 14px', fontSize: '12px', lineHeight: 1.6,
                color: 'var(--uui-text-secondary)',
                background: 'var(--uui-neutral-80)',
                border: '1px solid var(--uui-neutral-60)',
                borderRadius: 'var(--uui-border-radius)',
                minHeight: '60px',
                display: 'flex', alignItems: 'flex-start', gap: '8px',
              }}>
                <Info size={13} style={{ color: 'var(--uui-text-tertiary)', flexShrink: 0, marginTop: '2px' }} />
                {template.description}
              </div>
            </div>
          </div>

          {/* Parameters */}
          {!template.isCustom && (
            <div>
              {sectionTitle('Parameters')}
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(180px, 1fr))', gap: '12px' }}>

                {template.paramLabels.map(key => {
                  const meta = PARAM_META[key]
                  if (!meta) return null
                  const val = params[key] ?? 0
                  const isPositive = val > 0
                  const isNegative = val < 0
                  return (
                    <div key={key} style={{
                      background: 'var(--uui-neutral-70)',
                      border: '1px solid var(--uui-neutral-60)',
                      borderRadius: 'var(--uui-border-radius)',
                      padding: '12px',
                    }}>
                      <div style={{ fontSize: '11px', color: 'var(--uui-text-tertiary)', marginBottom: '8px' }}>
                        {meta.label}
                      </div>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '8px' }}>
                        <span style={{
                          fontSize: '20px', fontWeight: 700, fontFamily: 'var(--uui-font-mono)',
                          color: isPositive ? 'var(--uui-critical-60)' : isNegative ? 'var(--uui-warning-60)' : 'var(--uui-text-primary)',
                        }}>
                          {val > 0 ? '+' : ''}{val}{meta.unit}
                        </span>
                      </div>
                      <input
                        type="range"
                        min={meta.min} max={meta.max} step={meta.step}
                        value={val}
                        onChange={e => handleParamChange(key, parseFloat(e.target.value))}
                        style={{ width: '100%', accentColor: 'var(--uui-primary-60)', cursor: 'pointer' }}
                      />
                      <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '10px', color: 'var(--uui-text-tertiary)', marginTop: '2px' }}>
                        <span>{meta.min}{meta.unit}</span>
                        <span>{meta.max}{meta.unit}</span>
                      </div>
                    </div>
                  )
                })}

                {/* Sector selector if applicable */}
                {template.hasSector && (
                  <div style={{
                    background: 'var(--uui-neutral-70)',
                    border: '1px solid var(--uui-neutral-60)',
                    borderRadius: 'var(--uui-border-radius)',
                    padding: '12px',
                  }}>
                    <div style={{ fontSize: '11px', color: 'var(--uui-text-tertiary)', marginBottom: '8px' }}>Affected Sector</div>
                    <select
                      value={sector}
                      onChange={e => setSector(e.target.value)}
                      style={{
                        width: '100%', padding: '8px 10px',
                        background: 'var(--uui-neutral-80)',
                        border: '1px solid var(--uui-neutral-60)',
                        borderRadius: 'var(--uui-border-radius)',
                        color: 'var(--uui-text-primary)',
                        fontSize: '13px', fontFamily: 'var(--uui-font)',
                        outline: 'none',
                      }}
                    >
                      {SECTORS.map(s => <option key={s} value={s}>{s}</option>)}
                    </select>
                  </div>
                )}
              </div>
            </div>
          )}

          {/* Custom text input */}
          {template.isCustom && (
            <div>
              {sectionTitle('Describe Your Scenario')}
              <input
                type="text"
                placeholder="e.g. 'What if Trump imposes 50% tariffs on EU goods?'"
                value={customText}
                onChange={e => setCustomText(e.target.value)}
                onKeyPress={e => e.key === 'Enter' && handleRun()}
                style={{
                  width: '100%', padding: '10px 14px', boxSizing: 'border-box',
                  background: 'var(--uui-neutral-70)',
                  border: '1px solid var(--uui-neutral-60)',
                  borderRadius: 'var(--uui-border-radius)',
                  color: 'var(--uui-text-primary)',
                  fontSize: '13px', fontFamily: 'var(--uui-font)', outline: 'none',
                }}
              />
            </div>
          )}

          {/* Run button */}
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
            <div style={{ fontSize: '11px', color: 'var(--uui-text-tertiary)' }}>
              Scenario will run across all SMEs in the portfolio — typically 15–30 seconds
            </div>
            <Button variant="primary" size="lg" onClick={handleRun} disabled={isRunning || (template.isCustom && !customText.trim())}>
              <Play size={15} />
              {isRunning ? 'Running...' : 'Run Stress Test'}
            </Button>
          </div>
        </div>
      </div>

      {/* ── IN PROGRESS ──────────────────────────────────────────────── */}
      {inProgress.length > 0 && (
        <section>
          <div style={{ fontSize: '14px', fontWeight: 600, color: 'var(--uui-text-primary)', marginBottom: '12px' }}>
            ⏳ Running ({inProgress.length})
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '9px' }}>
            {inProgress.map(s => <ScenarioProgress key={s.id} scenario={s} />)}
          </div>
        </section>
      )}

      {/* ── COMPLETED ────────────────────────────────────────────────── */}
      {completed.length > 0 && (
        <section>
          <div style={{ fontSize: '14px', fontWeight: 600, color: 'var(--uui-text-primary)', marginBottom: '12px' }}>
            ✅ Completed ({completed.length})
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '9px' }}>
            {completed.map(s => <ScenarioResults key={s.id} scenario={s} />)}
          </div>
        </section>
      )}

      {/* ── EMPTY STATE ───────────────────────────────────────────────── */}
      {scenarios.length === 0 && !isLoading && (
        <div style={{ textAlign: 'center', padding: '48px', background: 'var(--uui-surface-main)', border: '1px solid var(--uui-neutral-60)', borderRadius: 'var(--uui-border-radius)' }}>
          <div style={{ fontSize: '36px', marginBottom: '12px' }}>📊</div>
          <p style={{ fontSize: '15px', fontWeight: 500, color: 'var(--uui-text-secondary)', marginBottom: '8px' }}>No scenarios run yet</p>
          <p style={{ fontSize: '13px', color: 'var(--uui-text-tertiary)' }}>
            Select a template above and click Run Stress Test to model portfolio impact
          </p>
        </div>
      )}
    </div>
  )
}

export default ScenariosTab