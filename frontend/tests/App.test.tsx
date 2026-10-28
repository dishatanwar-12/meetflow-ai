import { describe, it, expect, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import React from 'react';
import App from '../src/App';

describe('App Route Navigation', () => {
  it('renders login screen when unauthenticated', async () => {
    localStorage.clear();
    render(<App />);
    expect(await screen.findByText(/Sign in to MeetFlow AI/i)).toBeInTheDocument();
  });
});

