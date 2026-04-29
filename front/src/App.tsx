import { useEffect, useMemo, useState } from 'react';
import maplibregl from 'maplibre-gl';
import { C } from './lib/theme';
import { Header } from './components/Header';
import { MapView } from './components/MapView';
import { SearchSection } from './components/SearchSection';
import { IndicatorsSection } from './components/IndicatorsSection';
import { TimelineSection } from './components/TimelineSection';
import { DetailsSection } from './components/DetailsSection';
import { CompareSection } from './components/CompareSection';
import {
  getArrondissementsGeojson,
  getIrisGeojson,
  getIndicateursArrondissement,
  getIndicateursIris,
} from './lib/api';
import type { FeatureCollection } from 'geojson';
import type { IndicatorId, ZoneData, Granularity } from './lib/types';

export default function App() {
  const [indicator, setIndicator] = useState<IndicatorId>('price');

  // inutilisé pour le moment
  const [activeInds, setActiveInds] = useState<IndicatorId[]>(['price', 'social', 'income', 'iai']);

  const [year, setYear] = useState(2025);
  const [selectedCode, setSelectedCode] = useState<string | null>(null);
  const [pinned, setPinned] = useState<ZoneData[]>([]);
  const [granularity, setGranularity] = useState<Granularity>('arrondissement');

  // données géographiques (chargées une fois au démarrage)
  const [arrGeo, setArrGeo] = useState<FeatureCollection | null>(null);
  const [irisGeo, setIrisGeo] = useState<FeatureCollection | null>(null);

  // données indicateurs (rechargées à chaque changement d'année)
  const [zonesArr, setZonesArr] = useState<ZoneData[]>([]);
  const [zonesIris, setZonesIris] = useState<ZoneData[]>([]);

  const [error, setError] = useState<string | null>(null);

  // chargement initial des geojson
  useEffect(() => {
    Promise.all([getArrondissementsGeojson(), getIrisGeojson()])
      .then(([arr, iris]) => { setArrGeo(arr); setIrisGeo(iris); })
      .catch(e => setError(`Erreur chargement carte : ${e.message}`));
  }, []);

  // chargement des indicateurs à chaque changement d'année
  useEffect(() => {
    Promise.all([getIndicateursArrondissement(year), getIndicateursIris(year)])
      .then(([a, i]) => { setZonesArr(a); setZonesIris(i); })
      .catch(e => setError(`Erreur chargement indicateurs : ${e.message}`));
  }, [year]);

  // les zones de la granularité courante (utilisées par recherche, détails, etc.)
  const zonesCourantes = granularity === 'iris' ? zonesIris : zonesArr;

  // zone sélectionnée actuellement (si elle existe dans les zones courantes)
  const selectedZone = useMemo(
    () => zonesCourantes.find(z => z.code === selectedCode) || null,
    [zonesCourantes, selectedCode],
  );

  const handleToggle = (id: IndicatorId) =>
    setActiveInds(p => (p.includes(id) ? p.filter(x => x !== id) : [...p, id]));

  const handlePin = (z: ZoneData) => {
    setPinned(p => {
      if (p.some(x => x.code === z.code)) return p;
      // on garde max 2 zones, on remplace la plus ancienne si déjà 2
      return p.length >= 2 ? [p[1], z] : [...p, z];
    });
  };

  const handleUnpin = (code: string) => setPinned(p => p.filter(z => z.code !== code));

  return (
    <div style={{ display: 'flex', flexDirection: 'column', height: '100vh', fontFamily: "'DM Sans',sans-serif" }}>
      <Header indicator={indicator} year={year} />

      {error && (
        <div style={{
          background: '#fef2f2', color: '#991b1b', padding: '8px 16px',
          fontSize: '12px', borderBottom: '1px solid #fecaca',
        }}>
          {error}
        </div>
      )}

      <div style={{ flex: 1, display: 'flex', overflow: 'hidden' }}>
        <MapView
          arrondissementsGeo={arrGeo}
          irisGeo={irisGeo}
          zonesArrondissement={zonesArr}
          zonesIris={zonesIris}
          indicator={indicator}
          selectedCode={selectedCode}
          onSelect={setSelectedCode}
          granularity={granularity}
          onGranularityChange={setGranularity}
        />

        <aside style={{
          width: '358px', flexShrink: 0, background: C.panel,
          borderLeft: `1px solid ${C.border}`,
          display: 'flex', flexDirection: 'column', overflow: 'hidden',
        }}>
          <div style={{ flex: 1, overflowY: 'auto' }}>
            <SearchSection
              zones={zonesCourantes}
              onSelect={z => setSelectedCode(z.code)}
            />
            <IndicatorsSection
              active={activeInds} onToggle={handleToggle}
              primary={indicator} onPrimary={setIndicator}
            />
            <TimelineSection year={year} onChange={setYear} />
            <DetailsSection zone={selectedZone} onPin={handlePin} pinned={pinned} />
            <CompareSection pinned={pinned} onUnpin={handleUnpin} />
          </div>

          <div style={{
            borderTop: `1px solid ${C.border}`, padding: '10px 16px',
            display: 'flex', alignItems: 'center', gap: '6px', flexShrink: 0,
          }}>
            <div style={{ width: '6px', height: '6px', borderRadius: '50%', background: C.accentMid }} />
            <span style={{ fontSize: '10.5px', color: C.textLight }}>
              Données DVF · Filosofi · RPLS — année {year}
            </span>
          </div>
        </aside>
      </div>
    </div>
  );
}
