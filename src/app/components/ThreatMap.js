import { MapContainer, TileLayer, Marker, Popup } from "react-leaflet";
import "leaflet/dist/leaflet.css";

export default function ThreatMap({ threats }) {
  const positions = {
    USA: [37.0902, -95.7129],
    India: [20.5937, 78.9629],
    Russia: [61.5240, 105.3188],
    Germany: [51.1657, 10.4515],
    China: [35.8617, 104.1954],
  };

  return (
    <div className="bg-white  mt-4 mb-4 p-4 rounded shadow">
      <h2 className="text-black font-semibold mb-2">Global Threat Map</h2>
      <MapContainer center={[20, 0]} zoom={2} className="h-full w-full">
        <TileLayer url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" />
        {threats.map(threat => (
          <Marker key={threat.id} position={positions[threat.country]}>
            <Popup>
              <b>{threat.name}</b><br/>
              Type: {threat.type}<br/>
              Severity: {threat.severity}
            </Popup>
          </Marker>
        ))}
      </MapContainer>
    </div>
  );
}
