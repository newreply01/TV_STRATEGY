import React from 'react';
import { clsx, type ClassValue } from 'clsx';
import { twMerge } from 'tailwind-merge';

function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

interface ContainerProps {
  children: React.ReactNode;
  className?: string;
  size?: 'sm' | 'md' | 'lg' | 'xl' | 'full';
  as?: React.ElementType;
}

const sizeClasses = {
  sm: 'max-w-4xl',    // 896px
  md: 'max-w-5xl',    // 1024px
  lg: 'max-w-6xl',    // 1152px
  xl: 'max-w-7xl',    // 1280px (Standard)
  full: 'max-w-none',
};

export default function Container({ 
  children, 
  className, 
  size = 'xl',
  as: Component = 'div' 
}: ContainerProps) {
  return (
    <Component className={cn('mx-auto px-6 w-full', sizeClasses[size], className)}>
      {children}
    </Component>
  );
}
