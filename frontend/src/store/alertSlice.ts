import { createSlice, PayloadAction } from '@reduxjs/toolkit'
import type { Alert } from '@/services/types'

interface AlertState {
  currentAlert: Alert | null
  alertHistory: Alert[]
  showAlert: boolean
  loading: boolean
}

const initialState: AlertState = {
  currentAlert: null,
  alertHistory: [],
  showAlert: false,
  loading: false,
}

const alertSlice = createSlice({
  name: 'alerts',
  initialState,
  reducers: {
    showAlert: (state, action: PayloadAction<Alert>) => {
      state.currentAlert = action.payload
      state.showAlert = true
    },
    dismissAlert: (state) => {
      state.showAlert = false
      // Keep currentAlert for a moment to allow animation
      setTimeout(() => {
        state.currentAlert = null
      }, 300)
    },
    addToHistory: (state, action: PayloadAction<Alert>) => {
      state.alertHistory.unshift(action.payload)
      // Keep only last 50 alerts
      if (state.alertHistory.length > 50) {
        state.alertHistory = state.alertHistory.slice(0, 50)
      }
    },
    markAsReviewed: (state, action: PayloadAction<string>) => {
      const alert = state.alertHistory.find(a => a.id === action.payload)
      if (alert) {
        alert.dismissed = true
      }
    },
    clearHistory: (state) => {
      state.alertHistory = []
    },
    setLoading: (state, action: PayloadAction<boolean>) => {
      state.loading = action.payload
    },
  },
})

export const {
  showAlert,
  dismissAlert,
  addToHistory,
  markAsReviewed,
  clearHistory,
  setLoading,
} = alertSlice.actions

export default alertSlice.reducer
