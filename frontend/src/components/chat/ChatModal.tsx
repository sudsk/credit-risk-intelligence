import { useEffect, useRef } from 'react'
import { useDispatch, useSelector } from 'react-redux'
import { X } from 'lucide-react'
import { RootState } from '@/store'
import { setIsOpen, addMessage, setIsTyping } from '@/store/chatSlice'
import { chatAPI } from '@/services/api'
import ChatMessage from './ChatMessage'
import ChatInput from './ChatInput'

const ChatModal = () => {
  const dispatch = useDispatch()
  const { messages, isTyping } = useSelector((state: RootState) => state.chat)
  const messagesEndRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, isTyping])

  useEffect(() => {
    if (messages.length === 0) {
      dispatch(addMessage({
        id: 'initial',
        role: 'assistant',
        content: `Hello! I'm your Credit Risk AI Assistant. I have access to your portfolio of 1,284 SMEs and can help you with:\n\n- Analyzing specific SME health and risk factors\n- Running what-if scenarios on your portfolio\n- Collecting news and sentiment for any SME\n- Creating tasks and investigations\n- Answering questions about your portfolio metrics\n\nWhat would you like to know?`,
        timestamp: new Date().toISOString(),
      }))
    }
  }, [])

  const handleClose = () => dispatch(setIsOpen(false))

  const handleSendMessage = async (content: string) => {
    dispatch(addMessage({ id: `user_${Date.now()}`, role: 'user', content, timestamp: new Date().toISOString() }))
    dispatch(setIsTyping(true))
    try {
      const response = await chatAPI.sendMessage(content)
      dispatch(addMessage({ id: `assistant_${Date.now()}`, role: 'assistant', content: response.content, timestamp: new Date().toISOString() }))
    } catch {
      dispatch(addMessage({ id: `error_${Date.now()}`, role: 'assistant', content: 'Sorry, I encountered an error. Please try again.', timestamp: new Date().toISOString() }))
    } finally {
      dispatch(setIsTyping(false))
    }
  }

  return (
    <div style={{ position: 'fixed', bottom: '24px', right: '24px', zIndex: 1001, width: '420px', height: '600px', background: 'var(--uui-surface-main)', borderRadius: 'var(--uui-border-radius)', border: '1px solid var(--uui-neutral-60)', boxShadow: 'var(--uui-shadow-level-3)', display: 'flex', flexDirection: 'column', overflow: 'hidden' }}>

      {/* Header */}
      <div style={{ padding: '12px 18px', background: 'var(--uui-neutral-70)', borderBottom: '1px solid var(--uui-neutral-60)', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <div style={{ width: '36px', height: '36px', borderRadius: '50%', background: 'var(--uui-neutral-60)', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '18px' }}>
            🤖
          </div>
          <div>
            <div style={{ fontSize: '13px', fontWeight: 600, color: 'var(--uui-text-primary)' }}>Credit Risk AI Assistant</div>
            <div style={{ fontSize: '11px', color: 'var(--uui-text-tertiary)' }}>Always here to help</div>
          </div>
        </div>
        <button onClick={handleClose} style={{ width: '28px', height: '28px', borderRadius: 'var(--uui-border-radius)', background: 'var(--uui-neutral-60)', border: 'none', cursor: 'pointer', display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'var(--uui-text-primary)' }}>
          <X size={16} />
        </button>
      </div>

      {/* Messages */}
      <div style={{ flex: 1, overflowY: 'auto', padding: '18px', display: 'flex', flexDirection: 'column', gap: '12px', background: 'var(--uui-neutral-90)' }}>
        {messages.map((message) => (
          <ChatMessage key={message.id} message={message} />
        ))}

        {/* Typing indicator */}
        {isTyping && (
          <div style={{ display: 'flex', alignItems: 'flex-start', gap: '12px' }}>
            <div style={{ width: '32px', height: '32px', borderRadius: '50%', background: 'var(--uui-primary-60)', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '14px', flexShrink: 0 }}>
              🤖
            </div>
            <div style={{ padding: '10px 14px', background: 'var(--uui-neutral-70)', border: '1px solid var(--uui-neutral-60)', borderRadius: 'var(--uui-border-radius)' }}>
              <div style={{ display: 'flex', gap: '4px' }}>
                {[0, 150, 300].map((delay) => (
                  <span key={delay} style={{ width: '8px', height: '8px', borderRadius: '50%', background: 'var(--uui-text-tertiary)', display: 'inline-block', animation: 'bounce 1.4s infinite', animationDelay: `${delay}ms` }} />
                ))}
              </div>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      <ChatInput onSend={handleSendMessage} disabled={isTyping} />
    </div>
  )
}

export default ChatModal