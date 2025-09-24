"use client";

import { useEffect, useMemo, useState } from "react";
import dynamic from "next/dynamic";
import type { Feature, Point } from "geojson";
import type { LatLngBounds } from "leaflet";
import L from "leaflet";
import "leaflet/dist/leaflet.css";
import supercluster from "supercluster";
import type { JobHit } from "../types";

const MapContainer = dynamic(() => import("react-leaflet").then((mod) => mod.MapContainer), {
  ssr: false,
});
const TileLayer = dynamic(() => import("react-leaflet").then((mod) => mod.TileLayer), {
  ssr: false,
});
const Marker = dynamic(() => import("react-leaflet").then((mod) => mod.Marker), {
  ssr: false,
});
const Popup = dynamic(() => import("react-leaflet").then((mod) => mod.Popup), {
  ssr: false,
});
const CircleMarker = dynamic(
  () => import("react-leaflet").then((mod) => mod.CircleMarker),
  { ssr: false }
);

if (typeof window !== "undefined") {
  L.Icon.Default.mergeOptions({
    iconUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png",
    iconRetinaUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png",
    shadowUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png",
  });
}

interface JobMapProps {
  jobs: JobHit[];
  center: [number, number];
  zoom: number;
}

type ClusterPointProperties = {
  cluster: boolean;
  jobId?: string;
  job?: JobHit;
  point_count?: number;
  cluster_id?: number;
};

type GeoFeature = Feature<Point, ClusterPointProperties>;

type ClusterIndex = supercluster.Supercluster<ClusterPointProperties, ClusterPointProperties>;

interface MapEventsProps {
  onChange(bounds: LatLngBounds, zoom: number): void;
}

const MapEvents = dynamic(
  async () => {
    const { useMapEvents } = await import("react-leaflet");
    return ({ onChange }: MapEventsProps) => {
      const map = useMapEvents({
        moveend: () => onChange(map.getBounds(), map.getZoom()),
        zoomend: () => onChange(map.getBounds(), map.getZoom()),
      });
      useEffect(() => {
        onChange(map.getBounds(), map.getZoom());
      }, [map, onChange]);
      return null;
    };
  },
  { ssr: false }
);

export function JobMap({ jobs, center, zoom }: JobMapProps) {
  const [bounds, setBounds] = useState<LatLngBounds | null>(null);
  const [currentZoom, setCurrentZoom] = useState(zoom);

  const points = useMemo<GeoFeature[]>(
    () =>
      jobs
        .filter((job) => job.location?.latitude && job.location?.longitude)
        .map((job) => ({
          type: "Feature" as const,
          properties: {
            cluster: false,
            jobId: job.id,
            job,
          },
          geometry: {
            type: "Point" as const,
            coordinates: [job.location!.longitude!, job.location!.latitude!],
          },
        })),
    [jobs]
  );

  const clusterIndex = useMemo<ClusterIndex | null>(() => {
    if (!points.length) return null;
    const index = new supercluster<ClusterPointProperties>({
      radius: 60,
      maxZoom: 17,
    });
    index.load(points);
    return index;
  }, [points]);

  const clusters = useMemo(() => {
    if (!clusterIndex || !bounds) {
      return points;
    }
    const bbox: [number, number, number, number] = [
      bounds.getWest(),
      bounds.getSouth(),
      bounds.getEast(),
      bounds.getNorth(),
    ];
    return clusterIndex.getClusters(bbox, Math.round(currentZoom));
  }, [clusterIndex, bounds, currentZoom, points]);

  const handleChange = (nextBounds: LatLngBounds, nextZoom: number) => {
    setBounds(nextBounds);
    setCurrentZoom(nextZoom);
  };

  return (
    <MapContainer
      center={center}
      zoom={zoom}
      className="job-map-container"
      minZoom={2}
      scrollWheelZoom
    >
      <MapEvents onChange={handleChange} />
      <TileLayer
        attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
      />
      {clusters.map((cluster) => {
        const [longitude, latitude] = cluster.geometry.coordinates;
        const properties = cluster.properties;
        if (properties.cluster) {
          const count = properties.point_count ?? 0;
          const size = 40 + (count / (jobs.length || 1)) * 40;
          return (
            <CircleMarker
              key={`cluster-${properties.cluster_id}`}
              center={[latitude, longitude]}
              radius={Math.max(20, size / 4)}
              pathOptions={{ color: "#2563eb", fillColor: "#60a5fa", fillOpacity: 0.7 }}
            >
              <Popup>
                <strong>{count} opportunities</strong>
                <p>Zoom in to see more detail.</p>
              </Popup>
            </CircleMarker>
          );
        }

        const job = properties.job;
        if (!job) return null;
        return (
          <Marker key={job.id} position={[latitude, longitude]}>
            <Popup>
              <div className="map-popup">
                <h3>{job.title}</h3>
                {job.metadata?.company && <p>{job.metadata.company}</p>}
                {job.location?.city && (
                  <p>
                    {job.location.city}
                    {job.location.region ? `, ${job.location.region}` : ""}
                  </p>
                )}
              </div>
            </Popup>
          </Marker>
        );
      })}
    </MapContainer>
  );
}
