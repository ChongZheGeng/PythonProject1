import { Card } from 'antd';
import { PropsWithChildren } from 'react';

interface PanelCardProps extends PropsWithChildren {
  title: string;
  extra?: React.ReactNode;
  className?: string;
}

export const PanelCard = ({ title, extra, children, className }: PanelCardProps) => (
  <Card className={`panel-card ${className ?? ''}`} title={title} extra={extra}>
    {children}
  </Card>
);
