import React from 'react';
import { useSearchParams } from 'react-router-dom';
import FormFlow from '../components/FormFlow';

export default function ScenarioEditPage() {
  const [searchParams] = useSearchParams();
  const scenarioId = searchParams.get('id');
  const shouldCreate = searchParams.get('create') === 'true';
  
  return <FormFlow scenarioId={scenarioId} shouldCreate={shouldCreate} />;
} 