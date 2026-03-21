// hooks/useSSEStream.ts

import { useState, useCallback } from 'react';
import { PaceResult, SSEEvent } from '../types';
import { analyzeJD } from '../lib/api';

export type SSEStage =
  | 'idle'
  | 'extracting'
  | 'computing'
  | 'generating'
  | 'verifying'
  | 'complete'
  | 'error';

const STAGE_LABELS: Record<SSEStage, string> = {
  idle: '',
  extracting: 'Extracting skills...',
  computing: 'Computing mastery...',
  generating: 'Generating paths...',
  verifying: 'Verifying with Z3...',
  complete: 'Done!',
  error: 'Error occurred',
};

interface UseSSEStreamReturn {
  stage: SSEStage;
  stageLabel: string;
  result: PaceResult | null;
  error: string | null;
  isStreaming: boolean;
  startStream: (sessionId: string, jdText: string) => Promise<PaceResult | null>;
  reset: () => void;
}

export function useSSEStream(): UseSSEStreamReturn {
  const [stage, setStage] = useState<SSEStage>('idle');
  const [result, setResult] = useState<PaceResult | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isStreaming, setIsStreaming] = useState(false);

  const handleEvent = useCallback((event: SSEEvent) => {
    switch (event.event_type) {
      case 'mastery_map':
        setStage('computing');
        break;
      case 'paths':
        setStage('generating');
        break;
      case 'verifying':
        setStage('verifying');
        break;
      case 'complete':
        setStage('complete');
        setResult(event.payload as PaceResult);
        break;
      case 'error':
        setStage('error');
        setError(String(event.payload));
        break;
      default:
        // unknown events are ignored safely
        break;
    }
  }, []);

  const startStream = useCallback(
    async (sessionId: string, jdText: string) => {
      setIsStreaming(true);
      setError(null);
      setResult(null);
      setStage('extracting');

      try {
        const finalResult = await analyzeJD(sessionId, jdText, handleEvent);
        setResult(finalResult);
        setStage('complete');
        return finalResult;
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Unknown error');
        setStage('error');
        return null;
      } finally {
        setIsStreaming(false);
      }
    },
    [handleEvent]
  );

  const reset = useCallback(() => {
    setStage('idle');
    setResult(null);
    setError(null);
    setIsStreaming(false);
  }, []);

  return {
    stage,
    stageLabel: STAGE_LABELS[stage],
    result,
    error,
    isStreaming,
    startStream,
    reset,
  };
}
