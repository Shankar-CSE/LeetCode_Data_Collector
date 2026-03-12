const GROUP_OPTIONS = [
  { label: "Department", value: "DEPT" },
  { label: "Gender", value: "GENDER" },
  { label: "Batch", value: "BATCH" },
];

const METRIC_OPTIONS = [
  { label: "Problem Count", value: "Problem Count" },
  { label: "Contest Rating", value: "Contest Rating" },
  { label: "Contest Attended", value: "Contest Attended" },
  { label: "Easy", value: "Easy" },
  { label: "Medium", value: "medium" },
  { label: "Hard", value: "hard" },
];

const CHART_OPTIONS = [
  { label: "Bar", value: "bar" },
  { label: "Pie", value: "pie" },
];

export default function DropdownFilters({
  groupBy,
  setGroupBy,
  metric,
  setMetric,
  chartType,
  setChartType,
}) {
  const selectClass =
    "bg-gray-800 text-white border border-gray-600 rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-indigo-500";

  return (
    <div className="flex flex-wrap gap-4 items-center">
      <div>
        <label className="block text-sm text-gray-400 mb-1">Group By</label>
        <select
          className={selectClass}
          value={groupBy}
          onChange={(e) => setGroupBy(e.target.value)}
        >
          {GROUP_OPTIONS.map((o) => (
            <option key={o.value} value={o.value}>
              {o.label}
            </option>
          ))}
        </select>
      </div>

      <div>
        <label className="block text-sm text-gray-400 mb-1">Metric</label>
        <select
          className={selectClass}
          value={metric}
          onChange={(e) => setMetric(e.target.value)}
        >
          {METRIC_OPTIONS.map((o) => (
            <option key={o.value} value={o.value}>
              {o.label}
            </option>
          ))}
        </select>
      </div>

      <div>
        <label className="block text-sm text-gray-400 mb-1">Chart Type</label>
        <select
          className={selectClass}
          value={chartType}
          onChange={(e) => setChartType(e.target.value)}
        >
          {CHART_OPTIONS.map((o) => (
            <option key={o.value} value={o.value}>
              {o.label}
            </option>
          ))}
        </select>
      </div>
    </div>
  );
}
