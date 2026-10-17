export function BrandMark() {
  return (
    <svg
      className="brand-mark"
      viewBox="0 0 40 40"
      fill="none"
      aria-hidden="true"
      focusable="false"
    >
      <rect width="40" height="40" rx="12" fill="#3454F5" />
      <path
        d="M9 27h8v-7h7v-7h7"
        stroke="white"
        strokeWidth="3.5"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
      <path
        d="m26 13 5 0-2.7 4.4"
        stroke="#FFD65A"
        strokeWidth="2.8"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
    </svg>
  );
}

export function RouteIllustration() {
  return (
    <svg viewBox="0 0 420 310" fill="none" focusable="false">
      <defs>
        <linearGradient id="route-sky" x1="20" y1="8" x2="390" y2="300">
          <stop stopColor="#DDE5FF" />
          <stop offset="1" stopColor="#EDFDF9" />
        </linearGradient>
        <filter id="route-shadow" x="0" y="0" width="420" height="310">
          <feDropShadow dx="0" dy="10" stdDeviation="12" floodColor="#1C2C69" floodOpacity=".12" />
        </filter>
      </defs>
      <rect x="10" y="12" width="400" height="286" rx="36" fill="url(#route-sky)" />
      <circle cx="357" cy="54" r="23" fill="#FFD65A" />
      <path d="m357 39 3.7 11.3L372 54l-11.3 3.7L357 69l-3.7-11.3L342 54l11.3-3.7L357 39Z" fill="#172244" />
      <path d="M53 238c77 12 83-65 155-56 70 9 69-86 146-94" stroke="#3454F5" strokeWidth="7" strokeLinecap="round" strokeDasharray="2 17" />
      <circle cx="62" cy="236" r="19" fill="#3454F5" />
      <circle cx="62" cy="236" r="7" fill="white" />
      <g filter="url(#route-shadow)">
        <rect x="78" y="45" width="185" height="108" rx="18" fill="white" />
        <rect x="98" y="68" width="52" height="52" rx="15" fill="#E9E4FF" />
        <path d="M111 106V93l13-9 13 9v13h-26Z" stroke="#7546E8" strokeWidth="3" strokeLinejoin="round" />
        <path d="M119 107V96h10v11" stroke="#7546E8" strokeWidth="3" strokeLinejoin="round" />
        <rect x="166" y="75" width="72" height="9" rx="4.5" fill="#172244" />
        <rect x="166" y="94" width="58" height="7" rx="3.5" fill="#B6C3EA" />
        <rect x="166" y="109" width="42" height="7" rx="3.5" fill="#D9E1F7" />
      </g>
      <g filter="url(#route-shadow)">
        <rect x="218" y="173" width="150" height="89" rx="17" fill="white" />
        <circle cx="249" cy="204" r="16" fill="#C9F5F0" />
        <path d="m241 204 6 6 11-13" stroke="#117C70" strokeWidth="3.5" strokeLinecap="round" strokeLinejoin="round" />
        <rect x="274" y="194" width="70" height="8" rx="4" fill="#172244" />
        <rect x="274" y="212" width="53" height="7" rx="3.5" fill="#B6C3EA" />
        <rect x="238" y="236" width="94" height="7" rx="3.5" fill="#D9E1F7" />
      </g>
      <path d="m321 119 3 8 8 3-8 3-3 8-3-8-8-3 8-3 3-8Z" fill="#7546E8" />
      <path d="m97 176 2 6 6 2-6 2-2 6-2-6-6-2 6-2 2-6Z" fill="#F0A832" />
    </svg>
  );
}
