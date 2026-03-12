import Plot from "react-plotly.js";

export default function ChartViewer({ data, groupBy, metric, chartType }) {
  if (!data || data.length === 0) {
    return (
      <div className="bg-gray-800 rounded-xl p-8 text-center text-gray-400">
        No data available
      </div>
    );
  }

  const groups = data.map((d) => d.group);
  const values = data.map((d) => d.value);

  const LABEL_MAP = {
    DEPT: "Department",
    GENDER: "Gender",
    BATCH: "Batch",
  };

  const title = `${metric} by ${LABEL_MAP[groupBy] || groupBy}`;

  let plotData;
  if (chartType === "pie") {
    plotData = [
      {
        labels: groups,
        values,
        type: "pie",
        hole: 0.4,
        textinfo: "label+percent",
        marker: {
          colors: groups.map(
            (_, i) =>
              `hsl(${(i * 360) / groups.length}, 70%, 55%)`
          ),
        },
      },
    ];
  } else {
    plotData = [
      {
        x: groups,
        y: values,
        type: "bar",
        marker: {
          color: groups.map(
            (_, i) =>
              `hsl(${(i * 360) / groups.length}, 70%, 55%)`
          ),
          cornerradius: 6,
        },
      },
    ];
  }

  return (
    <div className="bg-gray-800 rounded-xl p-4">
      <Plot
        data={plotData}
        layout={{
          title: { text: title, font: { color: "#e5e7eb", size: 18 } },
          paper_bgcolor: "transparent",
          plot_bgcolor: "transparent",
          font: { color: "#9ca3af" },
          xaxis: { gridcolor: "#374151" },
          yaxis: { gridcolor: "#374151" },
          margin: { t: 50, b: 60, l: 60, r: 30 },
        }}
        useResizeHandler
        className="w-full"
        style={{ width: "100%", height: 420 }}
        config={{ responsive: true, displayModeBar: false }}
      />
    </div>
  );
}
