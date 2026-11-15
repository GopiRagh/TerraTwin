import { useEffect, useMemo, useState } from "react";
import L from "leaflet";
import { MapContainer, Marker, Popup, ScaleControl, TileLayer, useMap } from "react-leaflet";
import "leaflet/dist/leaflet.css";

const BASEMAPS = {
  satellite: {
    label: "Satellite imagery",
    url: "https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
    attribution: 'Tiles &copy; <a href="https://www.esri.com/">Esri</a> — Sources: Esri, Maxar, Earthstar Geographics, and the GIS User Community',
  },
  street: {
    label: "Street map",
    url: "https://tile.openstreetmap.org/{z}/{x}/{y}.png",
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
  },
};

function FitSites({ sites }) {
  const map = useMap();

  useEffect(() => {
    if (sites.length === 1) {
      map.setView(sites[0], 5, { animate: false });
    } else if (sites.length > 1) {
      map.fitBounds(L.latLngBounds(sites), { padding: [42, 42], maxZoom: 5, animate: false });
    }

    const frame = window.requestAnimationFrame(() => map.invalidateSize({ pan: false }));
    return () => window.cancelAnimationFrame(frame);
  }, [map, sites]);

  return null;
}

function markerIcon(score) {
  const matchClass = score == null ? "candidate" : score >= 90 ? "strong-match" : score >= 80 ? "good-match" : "low-match";
  return L.divIcon({
    className: `earth-analog-marker ${matchClass}`,
    html: '<span aria-hidden="true"><i></i></span>',
    iconSize: [22, 22],
    iconAnchor: [11, 11],
    popupAnchor: [0, -12],
  });
}

export default function AnalogMap({ id, candidates = [], results = [] }) {
  const [basemapMode, setBasemapMode] = useState("satellite");
  const [tileRetry, setTileRetry] = useState(0);
  const [tileWarning, setTileWarning] = useState("");
  const ranked = useMemo(() => new Map(results.map((result) => [result.location, result])), [results]);
  const sites = useMemo(() => candidates
    .filter((site) => Number.isFinite(site.coordinates?.latitude) && Number.isFinite(site.coordinates?.longitude))
    .map((site) => ({
      ...site,
      position: [site.coordinates.latitude, site.coordinates.longitude],
    })), [candidates]);
  const positions = useMemo(() => sites.map((site) => site.position), [sites]);
  const basemap = BASEMAPS[basemapMode];
  const handleTileError = () => {
    if (basemapMode === "satellite") {
      setBasemapMode("street");
      setTileWarning("Satellite imagery is unavailable, so the map switched to the street layer.");
      return;
    }
    setTileWarning("Map tiles could not be reached. The reference markers and coordinates are still shown.");
  };

  return (
    <div id={id} className="analog-map-shell" aria-label="Interactive map of Earth analog locations">
      <div className="analog-map-toolbar">
        <div className="analog-map-title"><strong>Earth analog sites</strong><span>{sites.length} mapped regions</span></div>
        <div className="map-layer-switch" role="group" aria-label="Map layer">
          <button type="button" className={basemapMode === "satellite" ? "active" : ""} aria-pressed={basemapMode === "satellite"} onClick={() => { setTileWarning(""); setBasemapMode("satellite"); }}>Satellite</button>
          <button type="button" className={basemapMode === "street" ? "active" : ""} aria-pressed={basemapMode === "street"} onClick={() => { setTileWarning(""); setBasemapMode("street"); }}>Street</button>
        </div>
      </div>
      <div className="analog-map-topline"><span>EARTH / WGS 84</span><span>Click a marker to inspect the site</span></div>
      {sites.length ? <MapContainer
        center={[15, 0]}
        zoom={2}
        minZoom={1}
        maxZoom={12}
        scrollWheelZoom={false}
        worldCopyJump
        className="analog-leaflet-map"
      >
        <TileLayer
          key={`${basemapMode}-${tileRetry}`}
          attribution={basemap.attribution}
          url={basemap.url}
          maxZoom={19}
          eventHandlers={{ error: handleTileError, load: () => setTileWarning("") }}
        />
        <ScaleControl position="bottomleft" imperial={false} />
        <FitSites sites={positions} />
        {sites.map((site) => {
          const result = ranked.get(site.location);
          return <Marker key={site.location} position={site.position} icon={markerIcon(result?.similarity_score)}>
            <Popup>
              <div className="analog-map-popup">
                <strong>{site.location}</strong>
                <span>{site.region_type || "Earth terrain region"}</span>
                <small>{site.coordinates.latitude.toFixed(3)}°, {site.coordinates.longitude.toFixed(3)}° · {site.radius_km ?? "—"} km sample</small>
                {result && <b>Rank {result.rank} · {result.similarity_score.toFixed(2)}% shape match</b>}
                <small>Source: {site.source || "Local elevation data"}</small>
              </div>
            </Popup>
          </Marker>;
        })}
      </MapContainer> : <div className="map-empty">No Earth locations with valid coordinates were returned.</div>}
      {tileWarning && <div className="map-tile-warning" role="status"><span>{tileWarning}</span><button type="button" onClick={() => { setTileWarning(""); if (basemapMode === "street") setBasemapMode("satellite"); setTileRetry((attempt) => attempt + 1); }}>TRY SATELLITE AGAIN</button></div>}
      <div className="analog-map-legend"><span><i className="legend-unranked" /> Reference location</span><span><i className="legend-ranked" /> Ranked analog</span><span>Drag to pan · Scroll or use controls to zoom</span></div>
    </div>
  );
}
