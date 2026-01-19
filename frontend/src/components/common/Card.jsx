import React from 'react';

const Card = ({
  children,
  hover = false,
  gradient = false,
  className = '',
  onClick,
  ...props
}) => {
  const baseStyles = 'bg-white rounded-xl shadow-quantum transition-all duration-300';
  
  const hoverStyles = hover ? 'hover:shadow-quantum-lg hover:scale-[1.02] cursor-pointer' : '';
  const gradientStyles = gradient ? 'bg-gradient-card-hover' : '';
  const clickable = onClick ? 'cursor-pointer' : '';
  
  const cardClasses = `${baseStyles} ${hoverStyles} ${gradientStyles} ${clickable} ${className}`.trim().replace(/\s+/g, ' ');
  
  return (
    <div
      className={cardClasses}
      onClick={onClick}
      {...props}
    >
      {children}
    </div>
  );
};

export default Card;

