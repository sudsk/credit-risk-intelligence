import { useEffect } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { useQuery } from '@tanstack/react-query';
import { portfolioAPI } from '@/services/api';
import { setMetrics, setSMEs, setLoading, setError } from '@/store/portfolioSlice';
import { RootState } from '@/store';

export const usePortfolio = () => {
  const dispatch = useDispatch();
  const { metrics, smes, selectedSME, filter, searchQuery } = useSelector(
    (state: RootState) => state.portfolio
  );

  // Fetch portfolio metrics
  const { data: metricsData, isLoading: metricsLoading } = useQuery({
    queryKey: ['portfolio-metrics'],
    queryFn: portfolioAPI.getMetrics,
    refetchInterval: 30000, // Refresh every 30 seconds
  });

  // Fetch SMEs
  const { data: smesData, isLoading: smesLoading } = useQuery({
    queryKey: ['smes'],
    queryFn: portfolioAPI.getSMEs,
    refetchInterval: 30000,
  });

  // Update Redux when data changes
  useEffect(() => {
    if (metricsData) {
      dispatch(setMetrics(metricsData));
    }
  }, [metricsData, dispatch]);

  useEffect(() => {
    if (smesData) {
      dispatch(setSMEs(smesData));
    }
  }, [smesData, dispatch]);

  useEffect(() => {
    dispatch(setLoading(metricsLoading || smesLoading));
  }, [metricsLoading, smesLoading, dispatch]);

  // Filtered SMEs
  const filteredSMEs = smes.filter((sme) => {
    // Filter by risk category
    if (filter !== 'all' && sme.riskCategory !== filter) {
      return false;
    }

    // Filter by search query
    if (searchQuery) {
      const query = searchQuery.toLowerCase();
      return (
        sme.id.toLowerCase().includes(query) ||
        sme.name.toLowerCase().includes(query) ||
        sme.sector.toLowerCase().includes(query)
      );
    }

    return true;
  });

  return {
    metrics,
    smes: filteredSMEs,
    selectedSME,
    filter,
    searchQuery,
    isLoading: metricsLoading || smesLoading,
  };
};
