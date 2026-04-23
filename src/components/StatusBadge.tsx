import { Badge } from 'antd';
import { StatusLevel } from '../types';

const colorMap: Record<StatusLevel, string> = {
  normal: '#2e9d4d',
  warning: '#f39c12',
  danger: '#d93a3a'
};

const textMap: Record<StatusLevel, string> = {
  normal: '正常',
  warning: '预警',
  danger: '危险'
};

export const StatusBadge = ({ level }: { level: StatusLevel }) => (
  <Badge color={colorMap[level]} text={textMap[level]} />
);
