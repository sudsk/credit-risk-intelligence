import ReactMarkdown from 'react-markdown'
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
        }}>
          {isUser ? (
            message.content
          ) : (
            <ReactMarkdown
              components={{
                p: ({ children }) => <p style={{ margin: '0 0 8px 0' }}>{children}</p>,
                ul: ({ children }) => <ul style={{ margin: '4px 0', paddingLeft: '18px' }}>{children}</ul>,
                ol: ({ children }) => <ol style={{ margin: '4px 0', paddingLeft: '18px' }}>{children}</ol>,
                li: ({ children }) => <li style={{ margin: '2px 0' }}>{children}</li>,
                strong: ({ children }) => <strong style={{ color: 'var(--uui-text-primary)', fontWeight: 600 }}>{children}</strong>,
                h3: ({ children }) => <h3 style={{ fontSize: '13px', fontWeight: 700, margin: '8px 0 4px 0' }}>{children}</h3>,
                h4: ({ children }) => <h4 style={{ fontSize: '13px', fontWeight: 600, margin: '6px 0 4px 0' }}>{children}</h4>,
                code: ({ children }) => <code style={{ fontFamily: 'var(--uui-font-mono)', fontSize: '12px', background: 'var(--uui-neutral-80)', padding: '1px 4px', borderRadius: '3px' }}>{children}</code>,
              }}
            >
              {message.content}
            </ReactMarkdown>
          )}
        </div>
        <span style={{ fontSize: '11px', color: 'var(--uui-text-tertiary)', marginTop: '4px' }}>
          {formatRelativeTime(message.timestamp)}
        </span>
      </div>
    </div>
  )
}

export default ChatMessage