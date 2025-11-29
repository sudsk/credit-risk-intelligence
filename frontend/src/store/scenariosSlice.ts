import { createSlice, PayloadAction } from '@reduxjs/toolkit';
import { Scenario } from '@/services/types';

interface ScenariosState {
  scenarios: Scenario[];
  selectedScenario: Scenario | null;
  loading: boolean;
  error: string | null;
}

const initialState: ScenariosState = {
  scenarios: [],
  selectedScenario: null,
  loading: false,
  error: null,
};

const scenariosSlice = createSlice({
  name: 'scenarios',
  initialState,
  reducers: {
    setScenarios: (state, action: PayloadAction<Scenario[]>) => {
      state.scenarios = action.payload;
    },
    addScenario: (state, action: PayloadAction<Scenario>) => {
      state.scenarios.unshift(action.payload);
    },
    updateScenario: (state, action: PayloadAction<Scenario>) => {
      const index = state.scenarios.findIndex(s => s.id === action.payload.id);
      if (index !== -1) {
        state.scenarios[index] = action.payload;
      }
    },
    setSelectedScenario: (state, action: PayloadAction<Scenario | null>) => {
      state.selectedScenario = action.payload;
    },
    setLoading: (state, action: PayloadAction<boolean>) => {
      state.loading = action.payload;
    },
    setError: (state, action: PayloadAction<string | null>) => {
      state.error = action.payload;
    },
  },
});

export const {
  setScenarios,
  addScenario,
  updateScenario,
  setSelectedScenario,
  setLoading,
  setError,
} = scenariosSlice.actions;

export default scenariosSlice.reducer;
