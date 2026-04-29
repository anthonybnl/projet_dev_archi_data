import { useState, type ReactNode } from 'react';
import { C } from '../lib/theme';
import { Icon } from './Icons';

// wrapper de section pliable (chevron à droite)
// utilisé pour Recherche, Indicateurs, Chronologie, Détails, Comparaison
export function Section({
  title,
  icon,
  defaultOpen = true,
  children,
  noPad = false,
}: {
  title: string;
  icon: ReactNode;
  defaultOpen?: boolean;
  children: ReactNode;
  noPad?: boolean;
}) {
  const [open, setOpen] = useState(defaultOpen);
  return (
    <div style={{ borderBottom: `1px solid ${C.border}` }}>
      <button onClick={() => setOpen(o => !o)} style={{
        width: '100%', display: 'flex', alignItems: 'center', justifyContent: 'space-between',
        padding: '11px 16px', background: 'none', border: 'none', cursor: 'pointer', textAlign: 'left',
        fontFamily: 'inherit',
      }}>
        <span style={{ display: 'flex', alignItems: 'center', gap: '9px' }}>
          <span style={{ color: C.accent, display: 'flex', alignItems: 'center' }}>{icon}</span>
          <span style={{ fontWeight: 600, fontSize: '12.5px', color: C.text, letterSpacing: '0.01em' }}>{title}</span>
        </span>
        <Icon.ChevDown open={open} />
      </button>
      {open && <div style={noPad ? {} : { padding: '0 16px 14px' }}>{children}</div>}
    </div>
  );
}
