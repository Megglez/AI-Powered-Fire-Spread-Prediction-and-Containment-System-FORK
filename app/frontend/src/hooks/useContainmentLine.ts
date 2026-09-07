import { useState, useCallback } from 'react';
import type { CreateContainmentLine, ContainmentLine } from '../types/ContainmentLines';
import { apiCall } from '../lib/api';

export function useContainmentLine(onDraw?: () => void) {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const submitLine = useCallback(
    async (body: CreateContainmentLine): Promise<ContainmentLine> => {
      setLoading(true);
      setError(null);
      try {
        const saved: ContainmentLine = await apiCall('/api/firefighter/containment-line', 'POST', 
          body,
        );
        return saved;
      } catch (err: unknown) {
        const message = err instanceof Error ? err.message : 'Unknown error';
        console.error('Failed to save the containment line', err);
        setError(message);
        throw err;
      } finally {
        setLoading(false);
        onDraw?.();
      }
    },
    [onDraw]
  );

  const fetchLines = useCallback(
    async (fireRef: string): Promise<ContainmentLine[]> => {
      try{
        const resp = await apiCall(
          `/api/firefighter/containment-lines/${encodeURIComponent(fireRef)}`
        );
        return resp?.data ?? [];
      }catch (err){
        console.error('Failed to load containment lines', err);
        return [];
      }
    }, []
  )

  return { submitLine, fetchLines, loading, error };
}
