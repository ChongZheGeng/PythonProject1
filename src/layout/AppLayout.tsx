import { DesktopOutlined, AlertOutlined, DashboardOutlined, SettingOutlined, AimOutlined } from '@ant-design/icons';
import { Layout, Menu, Typography } from 'antd';
import { useMemo } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';

const { Header, Content, Sider } = Layout;

const menuItems = [
  { key: '/', icon: <DashboardOutlined />, label: '总览 Dashboard' },
  { key: '/monitoring', icon: <DesktopOutlined />, label: '实时监测 Monitoring' },
  { key: '/sensor-layout', icon: <AimOutlined />, label: '测点布置 SensorLayout' },
  { key: '/alarm', icon: <AlertOutlined />, label: '预警与诊断 Alarm' },
  { key: '/settings', icon: <SettingOutlined />, label: '参数设置 Settings' }
];

export const AppLayout = ({ children }: { children: React.ReactNode }) => {
  const navigate = useNavigate();
  const location = useLocation();

  const selected = useMemo(() => {
    const target = menuItems.find((item) => location.pathname === item.key || location.pathname.startsWith(`${item.key}/`));
    return [target?.key ?? '/'];
  }, [location.pathname]);

  return (
    <Layout style={{ minHeight: '100vh' }}>
      <Sider theme="light" width={252} className="left-sider">
        <div className="logo-block">
          <Typography.Title level={5}>结构测试前面板</Typography.Title>
          <div>Virtual Instrument Console</div>
        </div>
        <Menu items={menuItems} mode="inline" selectedKeys={selected} onClick={(v) => navigate(v.key)} />
      </Sider>
      <Layout>
        <Header className="top-header">
          <Typography.Title level={3} style={{ margin: 0, color: '#163a68' }}>
            塔式起重机结构测试与安全监测系统
          </Typography.Title>
        </Header>
        <Content className="main-content">{children}</Content>
      </Layout>
    </Layout>
  );
};
