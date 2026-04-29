import { C } from '../lib/theme';
import { Icon } from './Icons';
import { Section } from './Section';
import { IAIGauge } from './IAIGauge';
import { fmtVal } from '../lib/indicators';
import type { ZoneData } from '../lib/types';

// panneau de détails affiché quand une zone est sélectionnée sur la carte
// si rien n'est sélectionné, on affiche une invitation à cliquer
export function DetailsSection({
  zone,
  onPin,
  pinned,
}: {
  zone: ZoneData | null;
  onPin: (z: ZoneData) => void;
  pinned: ZoneData[];
}) {
  if (!zone) {
    return (
      <Section title="Détails" icon={<Icon.Info />}>
        <div style={{
          textAlign: 'center', padding: '20px 0', color: C.textLight,
          fontSize: '12.5px', lineHeight: 1.6,
        }}>
          <div style={{ fontSize: '22px', marginBottom: '6px', opacity: 0.4 }}>
            <svg width="32" height="32" viewBox="0 0 32 32" fill="none" style={{ margin: '0 auto', display: 'block' }}>
              <circle cx="16" cy="16" r="14" stroke={C.textLight} strokeWidth="1.5" />
              <path d="M10 16 C10 12 13 9 16 9 C19 9 22 12 22 16 C22 20 19 22 16 22"
                stroke={C.textLight} strokeWidth="1.5" strokeLinecap="round" />
              <circle cx="16" cy="26" r="1.5" fill={C.textLight} />
            </svg>
          </div>
          Sélectionnez une zone<br />sur la carte pour voir les détails
        </div>
      </Section>
    );
  }

  const isPinned = pinned.some(p => p.code === zone.code);
  const displayName = zone.code.length <= 2
    ? `${zone.arrondissement}${zone.arrondissement === 1 ? 'er' : 'e'} arrondissement`
    : `IRIS ${zone.code}`;
  const rows: { label: string; value: string }[] = [
    { label: 'Prix m² médian',          value: fmtVal(zone.prix_m2_median, 'prix_m2_median') },
    { label: 'Logements sociaux fin.',  value: fmtVal(zone.nb_logements_sociaux_finances, 'nb_logements_sociaux_finances') },
    { label: 'Revenu médian',            value: fmtVal(zone.revenu_median, 'revenu_median') },
  ];

  return (
    <Section title="Détails" icon={<Icon.Info />} defaultOpen={true}>
      <div style={{
        background: C.accentXLight, borderRadius: '9px', padding: '10px 12px', marginBottom: '10px',
        border: `1px solid ${C.accentLight}`,
      }}>
        <div style={{ fontWeight: 700, fontSize: '14px', color: C.text }}>{displayName}</div>
        <div style={{ fontSize: '11px', color: C.textMid, marginTop: '2px', fontFamily: 'monospace' }}>
          {zone.code.length === 9 ? `IRIS ${zone.code}` : `Arr. ${zone.code}`}
        </div>
      </div>
      {rows.map((row, i) => (
        <div key={i} style={{
          display: 'flex', justifyContent: 'space-between', alignItems: 'center',
          padding: '7px 0', borderBottom: `1px solid ${C.border}`,
        }}>
          <span style={{ fontSize: '11.5px', color: C.textMid }}>{row.label}</span>
          <span style={{ fontSize: '13px', fontWeight: 600, color: C.text, fontVariantNumeric: 'tabular-nums' }}>
            {row.value}
          </span>
        </div>
      ))}
      <div style={{ paddingTop: '10px', marginBottom: '12px' }}>
        <IAIGauge value={zone.iai} />
      </div>
      <button onClick={() => onPin(zone)} style={{
        width: '100%', padding: '7px 12px', borderRadius: '8px', cursor: 'pointer',
        border: `1.5px solid ${isPinned ? C.accent : C.borderMid}`,
        background: isPinned ? C.accentLight : 'transparent',
        color: isPinned ? C.accent : C.textMid,
        fontSize: '12px', fontWeight: 600, display: 'flex', alignItems: 'center',
        justifyContent: 'center', gap: '6px', transition: 'all 0.15s',
        fontFamily: 'inherit',
      }}>
        <Icon.Pin />
        {isPinned ? 'Épinglé pour comparaison' : 'Épingler pour comparaison'}
      </button>
    </Section>
  );
}
