import { Button, Drawer, Flex, Radio, Space, Tag, Typography } from 'antd';
import { useMemo, useState } from 'react';
import { PanelCard } from '../components/PanelCard';
import { TowerDiagram } from '../components/TowerDiagram';
import { sensorPoints } from '../mock/data';
import { SensorPoint } from '../types';

type FilterType = 'all' | '应力' | '位移' | '告警';

const colorMap: Record<SensorPoint['type'], string> = {
  应力: '#3366cc', 位移: '#00a2ae', 垂直度: '#8b5cf6', 风速: '#f59e0b', 加速度: '#10b981', 温度: '#ef4444'
};

export const SensorLayoutPage = () => {
  const [selected, setSelected] = useState<SensorPoint | null>(sensorPoints[0]);
  const [filter, setFilter] = useState<FilterType>('all');

  const points = useMemo(() => {
    if (filter === 'all') return sensorPoints;
    if (filter === '告警') return sensorPoints.filter((p) => p.status !== 'normal');
    return sensorPoints.filter((p) => p.type === filter);
  }, [filter]);

  return (
    <PanelCard
      title="测点布置 / Sensor Layout"
      extra={
        <Flex gap={8}>
          <Radio.Group value={filter} onChange={(e) => setFilter(e.target.value)}>
            <Radio.Button value="all">显示全部</Radio.Button>
            <Radio.Button value="应力">仅显示应力</Radio.Button>
            <Radio.Button value="位移">仅显示位移</Radio.Button>
            <Radio.Button value="告警">仅显示告警测点</Radio.Button>
          </Radio.Group>
        </Flex>
      }
    >
      <TowerDiagram points={points} selectedId={selected?.id} onSelect={setSelected} />
      <Space wrap style={{ marginTop: 8 }}>
        {Object.entries(colorMap).map(([name, color]) => (
          <Tag color={color} key={name}>{name}测点</Tag>
        ))}
      </Space>

      <Drawer title="测点详情" open={!!selected} onClose={() => setSelected(null)} width={360}>
        {selected && (
          <Space direction="vertical">
            <Typography.Text><b>测点编号：</b>{selected.id}</Typography.Text>
            <Typography.Text><b>测点名称：</b>{selected.name}</Typography.Text>
            <Typography.Text><b>所属部位：</b>{selected.part}</Typography.Text>
            <Typography.Text><b>传感器类型：</b>{selected.type}</Typography.Text>
            <Typography.Text><b>安装位置说明：</b>{selected.locationDesc}</Typography.Text>
            <Typography.Text><b>当前状态：</b>{selected.status === 'normal' ? '正常' : selected.status === 'warning' ? '预警' : '危险'}</Typography.Text>
            <Button type="primary">联动历史趋势</Button>
          </Space>
        )}
      </Drawer>
    </PanelCard>
  );
};
