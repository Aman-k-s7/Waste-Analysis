import { Calendar, Scale, TrendingUp } from "lucide-react";
import {
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

import type { BainMarieAnalytics } from "@/lib/dashboard";


const COLORS = ["hsl(155,43%,21%)", "hsl(38,92%,50%)", "hsl(200,70%,50%)", "hsl(270,60%,55%)", "hsl(0,84%,60%)", "hsl(160,60%,40%)", "hsl(30,80%,55%)"];


interface BainMarieAnalyticsProps {
  data?: BainMarieAnalytics;
}


export default function BainMarieAnalyticsCard({ data }: BainMarieAnalyticsProps) {
  const kpis = [
    { label: "Total Bain Marie Waste", value: `${(data?.total_waste ?? 0).toLocaleString()} kg`, icon: Scale },
    { label: "Daily Average", value: `${(data?.daily_avg ?? 0).toLocaleString()} kg`, icon: TrendingUp },
    { label: "Active Days", value: (data?.active_days ?? 0).toString(), icon: Calendar },
  ];

  const topItems = (data?.top_food_items ?? []).slice(0, 7);

  return (
    <div className="chart-card space-y-4">
      <h3 className="section-title">Bain Marie Analytics</h3>

      <div className="grid grid-cols-3 gap-3">
        {kpis.map((kpi) => (
          <div key={kpi.label} className="bg-muted/40 rounded p-3 flex items-center gap-3">
            <kpi.icon className="h-4 w-4 text-primary shrink-0" />
            <div>
              <p className="text-xs text-muted-foreground">{kpi.label}</p>
              <p className="text-base font-bold text-foreground">{kpi.value}</p>
            </div>
          </div>
        ))}
      </div>

      <div className="grid grid-cols-2 gap-4">
        <div>
          <h4 className="text-sm font-medium text-foreground mb-2">Top Food Items</h4>
          <ResponsiveContainer width="100%" height={220}>
            <BarChart data={topItems} margin={{ top: 5, right: 10, bottom: 30, left: 0 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="hsl(220,13%,90%)" />
              <XAxis dataKey="name" tick={{ fontSize: 10 }} interval={0} angle={-20} textAnchor="end" height={60} />
              <YAxis tick={{ fontSize: 11 }} />
              <Tooltip contentStyle={{ fontSize: 12, borderRadius: 4 }} formatter={(v: number) => [`${v} kg`, "Waste"]} />
              <Bar dataKey="value" radius={[3, 3, 0, 0]}>
                {topItems.map((_, index) => (
                  <Cell key={index} fill={COLORS[index % COLORS.length]} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>

        <div>
          <h4 className="text-sm font-medium text-foreground mb-2">By Meal</h4>
          <ResponsiveContainer width="100%" height={220}>
            <BarChart data={data?.by_meal ?? []} margin={{ top: 5, right: 10, bottom: 5, left: 0 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="hsl(220,13%,90%)" />
              <XAxis dataKey="name" tick={{ fontSize: 11 }} />
              <YAxis tick={{ fontSize: 11 }} />
              <Tooltip contentStyle={{ fontSize: 12, borderRadius: 4 }} formatter={(v: number) => [`${v} kg`, "Waste"]} />
              <Bar dataKey="value" fill="hsl(38,92%,50%)" radius={[3, 3, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      <div>
        <h4 className="text-sm font-medium text-foreground mb-2">Daily Trend</h4>
        <ResponsiveContainer width="100%" height={160}>
          <LineChart data={data?.daily_trend ?? []} margin={{ top: 5, right: 20, bottom: 5, left: 0 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="hsl(220,13%,90%)" />
            <XAxis dataKey="date" tick={{ fontSize: 10 }} interval="preserveStartEnd" />
            <YAxis tick={{ fontSize: 11 }} />
            <Tooltip contentStyle={{ fontSize: 12, borderRadius: 4 }} formatter={(v: number) => [`${v} kg`, "Waste"]} />
            <Line type="monotone" dataKey="value" stroke="hsl(155,43%,21%)" strokeWidth={2} dot={false} />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
