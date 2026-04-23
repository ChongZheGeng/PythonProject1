import ReactECharts from 'echarts-for-react';

interface Props {
  title: string;
  unit: string;
  data: number[];
  color?: string;
}

export const TrendChart = ({ title, unit, data, color = '#2f6db5' }: Props) => {
  const option = {
    animation: false,
    grid: { left: 40, right: 20, top: 30, bottom: 30 },
    xAxis: {
      type: 'category',
      data: data.map((_, i) => `${i - data.length + 1}s`),
      axisLabel: { color: '#5c6f86' }
    },
    yAxis: { type: 'value', name: unit, axisLabel: { color: '#5c6f86' } },
    tooltip: { trigger: 'axis' },
    series: [{ data, type: 'line', smooth: true, showSymbol: false, lineStyle: { color, width: 2 } }]
  };

  return <ReactECharts option={option} style={{ height: 220 }} />;
};
