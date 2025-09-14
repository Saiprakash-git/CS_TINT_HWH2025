export default function ThreatFeed({ threats }) {
  return (
    <div >
      <h2 className="text-2xl font-bold mt-4 mb-4 text-gray-200">Threat Feed</h2>
      <div className="overflow-x-auto text-black border-0 rounded-lg">
        <table className="min-w-full text-sm text-left border-collapse">
          <thead>
            <tr className="bg-gray-100  uppercase text-xs">
              <th className="px-4 py-3">Name</th>
              <th className="px-4 py-3">Type</th>
              <th className="px-4 py-3">Severity</th>
              <th className="px-4 py-3">Country</th>
              <th className="px-4 py-3">Detected</th>
            </tr>
          </thead>
          <tbody>
            {threats.map((threat, idx) => (
              <tr
                key={threat.id}
                className={`border-b last:border-none hover:bg-gray-200 transition-colors ${
                  idx % 2 === 0 ? "bg-white" : "bg-gray-50"
                }`}
              >
                <td className="px-4 py-2 font-medium">{threat.name}</td>
                <td className="px-4 py-2">{threat.type}</td>
                <td className="px-4 py-2">
                  <span
                    className={`px-2 py-1 rounded-full text-xs font-semibold 
                      ${
                        threat.severity === "Critical"
                          ? "bg-red-100 text-red-700"
                          : threat.severity === "High"
                          ? "bg-orange-100 text-orange-700"
                          : threat.severity === "Medium"
                          ? "bg-yellow-100 text-yellow-700"
                          : "bg-green-100 text-green-700"
                      }`}
                  >
                    {threat.severity}
                  </span>
                </td>
                <td className="px-4 py-2">{threat.country}</td>
                <td className="px-4 py-2">{threat.detectedAt}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
