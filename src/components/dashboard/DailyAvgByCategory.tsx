import { Bar, BarChart, CartesianGrid, Cell, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";

import type { NamedValue } from "@/lib/dashboard";


const COLORS = ["hsl(155,43%,21%)", "hsl(38,92%,50%)", "hsl(200,70%,50%)", "hsl(270,60%,55%)", "hsl(0,84%,60%)", "hsl(160,60%,40%)", "hsl(30,80%,55%)"];


interface DailyAvgByCategoryProps {
  data: NamedValue[];
}


export default function DailyAvgByCategory({ data }: DailyAvgByCategoryProps) {
  if (!data.length) return null;

  return (
    <div className="chart-card">
      <h3 className="section-title">Daily Average Waste by Category</h3>
      <ResponsiveContainer width="100%" height={Math.max(200, data.length * 40)}>
        <BarChart data={data} layout="vertical" margin={{ top: 5, right: 20, bottom: 5, left: 130 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="hsl(220,13%,90%)" />
          <XAxis type="number" tick={{ fontSize: 11 }} unit=" kg" />
          <YAxis dataKey="name" type="category" tick={{ fontSize: 11 }} width={125} />
          <Tooltip
            contentStyle={{ fontSize: 12, borderRadius: 4 }}
            formatter={(v: number) => [`${v} kg/day`, "Avg Daily Waste"]}
          />
          <Bar dataKey="value" radius={[0, 3, 3, 0]}>
            {data.map((_, index) => (
              <Cell key={index} fill={COLORS[index % COLORS.length]} />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
