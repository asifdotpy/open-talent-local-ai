import React from 'react';
import { colors, radius, spacing } from './tokens';

type Variant = 'primary' | 'secondary';

type ButtonProps = React.ButtonHTMLAttributes<HTMLButtonElement> & {
  variant?: Variant;
};

export const Button: React.FC<ButtonProps> = ({ variant = 'primary', style, ...rest }) => {
  const base: React.CSSProperties = {
    padding: `${spacing.sm}px ${spacing.lg}px`,
    border: 'none',
    borderRadius: radius.sm,
    cursor: 'pointer',
    fontSize: 15,
    fontWeight: 600,
    letterSpacing: 0.5,
    textTransform: 'uppercase',
    transition: 'all 0.2s ease',
  };

  const primary: React.CSSProperties = {
    background: `linear-gradient(135deg, ${colors.primary} 0%, ${colors.primaryAlt} 100%)`,
    color: '#fff'
  };

  const secondary: React.CSSProperties = {
    background: '#f0f0f0',
    color: colors.text
  };

  const hover: React.CSSProperties = {
    transform: 'translateY(-1px)'
  };

  const variantStyle = variant === 'primary' ? primary : secondary;

  return (
    <button
      style={{ ...base, ...variantStyle, ...style }}
      onMouseEnter={e => (e.currentTarget.style.transform = hover.transform || '')}
      onMouseLeave={e => (e.currentTarget.style.transform = '')}
      {...rest}
    />
  );
};
