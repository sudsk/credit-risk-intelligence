import { useEffect } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { useQuery, useMutation } from '@tanstack/react-query';
import { scenariosAPI } from '@/services/api';
import { setScenarios, addScenario, setLoading } from '@/store/scenariosSlice';
import { RootState } from '@/store';

export const useScenarios = () => {
  const dispatch = useDispatch();
  const { scenarios, selectedScenario } = useSelector(
    (state: RootState) => state.scenarios
  );

  // Fetch scenarios
  const { data, isLoading } = useQuery({
    queryKey: ['scenarios'],
    queryFn: scenariosAPI.getScenarios,
    refetchInterval: 5000, // Refresh every 5 seconds to catch progress updates
  });

  // Create scenario mutation
  const createMutation = useMutation({
    mutationFn: scenariosAPI.createScenario,
    onSuccess: (newScenario) => {
      dispatch(addScenario(newScenario));
    },
  });

  useEffect(() => {
    if (data) {
      dispatch(setScenarios(data));
    }
  }, [data, dispatch]);

  useEffect(() => {
    dispatch(setLoading(isLoading));
  }, [isLoading, dispatch]);

  const createScenario = (description: string) => {
    return createMutation.mutateAsync(description);
  };

  return {
    scenarios,
    selectedScenario,
    isLoading,
    createScenario,
  };
};
