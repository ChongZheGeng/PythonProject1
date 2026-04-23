import { useEffect, useMemo, useState } from 'react';

const randomWalk = (arr: number[], range: [number, number], volatility: number) => {
  const last = arr[arr.length - 1] ?? (range[0] + range[1]) / 2;
  const next = Math.max(range[0], Math.min(range[1], last + (Math.random() - 0.5) * volatility));
  return [...arr.slice(1), Number(next.toFixed(2))];
};

export const useRealtimeSeries = (initial: number[], range: [number, number], refresh = 1500) => {
  const [data, setData] = useState<number[]>(initial);

  useEffect(() => {
    const timer = window.setInterval(() => {
      setData((prev) => randomWalk(prev, range, (range[1] - range[0]) * 0.12));
    }, refresh);
    return () => window.clearInterval(timer);
  }, [range, refresh]);

  const stats = useMemo(() => {
    const peak = Math.max(...data);
    const mean = data.reduce((a, b) => a + b, 0) / data.length;
    const rms = Math.sqrt(data.reduce((a, b) => a + b ** 2, 0) / data.length);
    return { realtime: data[data.length - 1], peak, mean, rms };
  }, [data]);

  return { data, stats };
};
