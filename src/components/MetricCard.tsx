import { Col, Statistic } from 'antd';
import { MetricCardData } from '../types';

const borderMap = {
  normal: '#79c26d',
  warning: '#f3ad3f',
  danger: '#de5757'
};

export const MetricCard = ({ metric }: { metric: MetricCardData }) => (
  <Col span={8}>
    <div className="metric-card" style={{ borderLeft: `4px solid ${borderMap[metric.level]}` }}>
      <div className="metric-title">{metric.title}</div>
      <Statistic value={metric.value} suffix={metric.unit} valueStyle={{ color: '#1b375f', fontSize: 24 }} />
      <div className="metric-desc">{metric.desc}</div>
    </div>
  </Col>
);
