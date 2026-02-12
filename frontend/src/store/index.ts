import { configureStore } from '@reduxjs/toolkit';
import portfolioReducer from './portfolioSlice';
import scenariosReducer from './scenariosSlice';
import tasksReducer from './tasksSlice';
import chatReducer from './chatSlice';
import uiReducer from './uiSlice';
import alertReducer from './alertSlice'

export const store = configureStore({
  reducer: {
    portfolio: portfolioReducer,
    scenarios: scenariosReducer,
    tasks: tasksReducer,
    chat: chatReducer,
    ui: uiReducer,
    alerts: alertReducer,
  },
});

export type RootState = ReturnType<typeof store.getState>;
export type AppDispatch = typeof store.dispatch;
