export function FloatLogo({ className = "" }: { className?: string }) {
  return (
    <svg 
      viewBox="0 0 120 40" 
      className={className}
      fill="none" 
      xmlns="http://www.w3.org/2000/svg"
    >
      {/* Floating element icon */}
      <path 
        d="M8 20C8 16 10 12 14 10C18 8 22 10 24 14C26 18 24 22 20 24C16 26 12 24 10 20" 
        fill="currentColor"
        opacity="0.3"
      />
      <path 
        d="M12 16C12 14 13 12 15 11C17 10 19 11 20 13C21 15 20 17 18 18C16 19 14 18 13 16" 
        fill="currentColor"
      />
      
      {/* FLOAT text */}
      <text 
        x="32" 
        y="28" 
        style={{ 
          fontSize: '24px', 
          fontWeight: '700',
          letterSpacing: '0.05em'
        }}
        fill="currentColor"
      >
        FLOWN
      </text>
    </svg>
  );
}
