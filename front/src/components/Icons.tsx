// pack d'icônes SVG repris du design Claude — on les a en inline pour éviter une lib externe
export const Icon = {
  Search: () => (
    <svg width="14" height="14" viewBox="0 0 14 14" fill="none">
      <circle cx="6" cy="6" r="4.2" stroke="currentColor" strokeWidth="1.5" />
      <path d="M9.5 9.5l3 3" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" />
    </svg>
  ),
  Chart: () => (
    <svg width="14" height="14" viewBox="0 0 14 14" fill="none">
      <rect x="1" y="8" width="2.5" height="5" rx=".8" fill="currentColor" />
      <rect x="5.5" y="4.5" width="2.5" height="8.5" rx=".8" fill="currentColor" />
      <rect x="10" y="1" width="2.5" height="12" rx=".8" fill="currentColor" />
    </svg>
  ),
  Cal: () => (
    <svg width="14" height="14" viewBox="0 0 14 14" fill="none">
      <rect x="1" y="2.5" width="12" height="10.5" rx="1.8" stroke="currentColor" strokeWidth="1.4" />
      <path d="M1 6h12M5 1v3M9 1v3" stroke="currentColor" strokeWidth="1.4" strokeLinecap="round" />
    </svg>
  ),
  Info: () => (
    <svg width="14" height="14" viewBox="0 0 14 14" fill="none">
      <circle cx="7" cy="7" r="5.8" stroke="currentColor" strokeWidth="1.4" />
      <path d="M7 6.5v3.5M7 4.2v.3" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" />
    </svg>
  ),
  Compare: () => (
    <svg width="14" height="14" viewBox="0 0 14 14" fill="none">
      <rect x="1" y="1" width="5" height="12" rx="1.5" stroke="currentColor" strokeWidth="1.4" />
      <rect x="8" y="1" width="5" height="12" rx="1.5" stroke="currentColor" strokeWidth="1.4" />
    </svg>
  ),
  ChevDown: ({ open }: { open: boolean }) => (
    <svg width="13" height="13" viewBox="0 0 13 13" fill="none">
      <path d={open ? 'M2.5 8.5l4-4 4 4' : 'M2.5 4.5l4 4 4-4'}
        stroke="#9a9a94" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" />
    </svg>
  ),
  Pin: () => (
    <svg width="13" height="13" viewBox="0 0 13 13" fill="none">
      <path d="M6.5 1l1.5 3.5 3.5.5-2.5 2.5.5 3.5L6.5 9.5l-3 1.5.5-3.5L1.5 5l3.5-.5z"
        stroke="currentColor" strokeWidth="1.3" strokeLinejoin="round" />
    </svg>
  ),
  X: () => (
    <svg width="11" height="11" viewBox="0 0 11 11" fill="none">
      <path d="M2 2l7 7M9 2l-7 7" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" />
    </svg>
  ),
  Globe: () => (
    <svg width="17" height="17" viewBox="0 0 17 17" fill="none">
      <circle cx="8.5" cy="8.5" r="6.5" stroke="white" strokeWidth="1.4" />
      <path d="M2 8.5h13" stroke="white" strokeWidth="1.2" />
      <path d="M8.5 2c-2.5 2-2.5 4.5 0 6.5s0 4.5 0 4.5" stroke="white" strokeWidth="1.2" strokeLinecap="round" />
      <path d="M8.5 2c2.5 2 2.5 4.5 0 6.5s0 4.5 0 4.5" stroke="white" strokeWidth="1.2" strokeLinecap="round" />
    </svg>
  ),
};
