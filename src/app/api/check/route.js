// app/api/check/route.js
import { NextResponse } from 'next/server';

export async function GET(request) {
  const { searchParams } = new URL(request.url);
  const domain = searchParams.get('domain');

  return NextResponse.json({
    domain,
     technology: "Palo Alto Firewall",
    cve: "CVE-2024-3400",
    severity: "Critical",
    riskScore: 9.8,
    leadership: "Business at high risk, apply patch now.",
    analyst:
      "CVE-2024-3400 critical RCE in Palo Alto firewall used by your domain. IOCs linked to Lazarus campaign.",
    ops: "Patch firewall to version X.Y immediately.",
  });
}
