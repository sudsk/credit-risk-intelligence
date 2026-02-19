import { useEffect, useRef, useState } from 'react'
import { useDispatch, useSelector } from 'react-redux'
import { X, Send } from 'lucide-react'
import { RootState } from '@/store'
import { setIsOpen, addMessage, setIsTyping } from '@/store/chatSlice'
import { chatAPI } from '@/services/api'
import ChatMessage from './ChatMessage'
import ChatInput from './ChatInput'
import { cn } from '@/utils/formatters'

const ChatModal = () => {
  const dispatch = useDispatch()
  const { messages, isTyping } = useSelector((state: RootState) => state.chat)
  const messagesEndRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    // Auto-scroll to bottom when new messages arrive
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, isTyping])

  useEffect(() => {
    // Add initial AI greeting if no messages
    if (messages.length === 0) {
      dispatch(
        addMessage({
          id: 'initial',
          role: 'assistant',
          content: `Hello! I'm your Credit Risk AI Assistant. I have access to your portfolio of 1,284 SMEs and can help you with:

- Analyzing specific SME health and risk factors
- Running what-if scenarios on your portfolio
- Collecting news and sentiment for any SME
- Creating tasks and investigations
- Answering questions about your portfolio metrics

What would you like to know?`,
          timestamp: new Date().toISOString(),
        })
      )
    }
  }, [])

  const handleClose = () => {
    dispatch(setIsOpen(false))
  }

  const handleSendMessage = async (content: string) => {
    // Add user message
    const userMessage = {
      id: `user_${Date.now()}`,
      role: 'user' as const,
      content,
      timestamp: new Date().toISOString(),
    }
    dispatch(addMessage(userMessage))

    // Show typing indicator
    dispatch(setIsTyping(true))

    try {
      // Send to API
      const response = await chatAPI.sendMessage(content);

      const assistantMessage = {
        id: `assistant_${Date.now()}`,
        role: 'assistant' as const,
        content: response.content,
        timestamp: new Date().toISOString(),
      }
      dispatch(addMessage(assistantMessage))
    } catch (error) {
      console.error('Failed to send message:', error)
      const errorMessage = {
        id: `error_${Date.now()}`,
        role: 'assistant' as const,
        content: 'Sorry, I encountered an error. Please try again.',
        timestamp: new Date().toISOString(),
      }
      dispatch(addMessage(errorMessage))
    } finally {
      dispatch(setIsTyping(false))
    }
  }
  return (
    <div style={{ position: 'fixed', bottom: '24px', right: '24px', zIndex: 1001, width: '420px', height: '600px', background: 'var(--uui-surface-main)', borderRadius: 'var(--uui-border-radius)', border: '1px solid var(--uui-neutral-60)', boxShadow: 'var(--uui-shadow-level-3)', display: 'flex', flexDirection: 'column', overflow: 'hidden' }}>
      {/* Header */}
      <div style={{ padding: '12px 18px', background: 'var(--uui-neutral-70)', borderBottom: '1px solid var(--uui-neutral-60)', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-full bg-white bg-opacity-20 flex items-center justify-center">
            <span className="text-lg">🤖</span>
          </div>
          <div>
            <h3 className="font-semibold">Credit Risk AI Assistant</h3>
            <p className="text-xs text-white text-opacity-90">Always here to help</p>
          </div>
        </div>
        <button
          onClick={handleClose}
          className="w-8 h-8 rounded hover:bg-white hover:bg-opacity-20 flex items-center justify-center transition-colors"
        >
          <X className="w-5 h-5" />
        </button>
      </div>

      {/* Messages */}
      <div style={{ flex: 1, overflowY: 'auto', padding: '18px', display: 'flex', flexDirection: 'column', gap: '12px', background: 'var(--uui-neutral-90)' }}>
        {messages.map((message) => (
          <ChatMessage key={message.id} message={message} />
        ))}
        {isTyping && (
          <div className="flex items-start gap-3">
            <div className="w-8 h-8 rounded-full bg-primary-60 flex items-center justify-center flex-shrink-0">
              <span className="text-sm">🤖</span>
            </div>
            <div className="bg-white rounded-lg px-4 py-3 max-w-[85%]">
              <div className="flex gap-1">
                <span className="w-2 h-2 bg-neutral-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
                <span className="w-2 h-2 bg-neutral-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
                <span className="w-2 h-2 bg-neutral-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
              </div>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <ChatInput onSend={handleSendMessage} disabled={isTyping} />
    </div>
  )
}

export default ChatModal
