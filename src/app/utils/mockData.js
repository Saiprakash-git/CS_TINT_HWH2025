export const generateThreat = () => {
  const severities = ["Low", "Medium", "High", "Critical"];
  const types = ["Malware", "Phishing", "Ransomware", "CVE"];
  const countries = ["USA", "India", "Russia", "Germany", "China"];
  
  return {
    id: Math.random().toString(36).substr(2, 9),
    name: `Threat-${Math.floor(Math.random() * 1000)}`,
    type: types[Math.floor(Math.random() * types.length)],
    severity: severities[Math.floor(Math.random() * severities.length)],
    country: countries[Math.floor(Math.random() * countries.length)],
    detectedAt: new Date().toLocaleTimeString()
  };
};
