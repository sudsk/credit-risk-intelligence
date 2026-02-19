import { AlertCircle, Clock } from 'lucide-react'
import { useState } from 'react'
import { useDispatch } from 'react-redux'
import { setActiveTab } from '@/store/uiSlice'
import { setSelectedSME } from '@/store/portfolioSlice'
import { addScenario } from '@/store/scenariosSlice'
import { addTask } from '@/store/tasksSlice'
import { Button } from '../common/Button'
import { Card, CardHeader, CardTitle, CardContent } from '../common/Card'
import { Badge } from '../common/Badge'
import { formatRelativeTime } from '@/utils/formatters'

// Mock data
const newsItems = [
  {
    id: 'news_001',
    timestamp: '2024-11-16T14:32:17Z',
    smeId: '#0142',
    smeName: 'TechStart Solutions Ltd',
    exposure: '€250K',
    type: 'departure' as const,
    severity: 'critical' as const,
    title: 'CTO Departure Detected',
    summary: 'LinkedIn activity shows CTO Sarah Johnson departed 2 hours ago. No replacement hire detected. Sales Director also left within 2-week window.',
    signals: [
      { source: 'LinkedIn', detail: 'CTO profile updated: "Open to new opportunities"' },
      { source: 'Web Traffic', detail: '-42% QoQ decline' },
      { source: 'Client Data', detail: '2 major clients lost in past 30 days' },
    ],
    recommendation: 'Immediate management meeting recommended. High risk of further deterioration.',
  },
  {
    id: 'news_002',
    timestamp: '2024-11-16T11:15:43Z',
    smeId: '#0287',
    smeName: 'Urban Fashion Ltd',
    exposure: '€180K',
    type: 'payment_delay' as const,
    severity: 'warning' as const,
    title: 'Payment Delays to Suppliers',
    summary: 'Alternative data shows 3 suppliers reporting late payments (avg 47 days vs normal 30 days). Cash flow stress indicator.',
    signals: [
      { source: 'Trade Data', detail: '3 suppliers flagged payment delays' },
      { source: 'Banking', detail: 'Overdraft facility 85% utilized' },
      { source: 'Companies House', detail: 'No recent capital injection' },
    ],
    recommendation: 'Review cash flow forecasts. Consider covenant breach risk.',
  },
  {
    id: 'news_003',
    timestamp: '2024-11-16T08:22:11Z',
    smeId: '#0531',
    smeName: 'Digital Marketing Hub',
    exposure: '€140K',
    type: 'churn' as const,
    severity: 'warning' as const,
    title: 'Client Churn Alert',
    summary: 'Website testimonials reduced by 40%. LinkedIn shows 2 account managers left. Review scores declining (4.2 → 3.1 in 90 days).',
    signals: [
      { source: 'Reviews', detail: 'Trustpilot: 4.2 → 3.1 stars' },
      { source: 'LinkedIn', detail: '2 account managers departed' },
      { source: 'Web Traffic', detail: 'Case studies page views -60%' },
    ],
    recommendation: 'Monitor closely. Service quality deterioration pattern.',
  },
]

const NewsIntelligence = () => {
  const dispatch = useDispatch()
  const [expandedNews, setExpandedNews] = useState<string | null>(null)
  const [selectedAssignee, setSelectedAssignee] = useState<{ [key: string]: string }>({})
  const [selectedPriority, setSelectedPriority] = useState<{ [key: string]: string }>({})

  const handleRunScenario = (newsItem: typeof newsItems[0]) => {
    const scenario = {
      id: `scenario_${Date.now()}`,
      name: `${newsItem.smeName} - ${newsItem.title}`,
      status: 'in_progress' as const,
      progress: 0,
      createdAt: new Date().toISOString(),
    }
    dispatch(addScenario(scenario))
    dispatch(setActiveTab('scenarios'))
  }

  const handleCreateTask = (newsItem: typeof newsItems[0]) => {
    const task = {
      id: `task_${Date.now()}`,
      title: `Follow up: ${newsItem.smeName} - ${newsItem.title}`,
      smeId: newsItem.smeId,
      smeName: newsItem.smeName,
      exposure: newsItem.exposure,
      assignee: selectedAssignee[newsItem.id] || 'Unassigned',
      priority: (selectedPriority[newsItem.id] || 'medium') as 'high' | 'medium' | 'low',
      dueDate: new Date(Date.now() + 3 * 24 * 60 * 60 * 1000).toISOString(),
      status: 'upcoming' as const,
      description: newsItem.summary,
      source: `News Intelligence (${newsItem.timestamp})`,
      createdAt: new Date().toISOString(),
    }
    dispatch(addTask(task))
    dispatch(setActiveTab('tasks'))
  }

  const handleViewSME = (smeId: string, smeName: string) => {
    // Mock SME object - in real app would fetch from API
    const sme = {
      id: smeId,
      name: smeName,
      riskScore: 68,
      riskCategory: 'critical' as const,
      exposure: '€250K',
      sector: 'Software/Technology',
      geography: 'UK',
      trend: 'up' as const,
      trendValue: 14,
    }
    dispatch(setSelectedSME(sme))
    dispatch(setActiveTab('home'))
  }

  const toggleExpand = (newsId: string) => {
    setExpandedNews(expandedNews === newsId ? null : newsId)
  }

  const getSeverityBadge = (severity: string) => {
    switch (severity) {
      case 'critical':
        return <Badge variant="critical">CRITICAL</Badge>
      case 'warning':
        return <Badge variant="warning">WARNING</Badge>
      default:
        return <Badge variant="info">INFO</Badge>
    }
  }

  return (
    <Card className="h-[calc(100vh-200px)] flex flex-col">
      <CardHeader className="flex-shrink-0">
        <CardTitle>
          <div className="flex items-center gap-2">
            <span className="text-2xl">📰</span>
            <div>
              <div className="text-lg font-semibold">News Intelligence</div>
              <div className="text-xs font-normal text-neutral-500">
                AI-Generated Insights from Alternative Data
              </div>
            </div>
          </div>
        </CardTitle>
      </CardHeader>

      <CardContent className="flex-1 overflow-y-auto">
        <div className="space-y-4">
          {newsItems.map((item) => (
            <div
              key={item.id}
              className="border-2 border-neutral-300 bg-white rounded-lg overflow-hidden hover:border-primary-60 transition-colors"
            >
              {/* News Header */}
              <div className="p-4">
                <div className="flex items-start justify-between mb-3">
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-2">
                      <span className="text-sm font-mono text-neutral-600">
                        {item.smeId} {item.smeName}
                      </span>
                      {getSeverityBadge(item.severity)}
                    </div>
                    <h4 className="text-base font-bold text-neutral-800 mb-1">
                      {item.title}
                    </h4>
                    <div className="flex items-center gap-2 text-xs text-neutral-500">
                      <Clock className="w-3 h-3" />
                      <span>{formatRelativeTime(item.timestamp)}</span>
                      <span>•</span>
                      <span className="font-mono">{item.exposure} exposure</span>
                    </div>
                  </div>
                </div>

                <p className="text-sm text-neutral-700 mb-3">{item.summary}</p>

                {/* Expanded Signals */}
                {expandedNews === item.id && (
                  <div className="mb-3 pt-3 border-t border-neutral-200">
                    <div className="text-xs font-semibold text-neutral-600 uppercase mb-2">
                      Data Signals
                    </div>
                    <div className="space-y-2">
                      {item.signals.map((signal, idx) => (
                        <div
                          key={idx}
                          className="flex items-start gap-2 text-xs bg-neutral-50 p-2 rounded"
                        >
                          <AlertCircle className="w-3 h-3 text-neutral-500 mt-0.5 flex-shrink-0" />
                          <div>
                            <strong>{signal.source}:</strong> {signal.detail}
                          </div>
                        </div>
                      ))}
                    </div>
                    <div className="mt-3 p-2 bg-warning-50 border border-warning-60 rounded text-xs">
                      <strong>💡 Recommendation:</strong> {item.recommendation}
                    </div>
                  </div>
                )}

                {/* Task Creation Inline Form */}
                {expandedNews === item.id && (
                  <div className="mb-3 pt-3 border-t border-neutral-200">
                    <div className="text-xs font-semibold text-neutral-600 uppercase mb-2">
                      Create Task
                    </div>
                    <div className="grid grid-cols-2 gap-2">
                      <div>
                        <label className="text-xs text-neutral-600 block mb-1">
                          Assign to
                        </label>
                        <select
                          value={selectedAssignee[item.id] || ''}
                          onChange={(e) =>
                            setSelectedAssignee({ ...selectedAssignee, [item.id]: e.target.value })
                          }
                          className="w-full px-2 py-1.5 text-xs border border-neutral-600 rounded focus:outline-none focus:ring-2 focus:ring-primary-60 bg-neutral-700 text-neutral-50"
                        >
                          <option value="">Select assignee...</option>
                          <option value="John Smith">John Smith</option>
                          <option value="Jane Doe">Jane Doe</option>
                          <option value="Sarah Chen">Sarah Chen</option>
                          <option value="Mike Wilson">Mike Wilson</option>
                        </select>
                      </div>
                      <div>
                        <label className="text-xs text-neutral-600 block mb-1">
                          Priority
                        </label>
                        <select
                          value={selectedPriority[item.id] || 'medium'}
                          onChange={(e) =>
                            setSelectedPriority({ ...selectedPriority, [item.id]: e.target.value })
                          }
                          className="w-full px-2 py-1.5 text-xs border border-neutral-600 rounded focus:outline-none focus:ring-2 focus:ring-primary-60 bg-neutral-700 text-neutral-50"
                        >
                          <option value="high">High</option>
                          <option value="medium">Medium</option>
                          <option value="low">Low</option>
                        </select>
                      </div>
                    </div>
                  </div>
                )}

                {/* Actions */}
                <div className="flex items-center gap-2">
                  <Button
                    variant="secondary"
                    size="sm"
                    onClick={() => handleCreateTask(item)}
                  >
                    📋 Create Task
                  </Button>
                  <Button
                    variant="secondary"
                    size="sm"
                    onClick={() => handleRunScenario(item)}
                  >
                    🎯 Run Impact Scenario
                  </Button>
                  <Button
                    variant="secondary"
                    size="sm"
                    onClick={() => handleViewSME(item.smeId, item.smeName)}
                  >
                    👁️ View SME
                  </Button>
                  <Button
                    variant="secondary"
                    size="sm"
                    onClick={() => toggleExpand(item.id)}
                  >
                    {expandedNews === item.id ? 'Less' : 'Details'}
                  </Button>
                </div>
              </div>
            </div>
          ))}
        </div>

        {/* Empty State */}
        {newsItems.length === 0 && (
          <div className="text-center py-12 text-neutral-500">
            <div className="text-4xl mb-3">📰</div>
            <p className="text-sm">No news intelligence in the last 24 hours</p>
          </div>
        )}
      </CardContent>
    </Card>
  )
}

export default NewsIntelligence
