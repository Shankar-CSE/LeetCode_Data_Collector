import { useEffect, useState } from "react";
import Plot from "react-plotly.js";
import { fetchScatter } from "../api/analytics";

export default function ScatterPlot() {
  const [data, setData] = useState(null);

  useEffect(() => {
    fetchScatter().then(setData).catch(console.error);
  }, []);

  if (!data) {
    return (
      <div className="bg-gray-800 rounded-xl p-6 animate-pulse h-64" />
    );
  }

  return (
    <div className="bg-gray-800 rounded-xl p-4">
      <Plot
        data={[
          {
            x: data.map((d) => d["Problem Count"]),
            y: data.map((d) => d["Contest Rating"]),
            text: data.map((d) => d.Name),
            mode: "markers",
            type: "scatter",
            marker: {
              size: 6,
              color: data.map((d) => d["Problem Count"]),
              colorscale: "Viridis",
              showscale: true,
              colorbar: { title: "Problems", font: { color: "#9ca3af" } },
            },
          },
        ]}
        layout={{
          title: {
            text: "Practice vs Performance",
            font: { color: "#e5e7eb", size: 18 },
          },
          xaxis: {
            title: "Problem Count",
            gridcolor: "#374151",
            color: "#9ca3af",
          },
          yaxis: {
            title: "Contest Rating",
            gridcolor: "#374151",
            color: "#9ca3af",
          },
          paper_bgcolor: "transparent",
          plot_bgcolor: "transparent",
          font: { color: "#9ca3af" },
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
