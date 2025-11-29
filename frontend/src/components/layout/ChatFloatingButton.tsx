import { MessageCircle, X } from 'lucide-react'
import { useDispatch, useSelector } from 'react-redux'
import { RootState } from '@/store'
import { setIsOpen } from '@/store/chatSlice'

const ChatFloatingButton = () => {
  const dispatch = useDispatch()
  const isOpen = useSelector((state: RootState) => state.chat.isOpen)

  const handleToggle = () => {
    dispatch(setIsOpen(!isOpen))
  }

  return (
    <button
      onClick={handleToggle}
      className="fixed bottom-6 right-6 z-50 w-14 h-14 bg-primary-60 text-white rounded-full shadow-lg hover:bg-primary-70 transition-all flex items-center justify-center"
      aria-label="Toggle chat"
    >
      {isOpen ? (
        <X className="w-6 h-6" />
      ) : (
        <MessageCircle className="w-6 h-6" />
      )}
    </button>
  )
}

export default ChatFloatingButton
