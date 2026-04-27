import { C } from '../lib/theme';

// jauge colorée pour l'IAI
// l'IAI réel = mois de revenu pour 1m² → typiquement 4-15 à Paris
// on rescale sur 0-100 pour la visualisation : moins de mois = mieux
// seuils : <5 (bon), 5-10 (moyen), >10 (faible)
function evaluerIai(iai: number) {
  if (iai < 5) return { color: '#2d6a4f', label: 'Bon', score: 100 - iai * 8 };
  if (iai < 10) return { color: '#e6891a', label: 'Moyen', score: 100 - iai * 6 };
  return { color: '#c0392b', label: 'Faible', score: Math.max(10, 100 - iai * 5) };
}

export function IAIGauge({ value }: { value: number | null }) {
  if (value === null || value === undefined) {
    return (
      <div style={{ fontSize: '11px', color: C.textLight, padding: '6px 0' }}>
        IAI · pas de donnée pour cette zone
      </div>
    );
  }
  const { color, label, score } = evaluerIai(value);
  const pct = Math.max(0, Math.min(100, score)) / 100;

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '5px' }}>
        <span style={{ fontSize: '11px', color: C.textMid }}>IAI · Accessibilité Immobilière</span>
        <span style={{ fontSize: '12px', fontWeight: 700, color, display: 'flex', alignItems: 'center', gap: '5px' }}>
          <span style={{ fontSize: '10px', fontWeight: 500, padding: '1px 5px', borderRadius: '4px', background: color + '18', color }}>
            {label}
          </span>
          {value.toFixed(1)} mois/m²
        </span>
      </div>
      <div style={{ height: '6px', borderRadius: '3px', background: '#e0ddd8', overflow: 'hidden', position: 'relative' }}>
        <div style={{
          height: '100%', width: `${pct * 100}%`, borderRadius: '3px',
          background: `linear-gradient(to right, #74c69d, ${color})`,
          transition: 'width 0.4s ease',
        }} />
      </div>
    </div>
  );
}
