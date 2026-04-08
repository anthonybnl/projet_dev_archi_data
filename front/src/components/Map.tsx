import { useEffect, useRef } from 'react'
import maplibregl from 'maplibre-gl'
import 'maplibre-gl/dist/maplibre-gl.css'
import arrondissementsRaw from '../assets/arrondissements.geojson'
import type { FeatureCollection, Geometry } from 'geojson'

function buildGeoJSON(): FeatureCollection<Geometry> {
    // arrondissements : https://opendata.paris.fr/explore/dataset/arrondissements/information/
    const geojson = arrondissementsRaw as FeatureCollection<Geometry>
    return {
        ...geojson,
        features: geojson.features
            .filter(f => f.geometry !== null)
            .map(f => ({
                ...f,
                properties: {
                    ...f.properties,
                    score: Math.round(Math.random() * 100),
                },
            })),
    }
}

export default function Map() {
    const containerRef = useRef<HTMLDivElement>(null)
    const mapRef = useRef<maplibregl.Map | null>(null)

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

        map.on('load', () => {
            map.addSource('arrondissements', {
                type: 'geojson',
                data: buildGeoJSON(),
            })

            // on colorie l'arrondissement en fonction du score
            map.addLayer({
                id: 'arrondissements-fill',
                type: 'fill',
                source: 'arrondissements',
                paint: {
                    'fill-color': [
                        'interpolate', ['linear'], ['get', 'score'],
                        0, '#e74c3c',
                        50, '#f39c12',
                        100, '#2ecc71',
                    ],
                    'fill-opacity': 0.55,
                },
            })

            // contour des arrondissements
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

            const popup = new maplibregl.Popup({
                closeButton: false,
                closeOnClick: false,
            })

            map.on('mousemove', 'arrondissements-fill', (e) => {
                map.getCanvas().style.cursor = 'pointer'
                const feature = e.features?.[0]
                if (!feature) return
                const { c_ar: numero_arrondissement, score } = feature.properties as {
                    c_ar: number
                    score: number
                }
                popup
                    .setLngLat(e.lngLat)
                    .setHTML(
                        `<strong>Paris ${numero_arrondissement}</strong><br/>Score : ${score} / 100`
                    )
                    .addTo(map)
            })

            map.on('mouseleave', 'arrondissements-fill', () => {
                map.getCanvas().style.cursor = ''
                popup.remove()
            })
        })

        return () => {
            mapRef.current?.remove()
            mapRef.current = null
        }
    }, [])

    return <div ref={containerRef} style={{ width: '100%', height: '100vh' }} />
}
