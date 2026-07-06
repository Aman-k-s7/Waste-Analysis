import { AlertTriangle, Cpu, Leaf, Scale, ScanLine } from "lucide-react";

import type { DashboardSummary } from "@/lib/dashboard";


interface KpiStripProps {
  summary?: DashboardSummary;
}


export default function KpiStrip({ summary }: KpiStripProps) {
  const kpis = [
    { label: "Total Waste", value: `${(summary?.total_waste ?? 0).toLocaleString()} kg`, icon: Scale, color: "text-primary" },
    { label: "Total Scans", value: (summary?.total_scans ?? 0).toLocaleString(), icon: ScanLine, color: "text-primary" },
    { label: "Average Daily Waste", value: `${(summary?.average_daily_waste ?? 0).toLocaleString()} kg`, icon: Leaf, color: "text-primary" },
    { label: "Total Devices", value: (summary?.total_devices ?? 0).toString(), icon: Cpu, color: "text-primary" },
    { label: "Abnormal Days", value: (summary?.abnormal_days ?? 0).toString(), icon: AlertTriangle, color: "text-destructive" },
    { label: "Total CO₂e (kg)*", value: `${(summary?.co2_impact ?? 0).toLocaleString()} kg`, icon: Leaf, color: "text-accent" },
  ];

  return (
    <div className="space-y-4">
      <div className="grid grid-cols-2 lg:grid-cols-3 gap-4">
        {kpis.map((kpi) => (
          <div key={kpi.label} className="kpi-card flex items-center gap-4 py-5">
            <div className={`${kpi.color} shrink-0`}>
              <kpi.icon className="h-6 w-6" />
            </div>
            <div className="min-w-0">
              <p className="text-sm font-medium text-muted-foreground truncate">{kpi.label}</p>
              <p className="text-2xl font-bold leading-tight text-foreground mt-1">{kpi.value}</p>
            </div>
          </div>
        ))}
      </div>
      <p className="text-xs text-muted-foreground px-1">
        *CO₂e figures based on avg emission factors (1.75 kg CO₂e/kg food waste). Emission factors are applied based on procurement weight basis. Cooked weight is used as a conservative proxy. Cooking energy not included; values are indicative.
      </p>
    </div>
  );
}
