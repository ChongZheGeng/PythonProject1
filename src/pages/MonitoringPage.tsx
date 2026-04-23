import { Button, Card, Col, DatePicker, Flex, Row, Select, Space, Statistic, Table, Tag } from 'antd';
import ReactECharts from 'echarts-for-react';
import { useMemo, useState } from 'react';
import { PanelCard } from '../components/PanelCard';
import { useRealtimeSeries } from '../hooks/useRealtimeSeries';
import { sensorPoints } from '../mock/data';

export const MonitoringPage = () => {
  const [selected, setSelected] = useState(sensorPoints[0]);
  const series = useRealtimeSeries(Array.from({ length: 50 }, (_, i) => 150 + Math.sin(i / 3) * 22), [80, 300], 1200);

  const spectrum = useMemo(() => Array.from({ length: 40 }, (_, i) => [i, Number((Math.random() * 10 + i * 0.05).toFixed(2))]), [selected.id]);

  const commonOption = (name: string, unit: string, data: number[]) => ({
    animation: false,
    xAxis: { type: 'category', data: data.map((_, i) => i) },
    yAxis: { type: 'value', name: unit },
    series: [{ name, type: 'line', data, smooth: true, showSymbol: false }],
    grid: { left: 40, right: 20, top: 20, bottom: 25 }
  });

  return (
    <Space direction="vertical" size={12} style={{ width: '100%' }}>
      <PanelCard title="监测参数筛选 / 工况切换">
        <Flex gap={10} wrap>
          <Select defaultValue="应力" options={['应力', '位移', '倾角', '风速', '加速度', '温度'].map((v) => ({ value: v }))} style={{ width: 140 }} />
          <DatePicker.RangePicker showTime />
          <Select defaultValue="动载" options={['静载', '动载', '回转', '变幅', '起升'].map((v) => ({ value: v }))} style={{ width: 140 }} />
          <Button type="primary">开始采集</Button>
          <Button>暂停采集</Button>
          <Button>清零</Button>
          <Button>导出数据</Button>
        </Flex>
      </PanelCard>

      <Row gutter={12}>
        <Col span={5}>
          <PanelCard title="测点列表">
            <Table
              size="small"
              pagination={false}
              rowKey="id"
              columns={[{ title: '测点', dataIndex: 'id' }, { title: '类型', dataIndex: 'type' }]}
              dataSource={sensorPoints}
              onRow={(record) => ({ onClick: () => setSelected(record) })}
            />
          </PanelCard>
        </Col>
        <Col span={7}>
          <PanelCard title={`实时数据 / ${selected.id} ${selected.name}`}>
            <Row gutter={[8, 8]}>
              <Col span={12}><Card><Statistic title="实时值" value={series.stats.realtime.toFixed(2)} suffix="MPa" /></Card></Col>
              <Col span={12}><Card><Statistic title="峰值" value={series.stats.peak.toFixed(2)} suffix="MPa" /></Card></Col>
              <Col span={12}><Card><Statistic title="均值" value={series.stats.mean.toFixed(2)} suffix="MPa" /></Card></Col>
              <Col span={12}><Card><Statistic title="RMS" value={series.stats.rms.toFixed(2)} suffix="MPa" /></Card></Col>
            </Row>
            <Tag color="green" style={{ marginTop: 12 }}>采样状态：正常采集</Tag>
          </PanelCard>
        </Col>
        <Col span={12}>
          <PanelCard title="波形图 / 频谱图 / 历史趋势">
            <ReactECharts option={commonOption('波形', '幅值', series.data)} style={{ height: 190 }} />
            <ReactECharts
              option={{
                animation: false,
                xAxis: { type: 'value', name: 'Hz' },
                yAxis: { type: 'value', name: 'dB' },
                series: [{ type: 'bar', data: spectrum }],
                grid: { left: 40, right: 20, top: 20, bottom: 25 }
              }}
              style={{ height: 190 }}
            />
            <ReactECharts option={commonOption('历史趋势', '幅值', series.data.map((v) => Number((v * 0.85).toFixed(2))))} style={{ height: 190 }} />
          </PanelCard>
        </Col>
      </Row>
    </Space>
  );
};
