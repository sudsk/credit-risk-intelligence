import PortfolioMetrics from './PortfolioMetrics'
import SMEList from './SMEList'
import SMEDetailPanel from './SMEDetailPanel'
import SimulateFeedButton from './SimulateFeedButton'
import AlertToast from '../common/AlertToast'

const HomeTab = () => {
  return (
    <div className="space-y-6">
      {/* Alert Toast - Global */}
      <AlertToast /> {/* ADD */}

      {/* Portfolio Header with Simulate Button */}
      <div className="flex items-center justify-between">
        <h2 style={{ fontSize: '18px', fontWeight: 600, color: 'var(--uui-text-primary)' }}>
          Portfolio Overview
        </h2>
        <SimulateFeedButton /> {/* ADD */}
      </div>

      {/* Portfolio Metrics Cards */}
      <PortfolioMetrics />

      {/* SME List and Detail Panel */}
      <div className="grid grid-cols-12 gap-6">
        {/* SME List - Left Panel (5 columns) */}
        <div className="col-span-5">
          <SMEList />
        </div>

        {/* SME Detail Panel - Right Panel (7 columns) */}
        <div className="col-span-7">
          <SMEDetailPanel />
        </div>
      </div>
    </div>
  )
}

export default HomeTab
