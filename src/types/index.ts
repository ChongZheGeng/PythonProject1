export type StatusLevel = 'normal' | 'warning' | 'danger';

export interface DeviceInfo {
  craneId: string;
  projectName: string;
  status: string;
  condition: string;
  sampleRate: string;
  commStatus: string;
}

export interface MetricCardData {
  key: string;
  title: string;
  value: string;
  unit: string;
  level: StatusLevel;
  desc: string;
}

export interface AlarmItem {
  id: string;
  level: '正常' | '一级预警' | '二级预警' | '三级预警';
  point: string;
  message: string;
  time: string;
  advice: string;
}

export interface SensorPoint {
  id: string;
  name: string;
  part: string;
  type: '应力' | '位移' | '垂直度' | '风速' | '加速度' | '温度';
  position: { x: number; y: number };
  status: StatusLevel;
  locationDesc: string;
}

export interface TrendSeries {
  name: string;
  unit: string;
  data: number[];
}
