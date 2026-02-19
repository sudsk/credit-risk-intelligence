import { ButtonHTMLAttributes, ReactNode } from 'react'

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  children: ReactNode
  variant?: 'primary' | 'secondary' | 'danger'
  size?: 'sm' | 'md' | 'lg'
  fullWidth?: boolean
}

const variantStyles: Record<string, React.CSSProperties> = {
  primary: { background: 'var(--uui-primary-60)', color: 'white' },
  secondary: { background: 'var(--uui-neutral-60)', color: 'var(--uui-text-primary)' },
  danger: { background: 'var(--uui-critical-60)', color: 'white' },
}

const sizeStyles: Record<string, React.CSSProperties> = {
  sm: { padding: '4px 12px', fontSize: '11px' },
  md: { padding: '6px 12px', fontSize: '12px' },
  lg: { padding: '9px 18px', fontSize: '14px' },
}

export const Button = ({ children, variant = 'primary', size = 'md', fullWidth = false, style, ...props }: ButtonProps) => (
  <button
    style={{
      border: 'none',
      borderRadius: 'var(--uui-border-radius)',
      cursor: props.disabled ? 'not-allowed' : 'pointer',
      opacity: props.disabled ? 0.5 : 1,
      transition: 'all 0.2s',
      display: 'inline-flex',
      alignItems: 'center',
      justifyContent: 'center',
      gap: '6px',
      fontFamily: 'var(--uui-font)',
      fontWeight: 600,
      width: fullWidth ? '100%' : undefined,
      ...variantStyles[variant],
      ...sizeStyles[size],
      ...style,
    }}
    {...props}
  >
    {children}
  </button>
)