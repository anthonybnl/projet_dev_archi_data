import { useState } from 'react'
import Map from './components/Map'
import Sidebar from './components/Sidebar'
import type { Indicator } from './types'
import './App.css'

export default function App() {
  const [selectedIndicator, setSelectedIndicator] = useState<Indicator>('score')

  return (
    <div className="app-layout">
      <Sidebar selected={selectedIndicator} onChange={setSelectedIndicator} />
      <div className="map-wrapper">
        <Map selectedIndicator={selectedIndicator} />
      </div>
    </div>
  )
}
