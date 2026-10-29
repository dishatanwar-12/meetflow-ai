import React from 'react';

export const MeetingFlowLogo: React.FC<{ className?: string }> = ({ className = 'w-9 h-9' }) => {
  return (
    <svg
      viewBox="0 0 40 40"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
      className={className}
      aria-hidden="true"
    >
      <defs>
        <linearGradient id="mfRibbon1" x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%" stopColor="#4F46E5" />
          <stop offset="60%" stopColor="#7C3AED" />
          <stop offset="100%" stopColor="#9333EA" />
        </linearGradient>
        <linearGradient id="mfRibbon2" x1="0%" y1="100%" x2="100%" y2="0%">
          <stop offset="0%" stopColor="#6366F1" />
          <stop offset="50%" stopColor="#38BDF8" />
          <stop offset="100%" stopColor="#67E8F9" />
        </linearGradient>
        <linearGradient id="mfRibbon3" x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%" stopColor="#A855F7" />
          <stop offset="100%" stopColor="#3B82F6" />
        </linearGradient>
      </defs>

      {/* Left loop of the M */}
      <path
        d="M8 28 C6 22, 7 13, 14 13 C18 13, 21 18, 23 23 L25 27 C27 22, 29 15, 33 15 C37 15, 38 21, 35 27 C33 30, 28 32, 24 28 L22 24 C19 19, 16 16, 13 17 C10 18, 9 24, 11 27 Z"
        fill="url(#mfRibbon1)"
      />

      {/* Foreground folded twist loop */}
      <path
        d="M6 25 C5 18, 9 12, 15 12 C19 12, 23 17, 26 23 C28 27, 31 30, 35 28 C38 26, 38 20, 36 17 C34 14, 30 14, 28 17 C26 20, 23 24, 21 24 C17 24, 13 16, 8 18 C5 19, 4 23, 6 25 Z"
        fill="url(#mfRibbon2)"
        opacity="0.95"
      />
    </svg>
  );
};

