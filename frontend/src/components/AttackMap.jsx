import { MapContainer, TileLayer, Marker, Popup } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';
import L from 'leaflet';

// 1. Fix Leaflet's default icon issue in React
import icon from 'leaflet/dist/images/marker-icon.png';
import iconShadow from 'leaflet/dist/images/marker-shadow.png';
let DefaultIcon = L.icon({
    iconUrl: icon,
    shadowUrl: iconShadow,
    iconSize: [25, 41],
    iconAnchor: [12, 41]
});
L.Marker.prototype.options.icon = DefaultIcon;

// 2. Demo Locations (Hardcoded for Hackathon stability)
const locationMap = {
  "New York, USA": [40.7128, -74.0060],
  "Moscow, Russia": [55.7558, 37.6173],
  "Lagos, Nigeria": [6.5244, 3.3792],
  "Beijing, China": [39.9042, 116.4074],
  "Vellore, India": [12.9165, 79.1325], // Or your local city
};

const AttackMap = ({ logs }) => {
  // 3. Filter logs to only show ones we have coordinates for
  const markers = logs
    .filter(log => locationMap[log.location])
    .map(log => ({
      ...log,
      coords: locationMap[log.location]
    }));

  return (
    <MapContainer 
      center={[30, 0]} 
      zoom={1.5} 
      style={{ height: "100%", width: "100%", borderRadius: "12px", zIndex: 0 }}
      scrollWheelZoom={false} // Prevents getting stuck while scrolling page
    >
      {/* 4. Dark Mode "Cyber" Tiles */}
      <TileLayer
        url="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png"
        attribution='&copy; <a href="https://carto.com/attributions">CARTO</a>'
      />
      
      {markers.map((log) => (
        <Marker key={log.id} position={log.coords}>
          <Popup>
            <div style={{color: 'black', textAlign: 'center'}}>
                <strong>{log.reason}</strong><br/>
                IP: {log.ip}<br/>
                Risk: {(log.risk_score * 100).toFixed(0)}%
            </div>
          </Popup>
        </Marker>
      ))}
    </MapContainer>
  );
};

export default AttackMap;