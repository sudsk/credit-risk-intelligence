import { useState } from 'react'
import { useScenarios } from '@/hooks/useScenarios'
import ScenarioProgress from './ScenarioProgress'
import ScenarioResults from './ScenarioResults'
import { Button } from '../common/Button'
import { Play } from 'lucide-react'

const ScenariosTab = () => {
  const { scenarios, isLoading, createScenario } = useScenarios()
  const [newScenarioInput, setNewScenarioInput] = useState('')

  const inProgressScenarios = scenarios.filter((s) => s.status === 'in_progress')
  const completedScenarios = scenarios.filter((s) => s.status === 'completed')

  const handleCreateScenario = async () => {
    if (!newScenarioInput.trim()) return
    try {
      await createScenario(newScenarioInput)
      setNewScenarioInput('')
    } catch (error) {
      console.error('Failed to create scenario:', error)
    }
  }

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '18px' }}>
      {/* Create New Scenario */}
      <div style={{ background: 'var(--uui-surface-main)', border: '1px solid var(--uui-neutral-60)', borderRadius: 'var(--uui-border-radius)', padding: '18px' }}>
        <div style={{ fontSize: '16px', fontWeight: 600, color: 'var(--uui-text-primary)', marginBottom: '18px' }}>
          🎯 Create New Scenario
        </div>
        <div style={{ display: 'flex', gap: '12px' }}>
          <input
            type="text"
            placeholder="Describe your scenario (e.g., 'What if interest rates go up 1%?')"
            value={newScenarioInput}
            onChange={(e) => setNewScenarioInput(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && handleCreateScenario()}
            style={{
              flex: 1, padding: '10px 14px',
              background: 'var(--uui-neutral-70)',
              border: '1px solid var(--uui-neutral-60)',
              borderRadius: 'var(--uui-border-radius)',
              color: 'var(--uui-text-primary)',
              fontSize: '13px', fontFamily: 'var(--uui-font)', outline: 'none',
            }}
          />
          <Button variant="primary" size="lg" onClick={handleCreateScenario} disabled={!newScenarioInput.trim()}>
            <Play size={16} />
            Run Scenario
          </Button>
        </div>
        <p style={{ fontSize: '11px', color: 'var(--uui-text-tertiary)', marginTop: '9px' }}>
          Ask any what-if question about your portfolio. AI will analyze all 1,284 SMEs in 15-30 seconds.
        </p>
      </div>

      {/* In Progress */}
      {inProgressScenarios.length > 0 && (
        <section>
          <div style={{ fontSize: '16px', fontWeight: 600, color: 'var(--uui-text-primary)', marginBottom: '12px' }}>
            ⏳ In Progress ({inProgressScenarios.length})
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '9px' }}>
            {inProgressScenarios.map((s) => <ScenarioProgress key={s.id} scenario={s} />)}
          </div>
        </section>
      )}

      {/* Completed */}
      {completedScenarios.length > 0 && (
        <section>
          <div style={{ fontSize: '16px', fontWeight: 600, color: 'var(--uui-text-primary)', marginBottom: '12px' }}>
            ✅ Completed ({completedScenarios.length})
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '9px' }}>
            {completedScenarios.map((s) => <ScenarioResults key={s.id} scenario={s} />)}
          </div>
        </section>
      )}

      {/* Empty State */}
      {scenarios.length === 0 && !isLoading && (
        <div style={{ textAlign: 'center', padding: '48px', background: 'var(--uui-surface-main)', border: '1px solid var(--uui-neutral-60)', borderRadius: 'var(--uui-border-radius)' }}>
          <div style={{ fontSize: '36px', marginBottom: '12px' }}>🎯</div>
          <p style={{ fontSize: '16px', fontWeight: 500, color: 'var(--uui-text-secondary)', marginBottom: '8px' }}>No scenarios yet</p>
          <p style={{ fontSize: '13px', color: 'var(--uui-text-tertiary)' }}>Create your first scenario to analyze portfolio impact</p>
        </div>
      )}
    </div>
  )
}

export default ScenariosTab