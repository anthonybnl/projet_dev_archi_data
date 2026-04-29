import { useEffect, useRef, useState } from 'react';
import maplibregl from 'maplibre-gl';
import 'maplibre-gl/dist/maplibre-gl.css';
import { C, rampColor } from '../lib/theme';
import { INDICATORS, fmtVal, fmtShort } from '../lib/indicators';
import type { FeatureCollection, Feature, Polygon, MultiPolygon } from 'geojson';
import type { IndicatorId, ZoneData, Granularity } from '../lib/types';

// seuil de zoom où on bascule des arrondissements aux IRIS
// en dessous : choroplèthe par arrondissement (20 zones)
// au-dessus : choroplèthe par IRIS (~992 zones, plus précis)
const ZOOM_BASCULE_IRIS = 13;

// limites approximatives de Paris pour empêcher la carte de partir trop loin
const PARIS_BOUNDS: maplibregl.LngLatBoundsLike = [
  [2.21, 48.80],
  [2.48, 48.91],
];

// style "Plan" : tuiles raster OSM (gratuit, pas de clé API)
// const STYLE_PLAN: maplibregl.StyleSpecification = {
//   version: 8,
//   sources: {
//     'osm': {
//       type: 'raster',
//       tiles: ['https://tile.openstreetmap.org/{z}/{x}/{y}.png'],
//       tileSize: 256,
//       attribution: '© OpenStreetMap',
//     },
//   },
//   layers: [
//     { id: 'osm', type: 'raster', source: 'osm' },
//   ],
// };

const STYLE_PLAN = "https://tiles.openfreemap.org/styles/bright"
// fonction utilitaire qui colore un FeatureCollection selon un indicateur
// on injecte une propriété `_color` et `_value` dans chaque feature pour
// que MapLibre puisse les utiliser dans son expression de fill-color
function colorFeatures(
  fc: FeatureCollection,
  zonesByCode: Map<string, ZoneData>,
  codeProp: string,
  indicator: IndicatorId,
): FeatureCollection {
  // on calcule min/max pour normaliser
  const vals: number[] = [];
  for (const f of fc.features) {
    const code = String(f.properties?.[codeProp] ?? '');
    const z = zonesByCode.get(code);
    const v = z?.[indicator];
    if (v !== null && v !== undefined) vals.push(v);
  }
  const mn = vals.length ? Math.min(...vals) : 0;
  const mx = vals.length ? Math.max(...vals) : 1;
  const range = mx - mn || 1;

  return {
    type: 'FeatureCollection',
    features: fc.features.map(f => {
      const code = String(f.properties?.[codeProp] ?? '');
      const z = zonesByCode.get(code);
      const v = z?.[indicator];
      const t = v !== null && v !== undefined ? (v - mn) / range : null;
      return {
        ...f,
        properties: {
          ...f.properties,
          _code: code,
          _name: f.properties?.l_aroff ?? f.properties?.nom_iris ?? code,
          _color: t !== null ? rampColor(t) : '#cccccc',
          _value: v,
          _hasValue: t !== null,
        },
      };
    }),
  };
}

export function MapView({
  arrondissementsGeo,
  irisGeo,
  zonesArrondissement,
  zonesIris,
  indicator,
  selectedCode,
  onSelect,
  granularity,
  onGranularityChange,
}: {
  arrondissementsGeo: FeatureCollection | null;
  irisGeo: FeatureCollection | null;
  zonesArrondissement: ZoneData[];
  zonesIris: ZoneData[];
  indicator: IndicatorId;
  selectedCode: string | null;
  onSelect: (code: string | null) => void;
  granularity: Granularity;
  onGranularityChange: (g: Granularity) => void;
}) {
  const containerRef = useRef<HTMLDivElement>(null);
  const mapRef = useRef<maplibregl.Map | null>(null);
  const [hover, setHover] = useState<{ x: number; y: number; name: string; value: number | null } | null>(null);

  // init de la carte une seule fois
  useEffect(() => {
    if (!containerRef.current || mapRef.current) return;

    const map = new maplibregl.Map({
      container: containerRef.current,
      style: STYLE_PLAN,
      center: [2.3522, 48.8566],
      zoom: 11.5,
      maxBounds: PARIS_BOUNDS,
      minZoom: 10,
      maxZoom: 17,
      attributionControl: false,
    });

    map.addControl(new maplibregl.AttributionControl({ compact: true }), 'bottom-right');
    map.addControl(new maplibregl.NavigationControl({ showCompass: false }), 'top-right');

    // on bascule la granularité quand l'utilisateur zoome
    map.on('zoomend', () => {
      const z = map.getZoom();
      if (z >= ZOOM_BASCULE_IRIS) onGranularityChange('iris');
      else onGranularityChange('arrondissement');
    });

    mapRef.current = map;

    return () => {
      map.remove();
      mapRef.current = null;
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  useEffect(() => {
    const map = mapRef.current;
    if (!map) return;
    map.setStyle(STYLE_PLAN);
    map.once('styledata', () => {
      // une fois le style chargé on relance l'effet d'ajout des couches data
      // (en changeant `mapMode` on repasse aussi par l'autre useEffect ci-dessous)
      forceLayersUpdate();
    });
  }, []);

  // déclencheur manuel pour rafraîchir les couches data (ajout/maj sources)
  const [layersTick, setLayersTick] = useState(0);
  const forceLayersUpdate = () => setLayersTick(t => t + 1);

  const lineWidths = [0.1, 0.2]

  // ajoute / met à jour les couches choroplèthe à chaque changement de données
  useEffect(() => {
    const map = mapRef.current;
    if (!map || !arrondissementsGeo) return;

    const apply = () => {
      // ─── couche arrondissements ────────────────────────────────────────
      const arrFc = colorFeatures(
        arrondissementsGeo,
        new Map(zonesArrondissement.map(z => [z.code, z])),
        'c_ar',
        indicator,
      );

      if (map.getSource('arr-src')) {
        (map.getSource('arr-src') as maplibregl.GeoJSONSource).setData(arrFc);
        map.setPaintProperty('arr-line', 'line-width', [
          'case', ['==', ['get', '_code'], selectedCode || ''], 2.5, 1,
        ]);
      } else {
        map.addSource('arr-src', { type: 'geojson', data: arrFc });
        map.addLayer({
          id: 'arr-fill', type: 'fill', source: 'arr-src',
          maxzoom: ZOOM_BASCULE_IRIS,
          paint: {
            'fill-color': ['get', '_color'],
            'fill-opacity': 0.7,
          },
        });
        map.addLayer({
          id: 'arr-line', type: 'line', source: 'arr-src',
          maxzoom: ZOOM_BASCULE_IRIS,
          paint: {
            'line-color': C.accentHover,
            'line-width': [
              'case',
              ['==', ['get', '_code'], selectedCode || ''], lineWidths[1],
              lineWidths[0],
            ],
            'line-opacity': 0.7,
          },
        });
        map.addLayer({
          id: 'arr-label', type: 'symbol', source: 'arr-src',
          maxzoom: ZOOM_BASCULE_IRIS,
          layout: {
            'text-field': ['concat', ['to-string', ['get', 'c_ar']], 'e'],
            'text-font': ['Open Sans Regular', 'Arial Unicode MS Regular'],
            'text-size': 12,
            'text-allow-overlap': false,
          },
          paint: {
            'text-color': '#1a1a18',
            'text-halo-color': 'rgba(255,255,255,0.85)',
            'text-halo-width': 1.4,
          },
        });

        // gestion souris arrondissements
        map.on('click', 'arr-fill', (e) => {
          const f = e.features?.[0];
          if (f) onSelect(String(f.properties?._code ?? ''));
        });
        map.on('mousemove', 'arr-fill', (e) => {
          map.getCanvas().style.cursor = 'pointer';
          const f = e.features?.[0];
          if (f) {
            setHover({
              x: e.point.x, y: e.point.y,
              name: String(f.properties?._name ?? ''),
              value: f.properties?._hasValue ? Number(f.properties?._value) : null,
            });
          }
        });
        map.on('mouseleave', 'arr-fill', () => {
          map.getCanvas().style.cursor = '';
          setHover(null);
        });
      }

      // ─── couche IRIS ──────────────────────────────────────────────────
      if (irisGeo) {
        const irisFc = colorFeatures(
          irisGeo,
          new Map(zonesIris.map(z => [z.code, z])),
          'code_iris',
          indicator,
        );

        if (map.getSource('iris-src')) {
          (map.getSource('iris-src') as maplibregl.GeoJSONSource).setData(irisFc);
          map.setPaintProperty('iris-line', 'line-width', [
            'case', ['==', ['get', '_code'], selectedCode || ''], 2, 0.6,
          ]);
        } else {
          map.addSource('iris-src', { type: 'geojson', data: irisFc });
          map.addLayer({
            id: 'iris-fill', type: 'fill', source: 'iris-src',
            minzoom: ZOOM_BASCULE_IRIS,
            paint: {
              'fill-color': ['get', '_color'],
              'fill-opacity': 0.7,
            },
          });
          map.addLayer({
            id: 'iris-line', type: 'line', source: 'iris-src',
            minzoom: ZOOM_BASCULE_IRIS,
            paint: {
              'line-color': C.accentHover,
              'line-width': [
                'case',
                ['==', ['get', '_code'], selectedCode || ''], lineWidths[1],
                lineWidths[0],
              ],
              'line-opacity': 0.7,
            },
          });

          map.on('click', 'iris-fill', (e) => {
            const f = e.features?.[0];
            if (f) onSelect(String(f.properties?._code ?? ''));
          });
          map.on('mousemove', 'iris-fill', (e) => {
            map.getCanvas().style.cursor = 'pointer';
            const f = e.features?.[0];
            if (f) {
              setHover({
                x: e.point.x, y: e.point.y,
                name: String(f.properties?._name ?? ''),
                value: f.properties?._hasValue ? Number(f.properties?._value) : null,
              });
            }
          });
          map.on('mouseleave', 'iris-fill', () => {
            map.getCanvas().style.cursor = '';
            setHover(null);
          });
        }
      }
    };

    if (map.isStyleLoaded()) apply();
    else map.once('load', apply);
  }, [arrondissementsGeo, irisGeo, zonesArrondissement, zonesIris, indicator, selectedCode, layersTick]);

  // calcul des stats pour la légende
  const ind = INDICATORS.find(i => i.id === indicator)!;
  const zonesActives = granularity === 'iris' ? zonesIris : zonesArrondissement;
  const valsActives = zonesActives.map(z => z[indicator]).filter((v): v is number => v !== null);
  const mn = valsActives.length ? Math.min(...valsActives) : 0;
  const mx = valsActives.length ? Math.max(...valsActives) : 0;

  return (
    <div style={{ flex: 1, position: 'relative', overflow: 'hidden', background: C.mapBg }}>
      <div ref={containerRef} style={{ position: 'absolute', inset: 0 }} />

      {/* indication granularité actuelle (arr/iris) */}
      <div style={{
        position: 'absolute', top: '12px', left: '12px', zIndex: 10,
        background: C.panel, padding: '6px 11px', borderRadius: '8px',
        border: `1px solid ${C.border}`, fontSize: '11.5px', color: C.textMid,
        boxShadow: '0 2px 8px rgba(0,0,0,0.06)',
      }}>
        Granularité : <span style={{ fontWeight: 600, color: C.accent }}>
          {granularity === 'iris' ? 'IRIS' : 'Arrondissement'}
        </span>
      </div>

      {/* légende */}
      <div style={{
        position: 'absolute', bottom: '32px', left: '12px', zIndex: 10,
        background: C.panel, borderRadius: '8px', padding: '9px 11px',
        border: `1px solid ${C.border}`, boxShadow: '0 2px 8px rgba(0,0,0,0.1)', minWidth: '160px',
      }}>
        <div style={{
          fontSize: '10px', fontWeight: 600, color: C.textMid, marginBottom: '5px',
          textTransform: 'uppercase', letterSpacing: '0.05em',
        }}>{ind.short}</div>
        <div style={{
          height: '7px', borderRadius: '4px',
          background: 'linear-gradient(to right, #d8f3dc, #52b788, #1b4332)', marginBottom: '4px',
        }} />
        <div style={{ display: 'flex', justifyContent: 'space-between' }}>
          <span style={{ fontSize: '9.5px', color: C.textLight }}>{fmtShort(mn, indicator)}</span>
          <span style={{ fontSize: '9.5px', color: C.textLight }}>{fmtShort(mx, indicator)}</span>
        </div>
      </div>

      {/* tooltip de survol */}
      {hover && (
        <div style={{
          position: 'absolute',
          left: Math.min(hover.x + 14, (containerRef.current?.offsetWidth || 9999) - 220),
          top: Math.max(hover.y - 52, 8),
          background: 'rgba(8,18,12,0.90)', color: 'white',
          padding: '8px 11px', borderRadius: '7px',
          fontSize: '12px', pointerEvents: 'none', zIndex: 20,
          backdropFilter: 'blur(6px)', lineHeight: 1.5, maxWidth: '210px',
          boxShadow: '0 4px 16px rgba(0,0,0,0.3)',
        }}>
          <div style={{ fontWeight: 700, marginBottom: '2px' }}>{hover.name}</div>
          <div style={{ opacity: 0.75, fontSize: '11px' }}>
            {ind.short} · {fmtVal(hover.value, indicator)}
          </div>
        </div>
      )}
    </div>
  );
}
