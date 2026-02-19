import { ReactNode } from 'react'
import { cn } from '@/utils/formatters'

interface CardProps {
  children: ReactNode
  className?: string
  fullWidth?: boolean
}

export const Card = ({ children, className, fullWidth = false }: CardProps) => {
  return (
    <div
      className={cn(
        'bg-neutral-800 rounded-lg border border-neutral-600 shadow-sm',
        fullWidth && 'w-full',
        className
      )}
    >
      {children}
    </div>
  )
}

interface CardHeaderProps {
  children: ReactNode
  className?: string
  action?: ReactNode
}

export const CardHeader = ({ children, className, action }: CardHeaderProps) => {
  return (
    <div
      className={cn(
        'px-6 py-4 border-b border-neutral-600 flex items-center justify-between bg-neutral-700',
        className
      )}
    >
      <div className="flex items-center gap-3">{children}</div>
      {action && <div>{action}</div>}
    </div>
  )
}

export const CardTitle = ({ children }: { children: ReactNode }) => {
  return <h2 className="text-lg font-semibold text-neutral-800">{children}</h2>
}

export const CardContent = ({ children, className }: CardProps) => {
  return <div className={cn('px-6 py-4', className)}>{children}</div>
}
