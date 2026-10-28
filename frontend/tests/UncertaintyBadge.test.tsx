import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import React from 'react';
import { UncertaintyBadge } from '../src/components/common/UncertaintyBadge';

describe('UncertaintyBadge', () => {
  it('renders "Owner Unknown" for not_stated owner', () => {
    render(<UncertaintyBadge type="owner" status="not_stated" />);
    expect(screen.getByText('Owner Unknown')).toBeInTheDocument();
  });

  it('renders "No Deadline" for not_stated deadline', () => {
    render(<UncertaintyBadge type="due_date" status="not_stated" />);
    expect(screen.getByText('No Deadline')).toBeInTheDocument();
  });

  it('renders "Confirmed" for user_confirmed status', () => {
    render(<UncertaintyBadge type="owner" status="user_confirmed" />);
    expect(screen.getByText('Confirmed')).toBeInTheDocument();
  });

  it('renders "Ambiguous" for ambiguous status', () => {
    render(<UncertaintyBadge type="owner" status="ambiguous" />);
    expect(screen.getByText('Ambiguous')).toBeInTheDocument();
  });

  it('renders "Resolved" for resolved_from_meeting_date status', () => {
    render(<UncertaintyBadge type="due_date" status="resolved_from_meeting_date" dateExpression="next Friday" />);
    expect(screen.getByText('Resolved')).toBeInTheDocument();
  });
});

