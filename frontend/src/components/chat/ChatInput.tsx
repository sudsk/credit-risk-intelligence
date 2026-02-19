import { useState } from 'react'
import { Send } from 'lucide-react'
import { Button } from '../common/Button'

interface ChatInputProps {
  onSend: (message: string) => void
  disabled?: boolean
}

const ChatInput = ({ onSend, disabled = false }: ChatInputProps) => {
  const [input, setInput] = useState('')

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (!input.trim() || disabled) return

    onSend(input.trim())
    setInput('')
  }

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSubmit(e)
    }
  }

  return (
    <form onSubmit={handleSubmit} style={{ padding: '12px 18px', borderTop: '1px solid var(--uui-neutral-60)', background: 'var(--uui-neutral-70)', display: 'flex', flexDirection: 'column', gap: '8px' }}>
      <div className="flex gap-2">
        <textarea
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyPress={handleKeyPress}
          placeholder="Ask me anything about your portfolio..."
          disabled={disabled}
          rows={2}
          style={{ flex: 1, padding: '9px 12px', background: 'var(--uui-neutral-80)', border: '1px solid var(--uui-neutral-60)', borderRadius: 'var(--uui-border-radius)', color: 'var(--uui-text-primary)', fontSize: '13px', fontFamily: 'var(--uui-font)', outline: 'none', resize: 'none' }}
        />
        <Button
          type="submit"
          variant="primary"
          size="md"
          disabled={!input.trim() || disabled}
          className="self-end"
        >
          <Send className="w-4 h-4" />
        </Button>
      </div>
      <p style={{ fontSize: '11px', color: 'var(--uui-text-tertiary)' }}>
        Press Enter to send • Shift+Enter for new line
      </p>
    </form>
  )
}

export default ChatInput
