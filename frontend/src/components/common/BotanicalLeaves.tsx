import React from 'react';

export const BotanicalLeaves: React.FC<{ className?: string }> = ({ className = '' }) => {
  return (
    <svg
      viewBox="0 0 340 220"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
      className={className}
      aria-hidden="true"
    >
      <defs>
        {/* Emerald / Dark Teal Leaf Gradient */}
        <linearGradient id="emeraldLeafGrad" x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%" stopColor="#2E6B56" />
          <stop offset="45%" stopColor="#1E4D3E" />
          <stop offset="100%" stopColor="#0E2E25" />
        </linearGradient>

        {/* Violet / Orchid Main Petal Gradient */}
        <linearGradient id="orchidPetalGrad" x1="0%" y1="100%" x2="100%" y2="0%">
          <stop offset="0%" stopColor="#4F46E5" />
          <stop offset="50%" stopColor="#7C3AED" />
          <stop offset="100%" stopColor="#A78BFA" />
        </linearGradient>

        {/* Soft Lavender Translucent Petal Gradient */}
        <linearGradient id="lavenderPetalGrad" x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%" stopColor="#C4B5FD" stopOpacity="0.85" />
          <stop offset="60%" stopColor="#DDD6FE" stopOpacity="0.7" />
          <stop offset="100%" stopColor="#EDE9FE" stopOpacity="0.4" />
        </linearGradient>

        {/* Sage Green Leaf Gradient */}
        <linearGradient id="sageLeafGrad" x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%" stopColor="#86EFAC" />
          <stop offset="50%" stopColor="#4ADE80" />
          <stop offset="100%" stopColor="#22C55E" />
        </linearGradient>

        {/* Soft Shadow Filter */}
        <filter id="leafShadow" x="-20%" y="-20%" width="140%" height="140%">
          <feDropShadow dx="2" dy="8" stdDeviation="10" floodColor="#312E81" floodOpacity="0.12" />
        </filter>
      </defs>

      <g filter="url(#leafShadow)">
        {/* Background Soft Lilac Leaf Shape */}
        <path
          d="M170 140 C140 100, 180 30, 240 15 C280 4, 305 40, 290 85 C275 130, 210 170, 170 140 Z"
          fill="url(#lavenderPetalGrad)"
        />

        {/* Sage / Lime Accent Leaf */}
        <path
          d="M210 160 C230 130, 275 110, 310 115 C330 118, 335 140, 315 160 C290 185, 235 185, 210 160 Z"
          fill="url(#sageLeafGrad)"
          opacity="0.9"
        />

        {/* Main Dark Emerald Tropical Leaf */}
        <path
          d="M150 165 C130 110, 155 40, 220 20 C245 45, 250 85, 235 125 C215 175, 170 195, 150 165 Z"
          fill="url(#emeraldLeafGrad)"
        />
        {/* Vein on Emerald Leaf */}
        <path
          d="M150 165 Q195 105 220 20"
          stroke="#52B788"
          strokeWidth="2"
          strokeLinecap="round"
          opacity="0.6"
        />

        {/* Large Vibrant Violet / Orchid Petal Curving Left */}
        <path
          d="M140 170 C95 140, 85 85, 110 40 C125 15, 150 25, 145 60 C140 105, 180 140, 140 170 Z"
          fill="url(#orchidPetalGrad)"
        />
        {/* Highlight Curve on Violet Petal */}
        <path
          d="M140 170 Q115 110 110 40"
          stroke="#DDD6FE"
          strokeWidth="2"
          strokeLinecap="round"
          opacity="0.75"
        />

        {/* Small Graceful Foreground Orchid Petal */}
        <path
          d="M165 175 C145 155, 145 125, 160 100 C175 75, 195 80, 195 105 C195 130, 185 160, 165 175 Z"
          fill="url(#orchidPetalGrad)"
          opacity="0.85"
        />
      </g>
    </svg>
  );
};

export const GlowingWavesGraphic: React.FC<{ className?: string }> = ({ className = '' }) => {
  return (
    <svg
      viewBox="0 0 200 100"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
      className={className}
      preserveAspectRatio="none"
      aria-hidden="true"
    >
      <defs>
        <linearGradient id="waveGrad1" x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%" stopColor="#6366F1" stopOpacity="0.8" />
          <stop offset="50%" stopColor="#38BDF8" stopOpacity="0.6" />
          <stop offset="100%" stopColor="#818CF8" stopOpacity="0" />
        </linearGradient>
        <linearGradient id="waveGrad2" x1="100%" y1="0%" x2="0%" y2="100%">
          <stop offset="0%" stopColor="#8B5CF6" stopOpacity="0.7" />
          <stop offset="60%" stopColor="#06B6D4" stopOpacity="0.5" />
          <stop offset="100%" stopColor="#3B82F6" stopOpacity="0" />
        </linearGradient>
      </defs>

      <path
        d="M-20 80 C30 50, 70 95, 120 60 C160 30, 190 60, 230 40 L230 120 L-20 120 Z"
        fill="url(#waveGrad1)"
      />
      <path
        d="M-10 60 C40 30, 80 80, 130 45 C170 15, 200 45, 240 25 L240 120 L-10 120 Z"
        fill="url(#waveGrad2)"
        opacity="0.8"
      />
    </svg>
  );
};

export const SparklineWave: React.FC<{ color?: 'purple' | 'blue' | 'green' | 'rose'; className?: string }> = ({
  color = 'purple',
  className = 'w-16 h-8'
}) => {
  const strokeColor = {
    purple: '#8B5CF6',
    blue: '#38BDF8',
    green: '#10B981',
    rose: '#F43F5E',
  }[color];

  const paths = {
    purple: "M 2 20 Q 15 22, 28 14 T 54 6",
    blue: "M 2 18 Q 14 10, 28 16 T 54 8",
    green: "M 2 22 Q 16 22, 28 12 T 54 10",
    rose: "M 2 20 Q 14 12, 28 18 T 54 12",
  }[color];

  return (
    <svg viewBox="0 0 56 26" fill="none" xmlns="http://www.w3.org/2000/svg" className={className} aria-hidden="true">
      <path
        d={paths}
        stroke={strokeColor}
        strokeWidth="2"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
    </svg>
  );
};
