import { Button, Card, Col, Form, InputNumber, Row, Select, Space, Switch, message } from 'antd';
import { PanelCard } from '../components/PanelCard';

export const SettingsPage = () => {
  const [form] = Form.useForm();

  return (
    <Space direction="vertical" style={{ width: '100%' }} size={12}>
      <PanelCard title="阈值设置">
        <Form layout="vertical" form={form} initialValues={{ stress: 220, disp: 22, vertical: 2.2, wind: 15, acc: 0.6 }}>
          <Row gutter={12}>
            <Col span={8}><Form.Item label="应力预警阈值 (MPa)" name="stress"><InputNumber style={{ width: '100%' }} /></Form.Item></Col>
            <Col span={8}><Form.Item label="位移预警阈值 (mm)" name="disp"><InputNumber style={{ width: '100%' }} /></Form.Item></Col>
            <Col span={8}><Form.Item label="垂直度预警阈值 (‰)" name="vertical"><InputNumber style={{ width: '100%' }} /></Form.Item></Col>
            <Col span={8}><Form.Item label="风速预警阈值 (m/s)" name="wind"><InputNumber style={{ width: '100%' }} /></Form.Item></Col>
            <Col span={8}><Form.Item label="加速度预警阈值 (g)" name="acc"><InputNumber style={{ width: '100%' }} /></Form.Item></Col>
          </Row>
        </Form>
      </PanelCard>

      <Row gutter={12}>
        <Col span={12}>
          <PanelCard title="采样设置">
            <Form layout="vertical" initialValues={{ freq: 200, filter: true, refresh: 1500 }}>
              <Form.Item label="采样频率 (Hz)"><InputNumber style={{ width: '100%' }} /></Form.Item>
              <Form.Item label="滤波开关"><Switch defaultChecked /></Form.Item>
              <Form.Item label="数据刷新间隔 (ms)"><InputNumber style={{ width: '100%' }} /></Form.Item>
            </Form>
          </PanelCard>
        </Col>
        <Col span={12}>
          <PanelCard title="显示与通信设置">
            <Form layout="vertical" initialValues={{ theme: 'light', chart: 'smooth' }}>
              <Form.Item label="深浅主题切换"><Select options={[{ value: 'light', label: '浅色主题' }, { value: 'dark', label: '深色主题' }]} /></Form.Item>
              <Form.Item label="图表刷新方式"><Select options={[{ value: 'smooth', label: '平滑连续' }, { value: 'step', label: '步进刷新' }]} /></Form.Item>
              <Card size="small" title="通信状态设置">
                主链路：4G / 备链路：光纤 / 心跳间隔：5s / 丢包阈值：2%
              </Card>
            </Form>
          </PanelCard>
        </Col>
      </Row>

      <Button type="primary" onClick={() => message.success('参数已保存（前端Mock）')}>
        保存参数配置
      </Button>
    </Space>
  );
};
