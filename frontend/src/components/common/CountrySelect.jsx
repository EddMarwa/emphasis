import React, { useState, useRef, useEffect } from 'react';
import { ChevronDown } from 'lucide-react';
import { countries, getCountryByCode } from '../../data/countries';

const CountrySelect = ({
  value,
  onChange,
  className = '',
  label,
  required = false,
  error,
}) => {
  const [isOpen, setIsOpen] = useState(false);
  const dropdownRef = useRef(null);
  
  const selectedCountry = getCountryByCode(value || 'KE');
  
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target)) {
        setIsOpen(false);
      }
    };
    
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);
  
  const handleSelect = (country) => {
    onChange(country.code);
    setIsOpen(false);
  };
  
  return (
    <div className={`w-full ${className}`}>
      {label && (
        <label className="block text-sm font-semibold text-gray-700 mb-2">
          {label}
          {required && <span className="text-red-500 ml-1">*</span>}
        </label>
      )}
      
      <div className="relative" ref={dropdownRef}>
        <button
          type="button"
          onClick={() => setIsOpen(!isOpen)}
          className={`
            w-full px-4 py-3 border rounded-xl
            focus:ring-2 focus:ring-cyan-400 focus:border-transparent
            transition-all duration-300
            ${error ? 'border-red-500 focus:ring-red-400' : 'border-gray-300'}
            bg-white text-text-dark
            flex items-center justify-between
            hover:border-electric-cyan
          `}
        >
          <div className="flex items-center gap-3">
            <span className="text-2xl">{selectedCountry.flag}</span>
            <span className="font-medium">{selectedCountry.name}</span>
            <span className="text-text-gray text-sm">({selectedCountry.phoneCode})</span>
          </div>
          <ChevronDown 
            size={20} 
            className={`text-text-gray transition-transform duration-200 ${isOpen ? 'transform rotate-180' : ''}`}
          />
        </button>
        
        {isOpen && (
          <div className="absolute z-50 w-full mt-2 bg-white border border-gray-200 rounded-xl shadow-quantum-lg max-h-64 overflow-y-auto animate-slide-up">
            {countries.map((country) => (
              <button
                key={country.code}
                type="button"
                onClick={() => handleSelect(country)}
                className={`
                  w-full px-4 py-3 flex items-center gap-3 hover:bg-gray-50 transition-colors
                  ${value === country.code ? 'bg-gradient-card-hover' : ''}
                `}
              >
                <span className="text-2xl">{country.flag}</span>
                <div className="flex-1 text-left">
                  <div className="font-medium text-text-dark">{country.name}</div>
                  <div className="text-sm text-text-gray">{country.phoneCode}</div>
                </div>
                {value === country.code && (
                  <div className="w-2 h-2 bg-electric-cyan rounded-full"></div>
                )}
              </button>
            ))}
          </div>
        )}
      </div>
      
      {error && (
        <p className="text-sm text-red-600 mt-1">{error}</p>
      )}
    </div>
  );
};

export default CountrySelect;

