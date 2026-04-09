import { useState } from 'react'
import Map from './components/Map'
import Sidebar from './components/Sidebar'
import type { Indicator } from './types'
import './App.css'

export default function App() {
  const [selectedIndicator, setSelectedIndicator] = useState<Indicator>('score')
  const [showEspacesVerts, setShowEspacesVerts] = useState(false)

  return (
    <div className="app-layout">
      <Sidebar
        selected={selectedIndicator}
        onChange={setSelectedIndicator}
        showEspacesVerts={showEspacesVerts}
        onToggleEspacesVerts={() => setShowEspacesVerts(v => !v)}
      />
      <div className="map-wrapper">
        <Map selectedIndicator={selectedIndicator} showEspacesVerts={showEspacesVerts} />
      </div>
    </div>
  )
}
