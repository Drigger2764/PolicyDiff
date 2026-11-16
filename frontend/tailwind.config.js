/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        deontic: {
          must: '#ef4444',     // Red for strict obligation
          mustnot: '#dc2626',  // Dark red for prohibition
          should: '#f59e0b',   // Amber for recommendation
          may: '#10b981',      // Emerald for permission
          cannot: '#6b7280',   // Gray for incapacity
        }
      }
    },
  },
  plugins: [],
}
