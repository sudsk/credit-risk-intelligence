import { ReactNode } from 'react'

interface CardProps {
  children: ReactNode
  className?: string
  style?: React.CSSProperties
}

export const Card = ({ children, style }: CardProps) => (
  <div style={{
    background: 'var(--uui-surface-main)',
    borderRadius: 'var(--uui-border-radius)',
    border: '1px solid var(--uui-neutral-60)',
    overflow: 'hidden',
    ...style
  }}>
    {children}
  </div>
)

export const CardHeader = ({ children, action }: { children: ReactNode; action?: ReactNode }) => (
  <div style={{
    padding: '12px 18px',
    borderBottom: '1px solid var(--uui-neutral-60)',
    background: 'var(--uui-neutral-70)',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'space-between',
  }}>
    <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>{children}</div>
    {action && <div>{action}</div>}
  </div>
)

export const CardTitle = ({ children }: { children: ReactNode }) => (
  <h2 style={{ fontSize: '14px', fontWeight: 600, color: 'var(--uui-text-primary)' }}>
    {children}
  </h2>
)

export const CardContent = ({ children, style }: CardProps) => (
  <div style={{ padding: '18px', ...style }}>{children}</div>
)