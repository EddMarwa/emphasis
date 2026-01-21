// Country data with flags (using flag emojis)
export const countries = [
  { code: 'KE', name: 'Kenya', flag: '🇰🇪', phoneCode: '+254', phonePattern: /^\+254\s\d{3}\s\d{3}\s\d{3}$/ },
  { code: 'US', name: 'United States', flag: '🇺🇸', phoneCode: '+1', phonePattern: /^\+1\s\d{3}\s\d{3}\s\d{4}$/ },
  { code: 'UK', name: 'United Kingdom', flag: '🇬🇧', phoneCode: '+44', phonePattern: /^\+44\s\d{4}\s\d{6}$/ },
  { code: 'NG', name: 'Nigeria', flag: '🇳🇬', phoneCode: '+234', phonePattern: /^\+234\s\d{3}\s\d{3}\s\d{4}$/ },
  { code: 'ZA', name: 'South Africa', flag: '🇿🇦', phoneCode: '+27', phonePattern: /^\+27\s\d{2}\s\d{3}\s\d{4}$/ },
  { code: 'GH', name: 'Ghana', flag: '🇬🇭', phoneCode: '+233', phonePattern: /^\+233\s\d{3}\s\d{3}\s\d{3}$/ },
  { code: 'TZ', name: 'Tanzania', flag: '🇹🇿', phoneCode: '+255', phonePattern: /^\+255\s\d{3}\s\d{3}\s\d{3}$/ },
  { code: 'UG', name: 'Uganda', flag: '🇺🇬', phoneCode: '+256', phonePattern: /^\+256\s\d{3}\s\d{3}\s\d{3}$/ },
  { code: 'ET', name: 'Ethiopia', flag: '🇪🇹', phoneCode: '+251', phonePattern: /^\+251\s\d{2}\s\d{3}\s\d{4}$/ },
  { code: 'RW', name: 'Rwanda', flag: '🇷🇼', phoneCode: '+250', phonePattern: /^\+250\s\d{3}\s\d{3}\s\d{3}$/ },
  { code: 'ZW', name: 'Zimbabwe', flag: '🇿🇼', phoneCode: '+263', phonePattern: /^\+263\s\d{2}\s\d{3}\s\d{4}$/ },
  { code: 'ZM', name: 'Zambia', flag: '🇿🇲', phoneCode: '+260', phonePattern: /^\+260\s\d{2}\s\d{3}\s\d{4}$/ },
  { code: 'MW', name: 'Malawi', flag: '🇲🇼', phoneCode: '+265', phonePattern: /^\+265\s\d{1}\s\d{3}\s\d{3}\s\d{3}$/ },
  { code: 'CM', name: 'Cameroon', flag: '🇨🇲', phoneCode: '+237', phonePattern: /^\+237\s\d{3}\s\d{2}\s\d{2}\s\d{2}$/ },
  { code: 'CI', name: 'Ivory Coast', flag: '🇨🇮', phoneCode: '+225', phonePattern: /^\+225\s\d{2}\s\d{2}\s\d{2}\s\d{2}$/ },
  { code: 'SN', name: 'Senegal', flag: '🇸🇳', phoneCode: '+221', phonePattern: /^\+221\s\d{2}\s\d{3}\s\d{2}\s\d{2}$/ },
  { code: 'AO', name: 'Angola', flag: '🇦🇴', phoneCode: '+244', phonePattern: /^\+244\s\d{3}\s\d{3}\s\d{3}$/ },
  { code: 'MU', name: 'Mauritius', flag: '🇲🇺', phoneCode: '+230', phonePattern: /^\+230\s\d{4}\s\d{4}$/ },
  { code: 'BW', name: 'Botswana', flag: '🇧🇼', phoneCode: '+267', phonePattern: /^\+267\s\d{2}\s\d{3}\s\d{3}$/ },
  { code: 'NA', name: 'Namibia', flag: '🇳🇦', phoneCode: '+264', phonePattern: /^\+264\s\d{2}\s\d{3}\s\d{4}$/ },
];

// Get country by code
export const getCountryByCode = (code) => {
  return countries.find(c => c.code === code) || countries[0]; // Default to Kenya
};

// Format phone number based on country
export const formatPhoneNumber = (value, countryCode) => {
  const country = getCountryByCode(countryCode);
  const numbers = value.replace(/\D/g, '');
  
  // Remove country code if present
  const phoneCode = country.phoneCode.replace('+', '');
  let cleaned = numbers;
  if (cleaned.startsWith(phoneCode)) {
    cleaned = cleaned.slice(phoneCode.length);
  } else if (cleaned.startsWith('0') && countryCode === 'KE') {
    cleaned = cleaned.slice(1); // Remove leading 0 for Kenya
  }
  
  // Format based on country
  switch (countryCode) {
    case 'KE':
      if (cleaned.length <= 3) return `${country.phoneCode} ${cleaned}`;
      if (cleaned.length <= 6) return `${country.phoneCode} ${cleaned.slice(0, 3)} ${cleaned.slice(3)}`;
      return `${country.phoneCode} ${cleaned.slice(0, 3)} ${cleaned.slice(3, 6)} ${cleaned.slice(6, 9)}`;
    
    case 'US':
      if (cleaned.length <= 3) return `${country.phoneCode} ${cleaned}`;
      if (cleaned.length <= 6) return `${country.phoneCode} ${cleaned.slice(0, 3)} ${cleaned.slice(3)}`;
      return `${country.phoneCode} ${cleaned.slice(0, 3)} ${cleaned.slice(3, 6)} ${cleaned.slice(6, 10)}`;
    
    case 'UK':
      if (cleaned.length <= 4) return `${country.phoneCode} ${cleaned}`;
      return `${country.phoneCode} ${cleaned.slice(0, 4)} ${cleaned.slice(4, 10)}`;
    
    default:
      // Generic formatting
      if (cleaned.length <= 3) return `${country.phoneCode} ${cleaned}`;
      if (cleaned.length <= 6) return `${country.phoneCode} ${cleaned.slice(0, 3)} ${cleaned.slice(3)}`;
      return `${country.phoneCode} ${cleaned.slice(0, 3)} ${cleaned.slice(3, 6)} ${cleaned.slice(6)}`;
  }
};

