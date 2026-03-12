import { useState, useEffect, useCallback } from "react";
import SummaryCards from "../components/SummaryCards";
import DropdownFilters from "../components/DropdownFilters";
import ChartViewer from "../components/ChartViewer";
import ScatterPlot from "../components/ScatterPlot";
import Leaderboard from "../components/Leaderboard";
import { fetchAnalytics } from "../api/analytics";

export default function Dashboard() {
  const [groupBy, setGroupBy] = useState("DEPT");
  const [metric, setMetric] = useState("Problem Count");
  const [chartType, setChartType] = useState("bar");
  const [chartData, setChartData] = useState(null);
  const [loading, setLoading] = useState(false);

  const loadChart = useCallback(() => {
    setLoading(true);
    fetchAnalytics(groupBy, metric)
      .then(setChartData)
      .catch(console.error)
      .finally(() => setLoading(false));
  }, [groupBy, metric]);

  useEffect(() => {
    loadChart();
  }, [loadChart]);

  return (
    <div className="min-h-screen bg-gray-900 text-white">
      <header className="border-b border-gray-800 px-6 py-4">
        <h1 className="text-2xl font-bold tracking-tight">
          📊 LeetCode Analytics Dashboard
        </h1>
      </header>

      <main className="max-w-7xl mx-auto px-4 py-6 space-y-6">
        {/* Summary Cards */}
        <SummaryCards />

        {/* Filters + Chart */}
        <section className="space-y-4">
          <DropdownFilters
            groupBy={groupBy}
            setGroupBy={setGroupBy}
            metric={metric}
            setMetric={setMetric}
            chartType={chartType}
            setChartType={setChartType}
          />

          {loading ? (
            <div className="bg-gray-800 rounded-xl p-8 text-center text-gray-400 animate-pulse">
              Loading chart…
            </div>
          ) : (
            <ChartViewer
              data={chartData}
              groupBy={groupBy}
              metric={metric}
              chartType={chartType}
            />
          )}
        </section>

        {/* Scatter Plot */}
        <ScatterPlot />

        {/* Leaderboard */}
        <Leaderboard />
      </main>
    </div>
  );
}
