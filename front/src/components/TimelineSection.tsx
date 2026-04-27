import { C } from '../lib/theme';
import { Icon } from './Icons';
import { Section } from './Section';
import { YEARS } from '../lib/indicators';

// slider d'années + chips cliquables
export function TimelineSection({
  year,
  onChange,
}: {
  year: number;
  onChange: (y: number) => void;
}) {
  return (
    <Section title="Chronologie" icon={<Icon.Cal />}>
      <div>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '10px' }}>
          <span style={{ fontSize: '12px', color: C.textMid }}>Année de référence</span>
          <span style={{ fontSize: '14px', fontWeight: 700, color: C.accent, fontVariantNumeric: 'tabular-nums' }}>
            {year}
          </span>
        </div>
        <input type="range" min={2018} max={2025} value={year}
          onChange={e => onChange(+e.target.value)}
          style={{ width: '100%', accentColor: C.accent }} />
        <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: '4px', marginBottom: '10px' }}>
          <span style={{ fontSize: '10.5px', color: C.textLight }}>2018</span>
          <span style={{ fontSize: '10.5px', color: C.textLight }}>2025</span>
        </div>
        <div style={{ display: 'flex', gap: '4px', flexWrap: 'wrap' }}>
          {YEARS.map(y => (
            <button key={y} onClick={() => onChange(y)} style={{
              padding: '3px 8px', borderRadius: '6px', fontSize: '11px', border: 'none',
              background: y === year ? C.accent : C.border,
              color: y === year ? 'white' : C.textMid,
              cursor: 'pointer', fontFamily: 'inherit',
              fontWeight: y === year ? 600 : 400, transition: 'all 0.12s',
            }}>{y}</button>
          ))}
        </div>
      </div>
    </Section>
  );
}
