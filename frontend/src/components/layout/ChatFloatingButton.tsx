import { MessageCircle, X } from 'lucide-react'
import { useDispatch, useSelector } from 'react-redux'
import { RootState } from '@/store'
import { setIsOpen } from '@/store/chatSlice'

const ChatFloatingButton = () => {
  const dispatch = useDispatch()
  const isOpen = useSelector((state: RootState) => state.chat.isOpen)

  return (
    <button
      onClick={() => dispatch(setIsOpen(!isOpen))}
      aria-label="Toggle chat"
      style={{
        position: 'fixed', bottom: '24px', right: '24px', zIndex: 50,
        width: '56px', height: '56px', borderRadius: '50%',
        background: 'var(--uui-primary-60)',
        border: 'none', cursor: 'pointer',
        boxShadow: 'var(--uui-shadow-level-3)',
        display: 'flex', alignItems: 'center', justifyContent: 'center',
        color: 'white', transition: 'all 0.2s',
      }}
    >
      {isOpen ? <X size={24} /> : <MessageCircle size={24} />}
    </button>
  )
}

export default ChatFloatingButton