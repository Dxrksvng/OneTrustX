import { text } from "../i18n";
import { useState } from "react";
import {
  ArrowUpRight,
  Plane,
  ShieldCheck,
  Users,
  ZoomIn,
  ZoomOut,
  MoveUpRight,
} from "lucide-react";

type Point = {
  horizon: number;
  predicted_wait_min: number | null;
  lower_bound: number;
  upper_bound: number | null;
  queue_length: number;
  risk_level: string;
  confidence: number;
};
type Checkpoint = {
  id: string;
  name: string;
  current_wait: number | null;
  queue: number;
  open_lanes: number;
  forecast: Point[];
};
export default function AirportMap({
  checkpoints,
  horizon,
  gate,
  onCompare,
}: {
  checkpoints: Checkpoint[];
  horizon: number;
  gate: string;
  onCompare: () => void;
}) {
  const [selected, setSelected] = useState("security-a");
  const [zoom, setZoom] = useState(false);
  const active = checkpoints.find((c) => c.id === selected)!;
  const point = active.forecast.find((p) => p.horizon === (horizon || 15))!;
  const selectedWait = horizon ? point.predicted_wait_min : active.current_wait;
  return (
    <div className="airport-scene">
      <div className="scene-topline">
        <span>
          <i />
          {text(" T1 · DEPARTURES ")}
        </span>
        <span>{text("ILLUSTRATIVE DIGITAL TWIN")}</span>
      </div>
      <div className={"airport-canvas " + (zoom ? "zoomed" : "")}>
        <svg
          className="terminal-blueprint spatial-routes"
          viewBox="0 0 800 390"
          role="img"
          aria-label={text(
            "Illustrative routes through Security A and Security B toward the gate; background is AI-generated and not a surveyed airport",
          )}
        >
          <path
            className="flow-route alternate"
            d="M178 300 C220 290 230 180 280 170 S490 90 540 70"
            fill="none"
            stroke="#164e7a"
            strokeWidth="3"
            strokeDasharray="5 6"
          />
          <path
            className="flow-route"
            d="M178 300 C270 335 465 300 520 250 S580 120 540 70"
            fill="none"
            stroke="#5288ae"
            strokeWidth="3"
            strokeDasharray="5 6"
          />
          <path
            d="M90 65 L90 150 L178 300 M540 70 L655 70 L690 145"
            fill="none"
            stroke="#164e7a"
            strokeWidth="2"
          />
          {[
            { x: 90, y: 65, label: "Check-in" },
            { x: 50, y: 150, label: "Bag Drop" },
            { x: 740, y: 70, label: "Immigration" },
            { x: 690, y: 145, label: "Concourse" },
          ].map((node) => (
            <g key={node.label}>
              <rect
                x={node.x - 48}
                y={node.y - 13}
                width="96"
                height="26"
                rx="3"
                fill="#0d2942"
              />
              <text
                x={node.x}
                y={node.y + 4}
                textAnchor="middle"
                fill="white"
                fontSize="11"
              >
                {text(node.label)}
              </text>
            </g>
          ))}
          <circle
            className="location-ring"
            cx="178"
            cy="300"
            r="8"
            fill="white"
            stroke="#164e7a"
            strokeWidth="3"
          />
        </svg>
        {text(
          checkpoints.map((cp, index) => {
            const f = cp.forecast.find((p) => p.horizon === (horizon || 15))!;
            const wait = horizon ? f.predicted_wait_min : cp.current_wait;
            const risk = horizon
              ? f.risk_level
              : wait === null
                ? "RED"
                : wait >= 10
                  ? "YELLOW"
                  : "GREEN";
            return (
              <button
                key={cp.id}
                aria-pressed={selected === cp.id}
                aria-label={`Inspect ${cp.name}`}
                onClick={() => setSelected(cp.id)}
                className={`map-checkpoint checkpoint-${index} ${risk.toLowerCase()} ${selected === cp.id ? "is-selected" : ""}`}
              >
                <div className="map-checkpoint-label">
                  <ShieldCheck size={13} />
                  {text(cp.name)}
                  <span className="checkpoint-light" />
                </div>
                <strong key={`${horizon}-${wait}`}>
                  {text(wait === null ? "Closed" : Math.round(wait))}
                  <small>{text(wait !== null ? "min wait" : "")}</small>
                </strong>
                <div className="checkpoint-caption">
                  {text(
                    risk === "RED"
                      ? "↑ Intervention needed"
                      : risk === "ORANGE"
                        ? "↑ Rising pressure"
                        : risk === "YELLOW"
                          ? "● Attention"
                          : "✓ Healthy",
                  )}
                </div>
              </button>
            );
          }),
        )}
        <div className="map-gate">
          <Plane size={13} />
          <span>
            {text("GATE ")}
            {text(gate)}
          </span>
        </div>
        <div className="map-passenger">
          <Users size={12} />
          {text(" Food C · Passenger location ")}
        </div>
      </div>
      <div className="scene-toolbar">
        <span>
          <MoveUpRight size={17} />
          {text("N")}
          <span className="scale-line" />
          {text(" Illustrative scale ")}
        </span>
        <button
          aria-label={zoom ? "Zoom out map" : "Zoom in map"}
          onClick={() => setZoom(!zoom)}
        >
          {text(zoom ? <ZoomOut size={16} /> : <ZoomIn size={16} />)}
        </button>
      </div>
      <div className="checkpoint-inspector">
        <div>
          <span className="inspector-label">{text("SELECTED CHECKPOINT")}</span>
          <strong>
            {text(active.name)}
            <small>
              {text(horizon ? `+${horizon} min forecast` : "Current state")}
            </small>
          </strong>
        </div>
        <div>
          <span className="inspector-label">{text("WAIT RANGE")}</span>
          <strong>
            {text(
              horizon
                ? `${point.lower_bound}–${point.upper_bound ?? "∞"}`
                : (selectedWait ?? "Closed"),
            )}
            <small>{text("min · assumption")}</small>
          </strong>
        </div>
        <div>
          <span className="inspector-label">{text("QUEUE / LANES")}</span>
          <strong>
            {text(Math.round(horizon ? point.queue_length : active.queue))}
            <small>
              {text("pax / ")}
              {text(active.open_lanes)}
              {text(" open")}
            </small>
          </strong>
        </div>
        <button onClick={onCompare}>
          {text(" Explore actions ")}
          <ArrowUpRight size={14} />
        </button>
      </div>
    </div>
  );
}
