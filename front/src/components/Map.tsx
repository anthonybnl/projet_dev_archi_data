import { useEffect, useRef } from 'react'
import maplibregl from 'maplibre-gl'
import 'maplibre-gl/dist/maplibre-gl.css'
import type { FeatureCollection, Geometry } from 'geojson'
import type { Indicator, ScoresMap } from '../types'

const API = '/api'

const COLOR_EXPR = (field: Indicator): maplibregl.ExpressionSpecification => [
    'interpolate', ['linear'], ['get', field],
    0,   '#e74c3c',
    0.5, '#f39c12',
    1,   '#2ecc71',
]

interface Props {
    selectedIndicator: Indicator
}

export default function Map({ selectedIndicator }: Props) {
    const containerRef = useRef<HTMLDivElement>(null)
    const mapRef = useRef<maplibregl.Map | null>(null)
    const loadedRef = useRef(false)

    // Initialise la carte et charge les données une seule fois
    useEffect(() => {
        if (!containerRef.current || mapRef.current) return

        mapRef.current = new maplibregl.Map({
            container: containerRef.current,
            // style: 'https://tiles.openfreemap.org/styles/liberty',
            style: 'https://tiles.openfreemap.org/styles/bright',
            // style: 'https://basemaps.cartocdn.com/gl/positron-gl-style/style.json',
            //   style: 'https://basemaps.cartocdn.com/gl/voyager-gl-style/style.json',
            center: [2.3488, 48.8534],  // Paris
            zoom: 11,
        })

        const map = mapRef.current
        map.addControl(new maplibregl.NavigationControl(), 'top-right')

        map.on('load', async () => {
            const [geojson, scores]: [FeatureCollection<Geometry>, ScoresMap] =
                await Promise.all([
                    fetch(`${API}/features/`).then(r => r.json()),
                    fetch(`${API}/scores/`).then(r => r.json()),
                ])

            // Injection de tous les scores dans les propriétés de chaque feature
            const enriched: FeatureCollection<Geometry> = {
                ...geojson,
                features: geojson.features
                    .filter(f => f.geometry !== null)
                    .map(f => {
                        const num = String(Math.round(
                            f.properties?.c_ar ?? 0
                        ))
                        const s = scores[num] ?? { environnement: 0, mobilite: 0, score: 0 }
                        return {
                            ...f,
                            properties: { ...f.properties, ...s },
                        }
                    }),
            }

            map.addSource('arrondissements', { type: 'geojson', data: enriched })

            map.addLayer({
                id: 'arrondissements-fill',
                type: 'fill',
                source: 'arrondissements',
                paint: {
                    'fill-color': COLOR_EXPR(selectedIndicator),
                    'fill-opacity': 0.6,
                },
            })

            map.addLayer({
                id: 'arrondissements-border',
                type: 'line',
                source: 'arrondissements',
                paint: {
                    'line-color': '#ffffff',
                    'line-width': 1.5,
                    'line-opacity': 0.8,
                },
            })

            // Popup au survol
            const popup = new maplibregl.Popup({ closeButton: false, closeOnClick: false })

            map.on('mousemove', 'arrondissements-fill', (e) => {
                map.getCanvas().style.cursor = 'pointer'
                const feature = e.features?.[0]
                if (!feature) return
                const p = feature.properties as {
                    c_ar: number
                    environnement: number
                    mobilite: number
                    score: number
                }
                const num = p.c_ar
                popup
                    .setLngLat(e.lngLat)
                    .setHTML(`
                        <strong>Paris ${num}</strong><br/>
                        Environnement : ${(p.environnement * 100).toFixed(0)} / 100<br/>
                        Mobilité : ${(p.mobilite * 100).toFixed(0)} / 100<br/>
                        <br/>
                        Total : ${(p.score * 100).toFixed(0)} / 100
                    `)
                    .addTo(map)
            })
            map.on('mouseleave', 'arrondissements-fill', () => {
                map.getCanvas().style.cursor = ''
                popup.remove()
            })

            loadedRef.current = true
        })

        return () => {
            mapRef.current?.remove()
            mapRef.current = null
            loadedRef.current = false
        }
    }, []) // eslint-disable-line react-hooks/exhaustive-deps

    // Met à jour la couleur quand l'indicateur change
    useEffect(() => {
        if (!loadedRef.current || !mapRef.current) return
        mapRef.current.setPaintProperty(
            'arrondissements-fill',
            'fill-color',
            COLOR_EXPR(selectedIndicator)
        )
    }, [selectedIndicator])

    return <div ref={containerRef} style={{ width: '100%', height: '100vh' }} />
}
