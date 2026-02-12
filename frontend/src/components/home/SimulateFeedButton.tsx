import { useState } from 'react'
import { useDispatch } from 'react-redux'
import { Zap, Loader } from 'lucide-react'
import { Button } from '../common/Button'
import { alertAPI } from '@/services/api'
import { showAlert } from '@/store/alertSlice'

const SimulateFeedButton = () => {
  const dispatch = useDispatch()
  const [isProcessing, setIsProcessing] = useState(false)

  const handleSimulate = async () => {
    setIsProcessing(true)

    try {
      // Simulate processing delay
      await new Promise(resolve => setTimeout(resolve, 2500))

      // Call API to get simulated alert
      const alert = await alertAPI.simulateFeed()

      // Show alert toast
      dispatch(showAlert(alert))
    } catch (error) {
      console.error('Failed to simulate feed:', error)
    } finally {
      setIsProcessing(false)
    }
  }

  return (
    <Button
      variant="primary"
      size="md"
      onClick={handleSimulate}
      disabled={isProcessing}
      className="relative"
    >
      {isProcessing ? (
        <>
          <Loader className="w-4 h-4 animate-spin" />
          Processing 100 articles...
        </>
      ) : (
        <>
          <Zap className="w-4 h-4" />
          Simulate Live Feed
        </>
      )}
    </Button>
  )
}

export default SimulateFeedButton
