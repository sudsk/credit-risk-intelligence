import { useEffect, useState } from 'react'
import { activitiesAPI } from '@/services/api'
import ActivityFeed from './ActivityFeed'
import { Card, CardHeader, CardTitle, CardContent } from '../common/Card'
import { Button } from '../common/Button'
import { Download, Filter } from 'lucide-react'

const ActivitiesTab = () => {
  const [activities, setActivities] = useState<any[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [filter, setFilter] = useState<'all' | 'alert' | 'info' | 'success' | 'warning'>('all')

  useEffect(() => {
    loadActivities()
  }, [])

  const loadActivities = async () => {
    try {
      setIsLoading(true)
      const data = await activitiesAPI.getActivities()
      setActivities(data)
    } catch (error) {
      console.error('Failed to load activities:', error)
    } finally {
      setIsLoading(false)
    }
  }

  const filteredActivities = filter === 'all' 
    ? activities 
    : activities.filter(a => a.type === filter)

  const handleExportLog = () => {
    // Mock export functionality
    console.log('Exporting activity log...')
  }

  return (
    <div className="space-y-6">
      {/* Filters */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Filter className="w-4 h-4 text-neutral-500" />
          <span className="text-sm text-neutral-600">Filter:</span>
          <div className="flex gap-2">
            {['all', 'alert', 'info', 'success', 'warning'].map((filterType) => (
              <button
                key={filterType}
                onClick={() => setFilter(filterType as any)}
                className={`px-3 py-1.5 text-xs font-medium rounded transition-colors ${
                  filter === filterType
                    ? 'bg-primary-60 text-white'
                    : 'bg-neutral-200 text-neutral-700 hover:bg-neutral-300'
                }`}
              >
                {filterType.charAt(0).toUpperCase() + filterType.slice(1)}
              </button>
            ))}
          </div>
        </div>
        <Button variant="secondary" size="sm" onClick={handleExportLog}>
          <Download className="w-4 h-4" />
          Export Audit Log
        </Button>
      </div>

      {/* Activity Feed */}
      <Card>
        <CardHeader>
          <CardTitle>
            <div className="flex items-center gap-2">
              <span className="text-2xl">🔔</span>
              <div>
                <div className="text-lg font-semibold">System Activity Feed</div>
                <div className="text-xs font-normal text-neutral-500">
                  Real-time audit trail of all system actions
                </div>
              </div>
            </div>
          </CardTitle>
        </CardHeader>
        <CardContent>
          {isLoading ? (
            <div className="text-center py-12 text-neutral-500">
              Loading activities...
            </div>
          ) : (
            <ActivityFeed activities={filteredActivities} />
          )}
        </CardContent>
      </Card>
    </div>
  )
}

export default ActivitiesTab
