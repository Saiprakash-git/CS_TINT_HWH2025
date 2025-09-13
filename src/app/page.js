"use client"; 
import { useState, useEffect } from "react";
import ThreatFeed from "./components/ThreatFeed";

import dynamic from 'next/dynamic';
const AssetCheck = dynamic(() => import('./components/AssetCheck'), { ssr: false });

import { generateThreat } from "./utils/mockData";

export default function Dashboard() {
  const [threats, setThreats] = useState([]);

  useEffect(() => {
    const interval = setInterval(() => {
      setThreats(prev => [generateThreat(), ...prev].slice(0, 20)); // Keep last 20 threats
    }, 3000); // new threat every 3s

    return () => clearInterval(interval);
  }, []);

  return (
    <div className="p-4">
      <h1 className="text-2xl font-bold mb-4">Real-Time Threat Dashboard</h1>
      <div >
        <AssetCheck />
        <ThreatFeed threats={threats} />
        
      </div>
    </div>
  );
}
