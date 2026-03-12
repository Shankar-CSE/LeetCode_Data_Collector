import { useEffect, useState } from "react";
import { fetchLeaderboard } from "../api/analytics";

export default function Leaderboard() {
  const [rows, setRows] = useState(null);

  useEffect(() => {
    fetchLeaderboard().then(setRows).catch(console.error);
  }, []);

  if (!rows) {
    return (
      <div className="bg-gray-800 rounded-xl p-6 animate-pulse h-64" />
    );
  }

  return (
    <div className="bg-gray-800 rounded-xl p-4 overflow-x-auto">
      <h2 className="text-lg font-semibold text-white mb-3">
        🏅 Top 50 Leaderboard
      </h2>
      <table className="w-full text-sm text-left">
        <thead>
          <tr className="text-gray-400 border-b border-gray-700">
            <th className="py-2 px-3">#</th>
            <th className="py-2 px-3">Name</th>
            <th className="py-2 px-3">Roll No</th>
            <th className="py-2 px-3">Dept</th>
            <th className="py-2 px-3 text-right">Problems</th>
            <th className="py-2 px-3 text-right">Rating</th>
          </tr>
        </thead>
        <tbody>
          {rows.map((r, i) => (
            <tr
              key={r["Roll No"]}
              className="border-b border-gray-700/50 hover:bg-gray-700/40 transition-colors"
            >
              <td className="py-2 px-3 text-gray-400">{i + 1}</td>
              <td className="py-2 px-3 text-white font-medium">{r.Name}</td>
              <td className="py-2 px-3 text-gray-300">{r["Roll No"]}</td>
              <td className="py-2 px-3 text-gray-300">{r.DEPT}</td>
              <td className="py-2 px-3 text-right text-indigo-400 font-semibold">
                {r["Problem Count"]}
              </td>
              <td className="py-2 px-3 text-right text-amber-400 font-semibold">
                {typeof r["Contest Rating"] === "number"
                  ? r["Contest Rating"].toFixed(1)
                  : r["Contest Rating"] || "—"}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
