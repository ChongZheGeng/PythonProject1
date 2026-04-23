import { SensorPoint } from '../types';

const colorMap = {
  应力: '#3366cc',
  位移: '#00a2ae',
  垂直度: '#8b5cf6',
  风速: '#f59e0b',
  加速度: '#10b981',
  温度: '#ef4444'
};

interface Props {
  points: SensorPoint[];
  onSelect?: (p: SensorPoint) => void;
  selectedId?: string;
}

export const TowerDiagram = ({ points, onSelect, selectedId }: Props) => (
  <div className="tower-diagram">
    <svg viewBox="0 0 900 500" className="tower-svg">
      <line x1="400" y1="420" x2="400" y2="90" stroke="#5f6f86" strokeWidth="12" />
      <line x1="400" y1="130" x2="670" y2="180" stroke="#76879e" strokeWidth="10" />
      <line x1="400" y1="130" x2="230" y2="190" stroke="#76879e" strokeWidth="10" />
      <rect x="350" y="420" width="100" height="26" fill="#8f9aa8" />
      {points.map((p) => (
        <g key={p.id} onClick={() => onSelect?.(p)} style={{ cursor: 'pointer' }}>
          <circle
            cx={p.position.x}
            cy={p.position.y}
            r={selectedId === p.id ? 14 : 10}
            fill={colorMap[p.type]}
            stroke="#fff"
            strokeWidth="2"
          />
          <text x={p.position.x + 12} y={p.position.y + 4} fontSize="13" fill="#1f324f">
            {p.id}
          </text>
        </g>
      ))}
    </svg>
  </div>
);
