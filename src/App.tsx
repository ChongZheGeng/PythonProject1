import { Navigate, Route, Routes } from 'react-router-dom';
import { AppLayout } from './layout/AppLayout';
import { AlarmPage } from './pages/AlarmPage';
import { DashboardPage } from './pages/DashboardPage';
import { MonitoringPage } from './pages/MonitoringPage';
import { SensorLayoutPage } from './pages/SensorLayoutPage';
import { SettingsPage } from './pages/SettingsPage';

export const App = () => (
  <AppLayout>
    <Routes>
      <Route path="/" element={<DashboardPage />} />
      <Route path="/monitoring" element={<MonitoringPage />} />
      <Route path="/sensor-layout" element={<SensorLayoutPage />} />
      <Route path="/alarm" element={<AlarmPage />} />
      <Route path="/settings" element={<SettingsPage />} />
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  </AppLayout>
);
