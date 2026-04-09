import type { Indicator } from '../types'
import './Sidebar.css'

interface Props {
    selected: Indicator
    onChange: (i: Indicator) => void
    showEspacesVerts: boolean
    onToggleEspacesVerts: () => void
}

const OPTIONS: { value: Indicator; label: string }[] = [
    { value: 'score', label: 'Total' },
    { value: 'environnement', label: 'Environnement' },
    { value: 'mobilite', label: 'Mobilité' },
    { value: 'aucun', label: 'Aucun' },
]

export default function Sidebar({ selected, onChange, showEspacesVerts, onToggleEspacesVerts }: Props) {
    return (
        <aside className="sidebar">
            <h2 className="sidebar-title">Urban Data Explorer</h2>
            <p className="sidebar-subtitle">Paris — indicateurs par arrondissement</p>

            <div className="sidebar-section">
                <label className="sidebar-label">INDICATEUR AFFICHÉ</label>
                <ul className="indicator-list">
                    {OPTIONS.map(({ value, label }) => (
                        <li key={value}>
                            <button
                                className={`indicator-btn${selected === value ? ' active' : ''}`}
                                onClick={() => onChange(value)}
                            >
                                {label}
                            </button>
                        </li>
                    ))}
                </ul>
            </div>

            <div className="sidebar-section">
                <label className="sidebar-label">COUCHES</label>
                <label className="toggle-label">
                    <input
                        type="checkbox"
                        checked={showEspacesVerts}
                        onChange={onToggleEspacesVerts}
                    />
                    Espaces verts
                </label>
            </div>

            <div className="sidebar-legend">
                <span className="legend-label">Faible</span>
                <div className="legend-gradient" />
                <span className="legend-label">Élevé</span>
            </div>
        </aside>
    )
}
