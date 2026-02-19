import { useEffect, useState } from 'react'
import { activitiesAPI } from '@/services/api'
import ActivityFeed from './ActivityFeed'
import { Card, CardHeader, CardTitle, CardContent } from '../common/Card'
import { Button } from '../common/Button'
import { Download, Filter } from 'lucide-react'

const FILTERS = ['all', 'alert', 'info', 'success', 'warning'] as const
type FilterType = typeof FILTERS[number]

const ActivitiesTab = () => {
  const [activities, setActivities] = useState<any[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [filter, setFilter] = useState<FilterType>('all')

  useEffect(() => { loadActivities() }, [])

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

  const filteredActivities = filter === 'all' ? activities : activities.filter(a => a.type === filter)

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '18px' }}>
      {/* Filters */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '9px' }}>
          <Filter size={16} style={{ color: 'var(--uui-text-tertiary)' }} />
          <span style={{ fontSize: '13px', color: 'var(--uui-text-tertiary)' }}>Filter:</span>
          <div style={{ display: 'flex', gap: '6px' }}>
            {FILTERS.map((f) => (
              <button key={f} onClick={() => setFilter(f)} style={{
                padding: '4px 12px', fontSize: '11px', fontWeight: 600,
                borderRadius: 'var(--uui-border-radius)', border: 'none', cursor: 'pointer',
                background: filter === f ? 'var(--uui-primary-60)' : 'var(--uui-neutral-60)',
                color: filter === f ? 'white' : 'var(--uui-text-primary)',
                fontFamily: 'var(--uui-font)',
              }}>
                {f.charAt(0).toUpperCase() + f.slice(1)}
              </button>
            ))}
          </div>
        </div>
        <Button variant="secondary" size="sm" onClick={() => console.log('Exporting...')}>
          <Download size={14} />
          Export Audit Log
        </Button>
      </div>

      {/* Feed */}
      <Card>
        <CardHeader>
          <CardTitle>
            <div style={{ display: 'flex', alignItems: 'center', gap: '9px' }}>
              <span style={{ fontSize: '20px' }}>🔔</span>
              <div>
                <div style={{ fontSize: '14px', fontWeight: 600, color: 'var(--uui-text-primary)' }}>System Activity Feed</div>
                <div style={{ fontSize: '11px', color: 'var(--uui-text-tertiary)', fontWeight: 400 }}>Real-time audit trail of all system actions</div>
              </div>
            </div>
          </CardTitle>
        </CardHeader>
        <CardContent>
          {isLoading
            ? <div style={{ textAlign: 'center', padding: '48px', color: 'var(--uui-text-tertiary)' }}>Loading activities...</div>
            : <ActivityFeed activities={filteredActivities} />
          }
        </CardContent>
      </Card>
    </div>
  )
}

export default ActivitiesTab