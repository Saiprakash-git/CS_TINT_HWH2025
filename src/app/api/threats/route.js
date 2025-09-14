// app/api/threats/route.js
import { NextResponse } from 'next/server';

export async function GET() {
  try {
    // compute time window for newest CVEs (last 24 hours)
    const now = new Date().toISOString();
    const last24Hours = new Date(Date.now() - 24 * 60 * 60 * 1000).toISOString();

    const url = `https://services.nvd.nist.gov/rest/json/cves/2.0?resultsPerPage=20&lastModStartDate=${last24Hours}&lastModEndDate=${now}`;

    const res = await fetch(url, { cache: 'no-store' }); // disable cache in Vercel edge
    if (!res.ok) throw new Error('NVD fetch failed');

    const data = await res.json();

    const threats = (data.vulnerabilities || []).map((v) => ({
      id: v.cve.id,
      description: v.cve.descriptions?.[0]?.value || '',
      severity:
        v.cve.metrics?.cvssMetricV31?.[0]?.cvssData?.baseSeverity ||
        'Unknown',
      published: v.cve.published,
    }));

    return NextResponse.json({ threats });
  } catch (err) {
    console.error(err);
    return NextResponse.json(
      { threats: [], error: err.message },
      { status: 500 }
    );
  }
}
