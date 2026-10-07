// Empty VITE_API_URL = same origin (behind the load balancer); unset = local backend
export const API_BASE_URL = import.meta.env.VITE_API_URL ?? 'http://localhost:8000';
export const WS_URL = import.meta.env.VITE_WS_URL || 'ws://localhost:8000/ws';

export const RISK_CATEGORIES = {
  critical: {
    label: 'Critical Risk',
    range: '80-100',
    color: 'critical',
    min: 80,
    max: 100,
  },
  medium: {
    label: 'Medium Risk',
    range: '50-79',
    color: 'warning',
    min: 50,
    max: 79,
  },
  stable: {
    label: 'Low Risk',
    range: '0-49',
    color: 'success',
    min: 0,
    max: 49,
  },
} as const;

export const PRIORITY_COLORS = {
  high: 'critical',
  medium: 'warning',
  low: 'primary',
} as const;

export const STATUS_COLORS = {
  overdue: 'critical',
  due_today: 'warning',
  upcoming: 'primary',
  completed: 'success',
} as const;
