import { useEffect, useState } from "react";
import { fetchSummary } from "../api/analytics";

const CARDS = [
  { key: "total_students", label: "Total Students", icon: "👩‍🎓" },
  { key: "avg_rating", label: "Avg Rating", icon: "⭐" },
  { key: "total_problems", label: "Total Problems", icon: "💡" },
  { key: "total_contests", label: "Total Contests", icon: "🏆" },
];

export default function SummaryCards() {
  const [data, setData] = useState(null);

  useEffect(() => {
    fetchSummary().then(setData).catch(console.error);
  }, []);

  if (!data) {
    return (
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {CARDS.map((c) => (
          <div
            key={c.key}
            className="bg-gray-800 rounded-xl p-5 animate-pulse h-24"
          />
        ))}
      </div>
    );
  }

  return (
    <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
      {CARDS.map((c) => (
        <div
          key={c.key}
          className="bg-gray-800 rounded-xl p-5 flex flex-col items-center justify-center"
        >
          <span className="text-2xl mb-1">{c.icon}</span>
          <span className="text-2xl font-bold text-white">
            {typeof data[c.key] === "number"
              ? data[c.key].toLocaleString()
              : data[c.key]}
          </span>
          <span className="text-sm text-gray-400 mt-1">{c.label}</span>
        </div>
      ))}
    </div>
  );
}
