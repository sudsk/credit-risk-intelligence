import { createSlice, PayloadAction } from '@reduxjs/toolkit';
import { SME, PortfolioMetrics } from '@/services/types';

interface PortfolioState {
  metrics: PortfolioMetrics | null;
  smes: SME[];
  selectedSME: SME | null;
  filter: 'all' | 'critical' | 'medium' | 'stable';
  searchQuery: string;
  loading: boolean;
  error: string | null;
}

const initialState: PortfolioState = {
  metrics: null,
  smes: [],
  selectedSME: null,
  filter: 'all',
  searchQuery: '',
  loading: false,
  error: null,
};

const portfolioSlice = createSlice({
  name: 'portfolio',
  initialState,
  reducers: {
    setMetrics: (state, action: PayloadAction<PortfolioMetrics>) => {
      state.metrics = action.payload;
    },
    setSMEs: (state, action: PayloadAction<SME[]>) => {
      state.smes = action.payload;
    },
    setSelectedSME: (state, action: PayloadAction<SME | null>) => {
      state.selectedSME = action.payload;
    },
    setFilter: (state, action: PayloadAction<'all' | 'critical' | 'medium' | 'stable'>) => {
      state.filter = action.payload;
    },
    setSearchQuery: (state, action: PayloadAction<string>) => {
      state.searchQuery = action.payload;
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
  setMetrics,
  setSMEs,
  setSelectedSME,
  setFilter,
  setSearchQuery,
  setLoading,
  setError,
} = portfolioSlice.actions;

export default portfolioSlice.reducer;
