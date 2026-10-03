                                           
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  darkMode: false,
  theme: {
    extend: {
      colors: {
        dark: {
          950: '#07070a',                         
          900: '#0c0d12',                   
          850: '#11131a',                    
          800: '#171924',                
          750: '#1e2130',                          
          700: '#272b3e',                 
          600: '#383d57',                 
        },
        rose: {
          50: '#fff1f2',
          100: '#ffe4e6',
          200: '#fecdd3',
          300: '#fda4af',
          400: '#fb7185',
          500: '#f43f5e',                
          600: '#e11d48',                  
          700: '#be123c',            
          800: '#9f1239',             
          900: '#881337',             
          950: '#4c0519',                   
        },
        crimson: {
          base: '#e11d48',
          glow: 'rgba(225, 29, 72, 0.25)',
          muted: 'rgba(225, 29, 72, 0.12)',
        },
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', '-apple-system', 'BlinkMacSystemFont', 'Segoe UI', 'Roboto', 'sans-serif'],
        mono: ['JetBrains Mono', 'Fira Code', 'Menlo', 'Monaco', 'Courier New', 'monospace'],
      },
      boxShadow: {
        'glow-rose': '0 0 30px -5px rgba(244, 63, 94, 0.25)',
        'glow-crimson': '0 0 35px -5px rgba(225, 29, 72, 0.3)',
        'glow-wine': '0 0 40px -10px rgba(136, 19, 55, 0.35)',
        'card-dark': '0 12px 35px -10px rgba(0, 0, 0, 0.65)',
        'float-rose': '0 10px 30px -5px rgba(244, 63, 94, 0.2)',
      },
      animation: {
        'pulse-subtle': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'fade-in': 'fadeIn 0.35s ease-out forwards',
        'slide-up': 'slideUp 0.4s cubic-bezier(0.16, 1, 0.3, 1) forwards',
        'shimmer': 'shimmer 2.2s infinite linear',
      },
      keyframes: {
        fadeIn: {
          '0%': { opacity: '0', transform: 'translateY(8px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
        slideUp: {
          '0%': { opacity: '0', transform: 'translateY(16px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
        shimmer: {
          '0%': { backgroundPosition: '-200% 0' },
          '100%': { backgroundPosition: '200% 0' },
        },
      },
    },
  },
  plugins: [],
}

