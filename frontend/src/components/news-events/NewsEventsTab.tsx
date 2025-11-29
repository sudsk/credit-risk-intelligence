import PredictedEvents from './PredictedEvents'
import NewsIntelligence from './NewsIntelligence'

const NewsEventsTab = () => {
  return (
    <div className="space-y-6">
      {/* Two-column layout */}
      <div className="grid grid-cols-2 gap-6">
        {/* Left: Predicted Events */}
        <PredictedEvents />

        {/* Right: News Intelligence */}
        <NewsIntelligence />
      </div>
    </div>
  )
}

export default NewsEventsTab
