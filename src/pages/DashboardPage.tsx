import { Alert, Col, List, Row, Space, Statistic, Tag, Typography, notification } from 'antd';
import { useEffect, useMemo } from 'react';
import { MetricCard } from '../components/MetricCard';
import { PanelCard } from '../components/PanelCard';
import { TowerDiagram } from '../components/TowerDiagram';
import { TrendChart } from '../components/TrendChart';
import { useRealtimeSeries } from '../hooks/useRealtimeSeries';
import { alarms, deviceInfo, logs, metricCards, sensorPoints } from '../mock/data';

export const DashboardPage = () => {
  const stress = useRealtimeSeries(Array.from({ length: 40 }, (_, i) => 180 + Math.sin(i / 4) * 30), [120, 280]);
  const disp = useRealtimeSeries(Array.from({ length: 40 }, (_, i) => 14 + Math.cos(i / 5) * 4), [8, 24]);
  const wind = useRealtimeSeries(Array.from({ length: 40 }, (_, i) => 8 + Math.sin(i / 3) * 4), [2, 18]);
  const acc = useRealtimeSeries(Array.from({ length: 40 }, (_, i) => 0.25 + Math.cos(i / 4) * 0.12), [0.05, 0.8]);

  useEffect(() => {
    const timer = window.setInterval(() => {
      if (Math.random() > 0.78) {
        notification.warning({
          message: '结构测试预警提示',
          description: '检测到测点动态响应接近阈值，请关注告警面板。',
          placement: 'topRight'
        });
      }
    }, 10000);
    return () => window.clearInterval(timer);
  }, []);

  const info = useMemo(
    () => [
      ['塔机编号', deviceInfo.craneId],
      ['项目名称', deviceInfo.projectName],
      ['工作状态', deviceInfo.status],
      ['当前工况', deviceInfo.condition],
      ['采样频率', deviceInfo.sampleRate],
      ['通信状态', deviceInfo.commStatus],
      ['时间', new Date().toLocaleString('zh-CN')]
    ],
    []
  );

  return (
    <Space direction="vertical" size={12} style={{ width: '100%' }}>
      <PanelCard title="设备状态总览 / Device Overview">
        <Row gutter={[16, 10]}>
          {info.map(([k, v]) => (
            <Col span={8} key={k}>
              <div className="info-item">
                <Typography.Text type="secondary">{k}</Typography.Text>
                <Typography.Text strong>{v}</Typography.Text>
              </div>
            </Col>
          ))}
        </Row>
      </PanelCard>

      <Row gutter={12}>
        <Col span={8}>
          <PanelCard title="塔机结构示意 / 测点定位">
            <TowerDiagram points={sensorPoints} />
          </PanelCard>
        </Col>
        <Col span={10}>
          <PanelCard title="关键指标 / Key Metrics">
            <Row gutter={[10, 10]}>
              {metricCards.map((m) => (
                <MetricCard metric={m} key={m.key} />
              ))}
            </Row>
          </PanelCard>
        </Col>
        <Col span={6}>
          <PanelCard title="告警面板 / Warning Panel">
            <Space direction="vertical" style={{ width: '100%' }}>
              <Statistic title="正常" value={24} valueStyle={{ color: '#2e9d4d' }} />
              <Statistic title="一级预警" value={7} valueStyle={{ color: '#f39c12' }} />
              <Statistic title="二级预警" value={2} valueStyle={{ color: '#d07a15' }} />
              <Statistic title="三级预警" value={1} valueStyle={{ color: '#d93a3a' }} />
              <List
                size="small"
                dataSource={alarms}
                renderItem={(item) => (
                  <List.Item>
                    <Tag color={item.level.includes('三级') ? 'red' : item.level.includes('二级') ? 'orange' : 'gold'}>{item.level}</Tag>
                    <div className="alarm-msg">{item.point}</div>
                  </List.Item>
                )}
              />
            </Space>
          </PanelCard>
        </Col>
      </Row>

      <Row gutter={12}>
        <Col span={12}><PanelCard title="应力时程曲线"><TrendChart title="应力" unit="MPa" data={stress.data} color="#2057a7" /></PanelCard></Col>
        <Col span={12}><PanelCard title="位移时程曲线"><TrendChart title="位移" unit="mm" data={disp.data} color="#368f8b" /></PanelCard></Col>
        <Col span={12}><PanelCard title="风速时程曲线"><TrendChart title="风速" unit="m/s" data={wind.data} color="#cc8b26" /></PanelCard></Col>
        <Col span={12}><PanelCard title="加速度时程曲线"><TrendChart title="加速度" unit="g" data={acc.data} color="#55a06f" /></PanelCard></Col>
      </Row>

      <PanelCard title="系统运行日志 / 测试日志">
        <div className="log-scroll">
          {logs.map((log) => (
            <Alert key={log} type="info" message={log} showIcon style={{ marginBottom: 6 }} />
          ))}
        </div>
      </PanelCard>
    </Space>
  );
};
