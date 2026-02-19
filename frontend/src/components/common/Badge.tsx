interface BadgeProps {
  children: React.ReactNode
  variant?: 'critical' | 'warning' | 'info' | 'success'
}

const styles: Record<string, React.CSSProperties> = {
  critical: { background: 'rgba(229,98,72,0.15)', color: 'var(--uui-critical-70)', border: '1px solid rgba(229,98,72,0.3)' },
  warning: { background: 'rgba(244,184,58,0.15)', color: 'var(--uui-warning-70)', border: '1px solid rgba(244,184,58,0.3)' },
  info: { background: 'rgba(72,164,208,0.15)', color: 'var(--uui-primary-70)', border: '1px solid rgba(72,164,208,0.3)' },
  success: { background: 'rgba(131,185,24,0.15)', color: 'var(--uui-success-70)', border: '1px solid rgba(131,185,24,0.3)' },
}

export const Badge = ({ children, variant = 'info' }: BadgeProps) => (
  <span style={{
    display: 'inline-flex', padding: '3px 9px',
    borderRadius: 'var(--uui-border-radius)',
    fontSize: '11px', fontWeight: 600,
    ...styles[variant]
  }}>
    {children}
  </span>
)