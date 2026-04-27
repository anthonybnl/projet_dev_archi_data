import { C } from '../lib/theme';
import { Icon } from './Icons';
import { INDICATORS } from '../lib/indicators';
import type { IndicatorId } from '../lib/types';

// barre du haut : logo + titre + pill de l'indicateur courant + badge sources
export function Header({ indicator, year }: { indicator: IndicatorId; year: number }) {
  const ind = INDICATORS.find(i => i.id === indicator)!;

  return (
    <header style={{
      height: '50px', background: C.panel, borderBottom: `1px solid ${C.border}`,
      display: 'flex', alignItems: 'center', padding: '0 18px', gap: '10px',
      flexShrink: 0, boxShadow: '0 1px 3px rgba(0,0,0,0.06)', zIndex: 30,
    }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: '9px' }}>
        <div style={{
          width: '30px', height: '30px', borderRadius: '7px', background: C.accent,
          display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0,
        }}>
          <Icon.Globe />
        </div>
        <div>
          <div style={{ fontSize: '13.5px', fontWeight: 700, color: C.text, lineHeight: 1.25 }}>
            Urban Data Explorer
          </div>
          <div style={{ fontSize: '10px', color: C.textMid, lineHeight: 1.25 }}>
            Marché du logement · Paris
          </div>
        </div>
      </div>

      <div style={{ flex: 1 }} />

      <div style={{
        display: 'flex', alignItems: 'center', gap: '6px', padding: '4px 10px',
        background: C.accentXLight, borderRadius: '6px', border: `1px solid ${C.accentLight}`,
      }}>
        <div style={{ width: '7px', height: '7px', borderRadius: '50%', background: C.accent }} />
        <span style={{ fontSize: '11.5px', color: C.accent, fontWeight: 600 }}>
          {ind.short} · {year}
        </span>
      </div>

      <div style={{
        fontSize: '11px', color: C.textMid, padding: '4px 10px',
        border: `1px solid ${C.border}`, borderRadius: '6px', background: C.bg,
      }}>
        DVF · Filosofi · RPLS
      </div>
    </header>
  );
}
