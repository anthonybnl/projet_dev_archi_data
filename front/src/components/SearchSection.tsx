import { useState } from 'react';
import { C } from '../lib/theme';
import { Icon } from './Icons';
import { Section } from './Section';
import type { ZoneData } from '../lib/types';

// barre de recherche : on filtre la liste des zones courantes (arrondissement ou IRIS)
// par nom, code ou numéro d'arrondissement
export function SearchSection({
  zones,
  onSelect,
}: {
  zones: ZoneData[];
  onSelect: (z: ZoneData) => void;
}) {
  const [q, setQ] = useState('');

  const results = q.length > 1
    ? zones.filter(z =>
        z.name.toLowerCase().includes(q.toLowerCase()) ||
        z.code.includes(q) ||
        String(z.arrondissement).startsWith(q)
      ).slice(0, 6)
    : [];

  return (
    <Section title="Recherche" icon={<Icon.Search />} defaultOpen={true}>
      <div style={{ position: 'relative' }}>
        <span style={{
          position: 'absolute', left: '9px', top: '50%', transform: 'translateY(-50%)',
          color: C.textLight, display: 'flex',
        }}>
          <Icon.Search />
        </span>
        <input value={q} onChange={e => setQ(e.target.value)}
          placeholder="Arrondissement, code, quartier..."
          style={{
            width: '100%', padding: '8px 10px 8px 30px', border: `1px solid ${C.border}`,
            borderRadius: '8px', fontSize: '12.5px', color: C.text, background: C.bg,
            outline: 'none', fontFamily: 'inherit', transition: 'border-color 0.15s',
          }}
          onFocus={e => (e.target.style.borderColor = C.accentMid)}
          onBlur={e => (e.target.style.borderColor = C.border)}
        />
      </div>
      {results.length > 0 && (
        <div style={{
          marginTop: '6px', border: `1px solid ${C.border}`, borderRadius: '8px',
          overflow: 'hidden', background: C.panel, boxShadow: '0 4px 12px rgba(0,0,0,0.08)',
        }}>
          {results.map((z, i) => (
            <button key={z.code} onClick={() => { onSelect(z); setQ(''); }} style={{
              display: 'block', width: '100%', padding: '8px 12px', textAlign: 'left',
              background: 'none', border: 'none', cursor: 'pointer', fontSize: '12.5px',
              color: C.text, borderBottom: i < results.length - 1 ? `1px solid ${C.border}` : 'none',
              fontFamily: 'inherit',
            }}
              onMouseEnter={e => (e.currentTarget.style.background = C.accentXLight)}
              onMouseLeave={e => (e.currentTarget.style.background = 'none')}
            >
              <span style={{ fontWeight: 500 }}>{z.name}</span>
              <span style={{ color: C.textLight, marginLeft: '8px', fontSize: '11.5px' }}>{z.code}</span>
            </button>
          ))}
        </div>
      )}
    </Section>
  );
}
