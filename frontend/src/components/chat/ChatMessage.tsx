import { formatRelativeTime } from '@/utils/formatters'
import type { ChatMessage as ChatMessageType } from '@/services/types'

interface ChatMessageProps {
  message: ChatMessageType
}

const ChatMessage = ({ message }: ChatMessageProps) => {
  const isUser = message.role === 'user'

  return (
    <div style={{ display: 'flex', alignItems: 'flex-start', gap: '12px', flexDirection: isUser ? 'row-reverse' : 'row' }}>
      {/* Avatar */}
      <div style={{
        width: '32px', height: '32px', borderRadius: '50%', flexShrink: 0,
        background: isUser ? 'var(--uui-neutral-60)' : 'var(--uui-primary-60)',
        display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '14px',
      }}>
        {isUser ? '👤' : '🤖'}
      </div>

      {/* Bubble */}
      <div style={{ display: 'flex', flexDirection: 'column', alignItems: isUser ? 'flex-end' : 'flex-start', maxWidth: '85%' }}>
        <div style={{
          padding: '10px 14px',
          borderRadius: 'var(--uui-border-radius)',
          background: isUser ? 'var(--uui-primary-60)' : 'var(--uui-neutral-70)',
          border: isUser ? 'none' : '1px solid var(--uui-neutral-60)',
          color: 'var(--uui-text-primary)',
          fontSize: '13px',
          lineHeight: 1.5,
          whiteSpace: 'pre-wrap',
        }}>
          {message.content}
        </div>
        <span style={{ fontSize: '11px', color: 'var(--uui-text-tertiary)', marginTop: '4px' }}>
          {formatRelativeTime(message.timestamp)}
        </span>
      </div>
    </div>
  )
}

export default ChatMessage