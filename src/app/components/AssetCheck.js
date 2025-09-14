'use client';

import { useState } from "react";

export default function AssetCheck() {
  const [domain, setDomain] = useState("");
  const [data, setData] = useState(null);

  const handleCheck = async () => {
    try {
      const res = await fetch("http://127.0.0.1:8000/analyze", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ url: domain }),
      });
      const json = await res.json();
      setData(json);
    } catch (err) {
      console.error("Error calling API:", err);
    }
  };

  return (
    <div className="mt-10 flex flex-col items-center">
      <h1 className="text-3xl font-bold mb-6">Asset Vulnerability Check</h1>

      {/* Input + Button */}
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

      {/* Results */}
      {data && (
        <div className="w-full max-w-5xl bg-gray-800 rounded p-6 space-y-8">
          {/* ---- ML Analysis Section ---- */}
          <div>
            <h2 className="text-2xl font-semibold mb-4">ML Risk Analysis</h2>
            <p><strong>Status:</strong> {data.status}</p>
            <p>
              <strong>Overall Risk Score:</strong>{" "}
              <span className="font-bold text-red-400">
                {data.overall_risk_score}
              </span>
            </p>

            <h3 className="text-xl mt-4 mb-2">Technologies Detected:</h3>
            <ul className="list-disc pl-6">
              {data.technologies.map((t, i) => (
                <li key={i}>{t}</li>
              ))}
            </ul>

            <h3 className="text-xl mt-4 mb-2">Top Vulnerabilities:</h3>
            <table className="min-w-full text-sm text-left border-collapse">
              <thead>
                <tr className="bg-gray-700 text-white">
                  <th className="px-4 py-2">CVE</th>
                  <th className="px-4 py-2">Severity</th>
                  <th className="px-4 py-2">CVSS</th>
                  <th className="px-4 py-2">Exploitability</th>
                  <th className="px-4 py-2">Predicted Risk</th>
                </tr>
              </thead>
              <tbody>
                {data.vulnerabilities.map((v, i) => (
                  <tr key={i} className="bg-gray-600 text-white">
                    <td className="px-4 py-2">{v.cve_id}</td>
                    <td className="px-4 py-2">{v.severity}</td>
                    <td className="px-4 py-2">{v.cvss_score}</td>
                    <td className="px-4 py-2">{v.exploitability_score}</td>
                    <td className="px-4 py-2">{v.predicted_risk}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {/* ---- Page Scanner Section ---- */}
          <div>
            <h2 className="text-2xl font-semibold mb-4">Page Scanner Analysis</h2>
            <p><strong>Final URL:</strong> {data.page_scanner.final_url}</p>
            <p><strong>Verdict:</strong> {data.page_scanner.analysis.verdict}</p>
            <p><strong>Suspicion Score:</strong> {data.page_scanner.analysis.score}</p>

            <h3 className="text-xl mt-4 mb-2">Findings:</h3>
            <ul className="list-disc pl-6">
              {data.page_scanner.analysis.findings.map((f, i) => (
                <li key={i}>
                  <strong>{f.type}</strong>: {f.desc}
                </li>
              ))}
            </ul>

            <h3 className="text-xl mt-4 mb-2">Page Metrics:</h3>
            <ul className="list-disc pl-6">
              <li>Scripts: {data.page_scanner.analysis.page_metrics.num_scripts}</li>
              <li>Forms: {data.page_scanner.analysis.page_metrics.num_forms}</li>
              <li>Iframes: {data.page_scanner.analysis.page_metrics.num_iframes}</li>
              <li>Links: {data.page_scanner.analysis.page_metrics.num_links}</li>
            </ul>
          </div>
        </div>
      )}
    </div>
  );
}