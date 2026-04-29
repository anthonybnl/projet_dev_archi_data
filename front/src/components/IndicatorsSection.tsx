import { C } from '../lib/theme';
import { Icon } from './Icons';
import { Section } from './Section';
import { INDICATORS } from '../lib/indicators';
import type { IndicatorId } from '../lib/types';

// liste des 4 indicateurs avec checkboxes + un seul "primary" qui colore la carte
// click sur la ligne = sélectionne comme primary, click sur la checkbox = active/désactive
export function IndicatorsSection({
  active,
  onToggle,
  primary,
  onPrimary,
}: {
  active: IndicatorId[];
  onToggle: (id: IndicatorId) => void;
  primary: IndicatorId;
  onPrimary: (id: IndicatorId) => void;
}) {
  return (
    <Section title="Indicateurs" icon={<Icon.Chart />}>
      <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
        {INDICATORS.map(ind => {
          const isActive = active.includes(ind.id);
          const isPrimary = primary === ind.id;
          return (
            <div key={ind.id} onClick={() => onPrimary(ind.id)} style={{
              display: 'flex', alignItems: 'center', gap: '10px', padding: '8px 10px',
              borderRadius: '8px',
              border: `1px solid ${isPrimary ? C.accent + '66' : C.border}`,
              background: isPrimary ? C.accentXLight : C.bg, cursor: 'pointer',
              transition: 'all 0.15s',
            }}>
              {/* <div onClick={e => { e.stopPropagation(); onToggle(ind.id); }} style={{
                width: '15px', height: '15px', borderRadius: '4px', flexShrink: 0, cursor: 'pointer',
                background: isActive ? ind.color : 'transparent',
                border: `1.5px solid ${isActive ? ind.color : C.borderMid}`,
                display: 'flex', alignItems: 'center', justifyContent: 'center', transition: 'all 0.15s',
              }}>
                {isActive && (
                  <svg width="9" height="9" viewBox="0 0 9 9">
                    <path d="M1.5 4.5l2 2 4-4" stroke="white" strokeWidth="1.5"
                      strokeLinecap="round" strokeLinejoin="round" fill="none" />
                  </svg>
                )}
              </div> */}
              <div style={{ flex: 1, minWidth: 0 }}>
                <div style={{ fontSize: '12px', fontWeight: isPrimary ? 600 : 400, color: C.text, lineHeight: 1.3 }}>
                  {ind.label}
                </div>
                {isPrimary && (
                  <div style={{ fontSize: '10.5px', color: C.accent, marginTop: '2px', fontWeight: 500 }}>
                    Visible sur la carte
                  </div>
                )}
              </div>
              {/* <div style={{ width: '9px', height: '9px', borderRadius: '50%', background: ind.color, flexShrink: 0 }} /> */}
            </div>
          );
        })}
      </div>
    </Section>
  );
}
