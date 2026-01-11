import React from 'react';

const Input = ({
  type = 'text',
  label,
  error,
  success,
  placeholder,
  value,
  onChange,
  disabled = false,
  className = '',
  required = false,
  ...props
}) => {
  const inputClasses = `
    w-full px-4 py-3 border rounded-xl text-text-dark placeholder:text-gray-400
    focus:ring-2 focus:ring-cyan-400 focus:border-transparent
    transition-all duration-300
    ${error ? 'border-red-500 focus:ring-red-400' : ''}
    ${success ? 'border-emerald-500 focus:ring-emerald-400' : ''}
    ${!error && !success ? 'border-gray-300' : ''}
    ${disabled ? 'bg-gray-100 cursor-not-allowed text-gray-500' : 'bg-white'}
    ${className}
  `.trim().replace(/\s+/g, ' ');

  return (
    <div className="w-full">
      {label && (
        <label className="block text-sm font-semibold text-gray-700 mb-2">
          {label}
          {required && <span className="text-red-500 ml-1">*</span>}
        </label>
      )}
      <input
        type={type}
        className={inputClasses}
        placeholder={placeholder}
        value={value}
        onChange={onChange}
        disabled={disabled}
        required={required}
        {...props}
      />
      {error && (
        <p className="text-sm text-red-600 mt-1">{error}</p>
      )}
      {success && !error && (
        <p className="text-sm text-emerald-600 mt-1">{success}</p>
      )}
    </div>
  );
};

export default Input;

