/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./src/**/*.{js,jsx,ts,tsx}"],
  theme: {
    extend: {
      colors: {
        'navy-blue': '#0A1628',
        'electric-blue': '#1E40AF',
        'electric-cyan': '#00D9FF',
        'emerald': '#10B981',
        'teal': '#14B8A6',
        'light-gray': '#F8FAFC',
        'border-gray': '#E5E7EB',
        'text-gray': '#6B7280',
        'text-dark': '#111827',
      },
      backgroundImage: {
        'gradient-primary': 'linear-gradient(135deg, #0A1628 0%, #1E40AF 50%, #00D9FF 100%)',
        'gradient-success': 'linear-gradient(135deg, #059669 0%, #14B8A6 100%)',
        'gradient-header': 'linear-gradient(to right, #1E3A8A, #1E40AF, #0E7490)',
        'gradient-page': 'linear-gradient(to bottom right, #F8FAFC, #DBEAFE)',
        'gradient-button-primary': 'linear-gradient(to right, #1E40AF, #00D9FF)',
        'gradient-button-success': 'linear-gradient(to right, #059669, #14B8A6)',
        'gradient-button-danger': 'linear-gradient(to right, #DC2626, #F43F5E)',
        'gradient-card-hover': 'linear-gradient(to bottom right, #EFF6FF, #DBEAFE)',
      },
      boxShadow: {
        'quantum': '0 10px 40px rgba(30, 64, 175, 0.1)',
        'quantum-lg': '0 20px 60px rgba(30, 64, 175, 0.15)',
        'cyan-glow': '0 0 30px rgba(0, 217, 255, 0.3)',
      },
      animation: {
        'fade-in': 'fadeIn 0.5s ease-in-out',
        'slide-up': 'slideUp 0.4s ease-out',
        'glow': 'glow 2s ease-in-out infinite',
        'slide-in-right': 'slideInRight 0.3s ease-out',
        'scale-in': 'scaleIn 0.3s ease-out',
      },
      keyframes: {
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        slideUp: {
          '0%': { transform: 'translateY(20px)', opacity: '0' },
          '100%': { transform: 'translateY(0)', opacity: '1' },
        },
        glow: {
          '0%, 100%': { boxShadow: '0 0 20px rgba(0, 217, 255, 0.3)' },
          '50%': { boxShadow: '0 0 40px rgba(0, 217, 255, 0.6)' },
        },
        slideInRight: {
          '0%': { transform: 'translateX(100%)', opacity: '0' },
          '100%': { transform: 'translateX(0)', opacity: '1' },
        },
        scaleIn: {
          '0%': { transform: 'scale(0.95)', opacity: '0' },
          '100%': { transform: 'scale(1)', opacity: '1' },
        },
      },
    },
  },
  plugins: [],
}

