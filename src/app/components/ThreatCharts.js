import { Pie } from "react-chartjs-2";
import { Chart as ChartJS, ArcElement, Tooltip, Legend } from "chart.js";
ChartJS.register(ArcElement, Tooltip, Legend);

export default function ThreatCharts({ threats }) {
  const severityCounts = threats.reduce((acc, t) => {
    acc[t.severity] = (acc[t.severity] || 0) + 1;
    return acc;
  }, {});

  const data = {
    labels: Object.keys(severityCounts),
    datasets: [
      {
        data: Object.values(severityCounts),
        backgroundColor: ["#facc15", "#fb923c", "#f87171", "#b91c1c"],
      },
    ],
  };

  return (
    <div className="bg-white p-4 rounded shadow mt-4 mb-4 overflow-x-auto h-120" >
      <h2 className="text-black text-xl font-semibold mb-2">Threat Severity Distribution</h2>
      <Pie data={data} />
    </div>
  );
}
