import React from 'react';
import { TrendingUp, TrendingDown } from 'lucide-react';
import Card from '../common/Card';

const StatCard = ({
  title,
  value,
  change,
  changeType = 'positive',
  icon: Icon,
  iconColor = 'bg-gradient-button-primary',
  className = '',
}) => {
  return (
    <Card hover className={`p-6 ${className}`}>
      <div className="flex items-start justify-between">
        <div className="flex-1">
          <p className="text-sm font-medium text-text-gray mb-1">{title}</p>
          <p className="text-3xl font-bold text-text-dark mb-2">{value}</p>
          <div className="flex items-center gap-1">
            {changeType === 'positive' ? (
              <TrendingUp size={16} className="text-emerald-500" />
            ) : changeType === 'negative' ? (
              <TrendingDown size={16} className="text-red-500" />
            ) : null}
            <span className={`text-sm font-medium ${
              changeType === 'positive' ? 'text-emerald-600' : 
              changeType === 'negative' ? 'text-red-600' : 
              'text-text-gray'
            }`}>
              {change}
            </span>
          </div>
        </div>
        <div className={`${iconColor} w-12 h-12 rounded-xl flex items-center justify-center shadow-lg`}>
          {Icon && <Icon size={24} className="text-white" />}
        </div>
      </div>
    </Card>
  );
};

export default StatCard;

