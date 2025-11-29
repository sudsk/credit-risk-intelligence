import { ButtonHTMLAttributes, ReactNode } from 'react'
import { cn } from '@/utils/formatters'

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  children: ReactNode
  variant?: 'primary' | 'secondary' | 'danger'
  size?: 'sm' | 'md' | 'lg'
  fullWidth?: boolean
}

export const Button = ({
  children,
  variant = 'primary',
  size = 'md',
  fullWidth = false,
  className,
  ...props
}: ButtonProps) => {
  return (
    <button
      className={cn(
        'rounded font-medium transition-colors inline-flex items-center justify-center gap-2',
        // Variants
        variant === 'primary' && 'bg-primary-60 text-white hover:bg-primary-70',
        variant === 'secondary' && 'bg-neutral-300 text-neutral-800 hover:bg-neutral-400',
        variant === 'danger' && 'bg-critical-60 text-white hover:bg-critical-70',
        // Sizes
        size === 'sm' && 'px-3 py-1.5 text-xs',
        size === 'md' && 'px-4 py-2 text-sm',
        size === 'lg' && 'px-6 py-3 text-base',
        // Width
        fullWidth && 'w-full',
        // Disabled
        props.disabled && 'opacity-50 cursor-not-allowed',
        className
      )}
      {...props}
    >
      {children}
    </button>
  )
}
