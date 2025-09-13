'use client';

import { useState, useEffect } from 'react';
import ThreatFeed from './components/ThreatFeed';
import dynamic from 'next/dynamic';

const AssetCheck = dynamic(() => import('./components/AssetCheck'), {
  ssr: false,
});

export default function Dashboard() {
  const [threats, setThreats] = useState([]);
  const [loading, setLoading] = useState(true);

  async function fetchThreats() {
    try {
      const res = await fetch('/api/threats');
      const json = await res.json();
      if (json.threats) setThreats(json.threats);
    } catch (err) {
      console.error('Error fetching threats:', err);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    fetchThreats(); // initial load
    const interval = setInterval(fetchThreats, 60000); // refresh every 60s
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="p-4 bg-gray-900 min-h-screen text-white">
      <h1 className="text-2xl font-bold mb-4">Real-Time Threat Dashboard</h1>
      <AssetCheck />
      {loading ? (
        <p>Loading threats...</p>
      ) : (
        <ThreatFeed threats={threats} />
      )}
    </div>
  );
}
