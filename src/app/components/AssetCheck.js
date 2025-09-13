'use client'; // at the top of AssetCheck.js

import { useState } from "react";

export default function AssetCheck() {
  const [domain, setDomain] = useState("");
  const [data, setData] = useState(null);
  const [riskScore, setRiskScore] = useState(null);

  const handleCheck = async () => {
    const res = await fetch(`/api/check?domain=${domain}`);
    const json = await res.json();
    setData(json);
    setRiskScore(json.riskScore);
  };

  const simulateMitigation = () => {
    // reduce risk score
    setRiskScore(1.5); // mock safe score
  };

  return (
    <div className="mt-10 flex flex-col items-center">
      <h1 className="text-3xl font-bold mb-6">Asset Vulnerability Check</h1>

      <div className="flex gap-2 mb-6">
        <input
          className="px-4 py-2 rounded text-white bg-gray-800 border border-gray-600 focus:outline-none focus:border-blue-500"
          placeholder="Enter domain e.g. acmebank.com"
          value={domain}
          onChange={(e) => setDomain(e.target.value)}
        />
        <button
          onClick={handleCheck}
          className="bg-blue-600 hover:bg-blue-700 px-4 py-2 rounded"
        >
          Check
        </button>
      </div>

      {data && (
        <div className="w-full max-w-4xl bg-gray-800 rounded p-6">
          <h2 className="text-2xl font-semibold mb-4">Results for {domain}</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {/* Leadership */}
            <div className="bg-gray-700 p-4 rounded">
              <h3 className="font-bold text-lg mb-2">Leadership</h3>
              <p>{data.leadership}</p>
            </div>
            {/* Analyst */}
            <div className="bg-gray-700 p-4 rounded">
              <h3 className="font-bold text-lg mb-2">Analyst</h3>
              <p>{data.analyst}</p>
            </div>
            {/* Ops */}
            <div className="bg-gray-700 p-4 rounded">
              <h3 className="font-bold text-lg mb-2">Ops</h3>
              <p>{data.ops}</p>
            </div>
          </div>

          <div className="mt-6">
            <p className="text-xl">
              Current Risk Score:{" "}
              <span className="font-bold text-red-400">{riskScore}</span>
            </p>
            <button
              onClick={simulateMitigation}
              className="mt-4 bg-green-600 hover:bg-green-700 px-4 py-2 rounded"
            >
              Simulate Mitigation
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
