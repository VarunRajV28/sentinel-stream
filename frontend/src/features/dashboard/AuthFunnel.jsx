import { ShieldCheck, ShieldAlert, Activity } from "lucide-react";
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip } from "recharts";

const COLORS = ["#10b981", "#f43f5e"]; // emerald-500, rose-500

export default function AuthFunnel({ authData }) {
  const { success = 0, failed = 0, total = 0, failure_rate = 0 } = authData || {};

  const chartData = [
    { name: "Success", value: success },
    { name: "Failed", value: failed },
  ];

  return (
    <div className="h-full flex flex-col rounded-lg border border-slate-800 bg-slate-900/60 glow-blue">
      {/* Header */}
      <div className="shrink-0 flex items-center gap-2 px-4 py-3 border-b border-slate-800">
        <Activity className="w-4 h-4 text-emerald-400" />
        <h2 className="text-sm font-semibold text-slate-200 tracking-wide uppercase">
          Authentication Health
        </h2>
      </div>

      {/* Content */}
      <div className="flex-1 flex flex-col p-4">
        {/* Chart + Stats Row */}
        <div className="flex-1 flex flex-col sm:flex-row items-center gap-6">
          {/* Pie Chart */}
          <div className="w-full sm:w-1/2 h-40 sm:h-48 flex items-center justify-center relative">
            {total > 0 ? (
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={chartData}
                    cx="50%"
                    cy="50%"
                    innerRadius={40}
                    outerRadius={65}
                    paddingAngle={5}
                    dataKey="value"
                    stroke="none"
                    animationDuration={1000}
                  >
                    {chartData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                    ))}
                  </Pie>
                  <Tooltip 
                    contentStyle={{ backgroundColor: '#1e293b', border: '1px solid #334155', borderRadius: '4px', fontSize: '10px' }}
                    itemStyle={{ color: '#f8fafc', padding: '2px 0' }}
                    cursor={{ fill: 'transparent' }}
                  />
                </PieChart>
              </ResponsiveContainer>
            ) : (
              <div className="text-slate-600 text-[10px] font-mono border border-dashed border-slate-800 rounded-full w-24 h-24 flex items-center justify-center text-center px-2">
                No Activity
              </div>
            )}
          </div>

          {/* Counts Column */}
          <div className="w-full sm:w-1/2 space-y-3">
            {/* Successes */}
            <div className="p-3 rounded-lg bg-emerald-500/5 border border-emerald-500/10">
              <div className="flex items-center gap-2 mb-1">
                <ShieldCheck className="w-3.5 h-3.5 text-emerald-500" />
                <span className="text-[10px] text-slate-400 font-mono uppercase tracking-wider">Successful</span>
              </div>
              <div className="text-xl font-mono text-emerald-400 font-bold">
                {success.toLocaleString()}
              </div>
            </div>

            {/* Failures */}
            <div className="p-3 rounded-lg bg-rose-500/5 border border-rose-500/10">
              <div className="flex items-center gap-2 mb-1">
                <ShieldAlert className="w-3.5 h-3.5 text-rose-500" />
                <span className="text-[10px] text-slate-400 font-mono uppercase tracking-wider">Failed</span>
              </div>
              <div className="text-xl font-mono text-rose-400 font-bold">
                {failed.toLocaleString()}
              </div>
            </div>
          </div>
        </div>

        {/* Footer Summary */}
        <div className="mt-4 pt-4 border-t border-slate-800/50">
          <div className="flex justify-between items-center mb-2">
            <span className="text-[10px] text-slate-500 font-mono uppercase">Avg Failure Rate</span>
            <span className="text-xs font-mono text-rose-400 font-bold">{failure_rate}%</span>
          </div>
          <div className="h-1.5 w-full bg-slate-800 rounded-full overflow-hidden">
            <div 
              className="h-full bg-rose-500 transition-all duration-700"
              style={{ width: `${Math.min(failure_rate, 100)}%` }}
            />
          </div>
          <div className="mt-2 flex justify-between text-[10px] text-slate-500 font-mono">
             <span>TOTAL ATTEMPTS</span>
             <span className="text-slate-300 font-bold">{total.toLocaleString()}</span>
          </div>
        </div>
      </div>
    </div>
  );
}
