import { AlarmItem, DeviceInfo, MetricCardData, SensorPoint } from '../types';

export const deviceInfo: DeviceInfo = {
  craneId: 'TC-DZ-2026-018',
  projectName: '临港智造园区二期项目',
  status: '在线监测',
  condition: '动载-回转工况',
  sampleRate: '200 Hz',
  commStatus: '4G/光纤双链路正常'
};

export const metricCards: MetricCardData[] = [
  { key: 'stress', title: '起重臂根部应力', value: '238', unit: 'MPa', level: 'warning', desc: '结构应力' },
  { key: 'disp', title: '塔身顶部位移', value: '18.4', unit: 'mm', level: 'normal', desc: '挠度/位移' },
  { key: 'vertical', title: '塔身垂直度', value: '1.6‰', unit: '', level: 'normal', desc: '垂直度' },
  { key: 'wind', title: '风速', value: '14.2', unit: 'm/s', level: 'warning', desc: '环境风场' },
  { key: 'acc', title: '振动加速度', value: '0.42', unit: 'g', level: 'normal', desc: '动态响应' },
  { key: 'daq', title: '数据采集状态', value: '采集中', unit: '', level: 'normal', desc: '数据采集' }
];

export const alarms: AlarmItem[] = [
  {
    id: 'A-1001',
    level: '二级预警',
    point: 'S-01 起重臂根部应力',
    message: '应力连续120秒高于220MPa',
    time: '2026-04-23 09:45:12',
    advice: '建议检查当前吊重与幅度组合，降低瞬时冲击载荷。'
  },
  {
    id: 'A-1002',
    level: '一级预警',
    point: 'W-01 顶端风速',
    message: '风速接近阈值 15m/s',
    time: '2026-04-23 09:42:08',
    advice: '建议暂停高空吊装并观察阵风变化。'
  },
  {
    id: 'A-1003',
    level: '三级预警',
    point: 'V-01 塔身垂直度',
    message: '垂直度波动异常',
    time: '2026-04-23 09:35:56',
    advice: '建议复核结构连接状态及基础沉降数据。'
  }
];

export const sensorPoints: SensorPoint[] = [
  { id: 'S-01', name: '起重臂根部应力1', part: '起重臂铰接处', type: '应力', position: { x: 420, y: 230 }, status: 'warning', locationDesc: '主臂根部腹板外侧' },
  { id: 'S-02', name: '起重臂中段应力', part: '起重臂中段', type: '应力', position: { x: 560, y: 188 }, status: 'normal', locationDesc: '主臂中段下弦杆' },
  { id: 'D-01', name: '塔顶位移', part: '塔身顶部', type: '位移', position: { x: 410, y: 140 }, status: 'normal', locationDesc: '回转平台邻近基准点' },
  { id: 'V-01', name: '塔身垂直度', part: '塔身标准节', type: '垂直度', position: { x: 390, y: 280 }, status: 'danger', locationDesc: '中段标准节法兰连接处' },
  { id: 'W-01', name: '塔顶风速', part: '塔帽', type: '风速', position: { x: 450, y: 95 }, status: 'warning', locationDesc: '塔帽顶部风速仪安装座' },
  { id: 'A-01', name: '配重端加速度', part: '平衡臂', type: '加速度', position: { x: 290, y: 190 }, status: 'normal', locationDesc: '平衡臂中后段' },
  { id: 'T-01', name: '电控柜温度', part: '司机室下方', type: '温度', position: { x: 360, y: 235 }, status: 'normal', locationDesc: '电控柜内部环境测点' }
];

export const logs = [
  '09:46:12 采集任务#18 正常写入，缓存延时 42ms',
  '09:45:12 触发二级预警：S-01 起重臂根部应力偏高',
  '09:44:39 工况切换：动载 -> 回转',
  '09:43:15 信号处理模块：滤波参数组B生效',
  '09:42:08 触发一级预警：W-01 顶端风速接近阈值'
];
