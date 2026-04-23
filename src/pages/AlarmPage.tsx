import { Card, Col, Descriptions, Modal, Row, Space, Statistic, Table, Timeline } from 'antd';
import { useState } from 'react';
import { PanelCard } from '../components/PanelCard';
import { alarms } from '../mock/data';
import { AlarmItem } from '../types';

export const AlarmPage = () => {
  const [current, setCurrent] = useState<AlarmItem | null>(null);

  return (
    <Space direction="vertical" style={{ width: '100%' }} size={12}>
      <Row gutter={12}>
        <Col span={6}><Card><Statistic title="一级预警" value={7} valueStyle={{ color: '#f0a22e' }} /></Card></Col>
        <Col span={6}><Card><Statistic title="二级预警" value={2} valueStyle={{ color: '#d67f1c' }} /></Card></Col>
        <Col span={6}><Card><Statistic title="三级预警" value={1} valueStyle={{ color: '#d93a3a' }} /></Card></Col>
        <Col span={6}><Card><Statistic title="累计告警" value={43} valueStyle={{ color: '#1f3e67' }} /></Card></Col>
      </Row>

      <Row gutter={12}>
        <Col span={8}>
          <PanelCard title="告警时间轴">
            <Timeline items={alarms.map((a) => ({ color: a.level.includes('三级') ? 'red' : 'orange', children: `${a.time} - ${a.point}` }))} />
          </PanelCard>
        </Col>
        <Col span={16}>
          <PanelCard title="告警列表">
            <Table
              rowKey="id"
              columns={[
                { title: '告警编号', dataIndex: 'id' },
                { title: '预警等级', dataIndex: 'level' },
                { title: '测点', dataIndex: 'point' },
                { title: '描述', dataIndex: 'message' },
                { title: '时间', dataIndex: 'time' }
              ]}
              dataSource={alarms}
              onRow={(record) => ({ onClick: () => setCurrent(record) })}
            />
          </PanelCard>
        </Col>
      </Row>

      <PanelCard title="诊断建议">
        <Row gutter={12}>
          {alarms.map((a) => (
            <Col span={8} key={a.id}><Card className="advice-card">{a.advice}</Card></Col>
          ))}
        </Row>
      </PanelCard>

      <Modal title="告警详情" open={!!current} onCancel={() => setCurrent(null)} footer={null}>
        {current && (
          <Descriptions column={1} bordered>
            <Descriptions.Item label="告警编号">{current.id}</Descriptions.Item>
            <Descriptions.Item label="预警等级">{current.level}</Descriptions.Item>
            <Descriptions.Item label="测点">{current.point}</Descriptions.Item>
            <Descriptions.Item label="告警描述">{current.message}</Descriptions.Item>
            <Descriptions.Item label="处理建议">{current.advice}</Descriptions.Item>
          </Descriptions>
        )}
      </Modal>
    </Space>
  );
};
