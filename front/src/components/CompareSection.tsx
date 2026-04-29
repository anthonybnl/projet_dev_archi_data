import { useState } from 'react';
import { C } from '../lib/theme';
import { Icon } from './Icons';
import { Section } from './Section';
import { INDICATORS } from '../lib/indicators';
import type { ZoneData } from '../lib/types';

// permet d'épingler 2 zones et d'afficher leurs valeurs côte à côte
// pour chaque indicateur, on met en valeur la "meilleure" valeur (prix bas = bon, autres : haut = bon)
export function CompareSection({
  pinned,
  onUnpin,
}: {
  pinned: ZoneData[];
  onUnpin: (code: string) => void;
}) {
  const [open, setOpen] = useState(false);
  const canCompare = pinned.length >= 2;

  return (
    <Section title="Comparaison" icon={<Icon.Compare />} defaultOpen={false}>
      {pinned.length === 0 && (
        <p style={{ fontSize: '12px', color: C.textLight, lineHeight: 1.6 }}>
          Épinglez 2 zones depuis les détails pour les comparer.
        </p>
      )}
      {pinned.length > 0 && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '6px', marginBottom: '10px' }}>
          {pinned.map(z => (
            <div key={z.code} style={{
              display: 'flex', alignItems: 'center', justifyContent: 'space-between',
              padding: '7px 10px', borderRadius: '8px', background: C.accentXLight,
              border: `1px solid ${C.accentLight}`,
            }}>
              <span style={{ fontSize: '12.5px', fontWeight: 600, color: C.text }}>
                {z.code.length <= 2 ? `${z.arrondissement}${z.arrondissement === 1 ? 'er' : 'e'} arr.` : `IRIS ${z.code}`}
              </span>
              <button onClick={() => onUnpin(z.code)} style={{
                background: 'none', border: 'none', cursor: 'pointer', color: C.textLight,
                padding: '2px', display: 'flex', borderRadius: '4px',
              }}><Icon.X /></button>
            </div>
          ))}
          {pinned.length < 2 && (
            <p style={{ fontSize: '11.5px', color: C.textMid, textAlign: 'center', padding: '4px 0' }}>
              Ajoutez encore {2 - pinned.length} zone(s)
            </p>
          )}
        </div>
      )}
      {canCompare && (
        <button onClick={() => setOpen(o => !o)} style={{
          width: '100%', padding: '8px', borderRadius: '8px',
          background: open ? C.accent : C.accentXLight,
          border: `1.5px solid ${C.accent}`,
          color: open ? 'white' : C.accent,
          fontSize: '12.5px', fontWeight: 700, cursor: 'pointer', fontFamily: 'inherit',
          transition: 'all 0.15s',
        }}>
          {open ? 'Masquer la comparaison' : 'Comparer les zones'}
        </button>
      )}
      {open && canCompare && (
        <div style={{
          marginTop: '10px', borderRadius: '9px', overflow: 'hidden',
          border: `1px solid ${C.border}`, fontSize: '11.5px',
        }}>
          <div style={{
            display: 'grid', gridTemplateColumns: '1fr 90px 90px',
            background: C.bg, padding: '7px 10px', borderBottom: `1px solid ${C.border}`,
          }}>
            <span style={{ color: C.textLight, fontSize: '10.5px', fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.05em' }}>
              Indicateur
            </span>
            {pinned.slice(0, 2).map(z => (
              <span key={z.code} style={{ color: C.accent, fontWeight: 700, textAlign: 'right', fontSize: '11px' }}>
                {/* on prend juste le numéro d'arrondissement pour l'en-tête */}
                {z.arrondissement}
              </span>
            ))}
          </div>
          {INDICATORS.map(ind => {
            const vals = pinned.slice(0, 2).map(z => z[ind.id]);
            // pour le prix et l'iai (mois/m²) : valeur basse = mieux
            // pour social et revenu : valeur haute = mieux
            const lowerIsBetter = ind.id === 'prix_m2_median' || ind.id === 'iai';
            let betterIdx = -1;
            if (vals[0] !== null && vals[1] !== null) {
              betterIdx = lowerIsBetter
                ? (vals[0]! < vals[1]! ? 0 : 1)
                : (vals[0]! > vals[1]! ? 0 : 1);
            }
            return (
              <div key={ind.id} style={{
                display: 'grid', gridTemplateColumns: '1fr 90px 90px',
                padding: '7px 10px', borderBottom: `1px solid ${C.border}`, alignItems: 'center',
              }}>
                <span style={{ color: C.textMid, fontSize: '10.5px' }}>{ind.short}</span>
                {vals.map((v, i) => (
                  <span key={i} style={{
                    fontWeight: i === betterIdx ? 700 : 400,
                    color: i === betterIdx ? C.accent : C.textMid,
                    textAlign: 'right', fontVariantNumeric: 'tabular-nums', fontSize: '11.5px',
                  }}>
                    {v === null
                      ? '—'
                      : ind.id === 'iai'
                      ? v.toFixed(1)
                      : Math.round(v).toLocaleString('fr-FR')}
                  </span>
                ))}
              </div>
            );
          })}
        </div>
      )}
    </Section>
  );
}
