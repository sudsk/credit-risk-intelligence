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
    <form onSubmit={handleSubmit} className="p-4 border-t border-neutral-300 bg-white rounded-b-lg">
      <div className="flex gap-2">
        <textarea
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyPress={handleKeyPress}
          placeholder="Ask me anything about your portfolio..."
          disabled={disabled}
          rows={2}
          className="flex-1 px-3 py-2 text-sm border border-neutral-600 rounded resize-none focus:outline-none focus:ring-2 focus:ring-primary-60 bg-neutral-700 text-neutral-50 disabled:bg-neutral-800 disabled:cursor-not-allowed"
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
      <p className="text-xs text-neutral-500 mt-2">
        Press Enter to send • Shift+Enter for new line
      </p>
    </form>
  )
}

export default ChatInput
