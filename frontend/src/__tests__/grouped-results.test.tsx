import { render, screen, fireEvent } from '@testing-library/react';
import { test, expect, vi } from 'vitest';
import { Results } from '../components/Results';
import type { components } from '../types';

test('college preferences filter colleges, retain portable awards, and keep Explore collapsed', () => {
  const scholarships = [
    ['gatech-stamps-gold', 'Tech award'], ['auburn-charter', 'Auburn award'],
    ['burger-king-general', 'Company award'], ['cooke-college', 'Foundation award'],
  ].map(([id,name]) => ({id,name,deadline:'2027-01-01'})) as components['schemas']['Scholarship'][];
  const matches = scholarships.map(s => ({scholarship_id:s.id,group:'matches',fit:s.id==='cooke-college'?'Explore':'Possible match',fit_reason:'Confirm remaining rules.',timing:'unknown',evidence_label:s.id==='cooke-college'?'conflicting':'source_checked',conditions:[],followups:[],sort_key:[1,0,s.name,s.id]})) as components['schemas']['MatchResult'][];
  render(<Results scholarships={scholarships} matches={matches} selected={[]} onSelect={vi.fn()} onAsk={vi.fn()} collegeChoices={['Georgia Institute of Technology']} />);
  expect(screen.getByText('2 matches · 1 to explore')).toBeVisible();
  expect(screen.queryByText('Auburn award')).not.toBeInTheDocument();
  expect(screen.getByText('Company award')).toBeVisible();
  expect(screen.getByText('Foundation award')).not.toBeVisible();
  expect(screen.queryByText('source checked')).not.toBeInTheDocument();
  fireEvent.click(screen.getByText('Explore other opportunities (1)'));
  expect(screen.getByText('Source details differ')).toBeVisible();
  fireEvent.change(screen.getByLabelText('College location'), {target:{value:'GA'}});
  expect(screen.getByText('1 matches · 0 to explore')).toBeVisible();
  expect(screen.queryByText('Company award')).not.toBeInTheDocument();
  fireEvent.change(screen.getByLabelText('College location'), {target:{value:'all'}});
  fireEvent.click(screen.getByRole('checkbox'));
  expect(screen.getByText('Auburn award')).toBeVisible();
  expect(screen.getByText('3 matches · 1 to explore')).toBeVisible();
});
