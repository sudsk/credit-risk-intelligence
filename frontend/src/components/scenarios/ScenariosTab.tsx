import { useState } from 'react'
import { useDispatch } from 'react-redux'
import { useScenarios } from '@/hooks/useScenarios'
import ScenarioProgress from './ScenarioProgress'
import ScenarioResults from './ScenarioResults'
import { Button } from '../common/Button'
import { Plus, Play } from 'lucide-react'

const ScenariosTab = () => {
  const dispatch = useDispatch()
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
    <div className="space-y-6">
      {/* Create New Scenario */}
      <div className="bg-white rounded-lg border border-neutral-300 p-6">
        <h3 className="text-lg font-semibold text-neutral-800 mb-4">
          🎯 Create New Scenario
        </h3>
        <div className="flex gap-3">
          <input
            type="text"
            placeholder="Describe your scenario (e.g., 'What if interest rates go up 1%?')"
            value={newScenarioInput}
            onChange={(e) => setNewScenarioInput(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && handleCreateScenario()}
            className="flex-1 px-4 py-3 border border-neutral-600 rounded focus:outline-none focus:ring-2 focus:ring-primary-60 bg-neutral-700 text-neutral-50"
          />
          <Button
            variant="primary"
            size="lg"
            onClick={handleCreateScenario}
            disabled={!newScenarioInput.trim()}
          >
            <Play className="w-4 h-4" />
            Run Scenario
          </Button>
        </div>
        <p className="text-xs text-neutral-500 mt-2">
          Ask any what-if question about your portfolio. AI will analyze all 1,284 SMEs in 15-30 seconds.
        </p>
      </div>

      {/* In Progress Scenarios */}
      {inProgressScenarios.length > 0 && (
        <section>
          <h3 className="text-lg font-semibold text-neutral-800 mb-3">
            ⏳ In Progress ({inProgressScenarios.length})
          </h3>
          <div className="space-y-3">
            {inProgressScenarios.map((scenario) => (
              <ScenarioProgress key={scenario.id} scenario={scenario} />
            ))}
          </div>
        </section>
      )}

      {/* Completed Scenarios */}
      {completedScenarios.length > 0 && (
        <section>
          <h3 className="text-lg font-semibold text-neutral-800 mb-3">
            ✅ Completed ({completedScenarios.length})
          </h3>
          <div className="space-y-3">
            {completedScenarios.map((scenario) => (
              <ScenarioResults key={scenario.id} scenario={scenario} />
            ))}
          </div>
        </section>
      )}

      {/* Empty State */}
      {scenarios.length === 0 && !isLoading && (
        <div className="text-center py-12 bg-white rounded-lg border border-neutral-300">
          <div className="text-4xl mb-3">🎯</div>
          <p className="text-lg font-medium text-neutral-700">No scenarios yet</p>
          <p className="text-sm text-neutral-500 mt-2">
            Create your first scenario to analyze portfolio impact
          </p>
        </div>
      )}
    </div>
  )
}

export default ScenariosTab
