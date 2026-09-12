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
          T1 · DEPARTURES
        </span>
        <span>ILLUSTRATIVE DIGITAL TWIN</span>
      </div>
      <div className={"airport-canvas " + (zoom ? "zoomed" : "")}>
        <svg
          className="terminal-blueprint"
          viewBox="0 0 800 390"
          role="img"
          aria-label="Illustrative terminal with two security routes leading to immigration and departure concourses"
        >
          <defs>
            <pattern
              id="blueprintGrid"
              width="26"
              height="26"
              patternUnits="userSpaceOnUse"
            >
              <path
                d="M26 0H0V26"
                fill="none"
                stroke="#34564a"
                strokeWidth=".5"
              />
            </pattern>
            <linearGradient id="terminalRoof" x1="0" x2="1" y1="0" y2="1">
              <stop stopColor="#477365" />
              <stop offset="1" stopColor="#284c40" />
            </linearGradient>
            <filter id="buildingShadow">
              <feDropShadow dx="0" dy="7" stdDeviation="6" floodOpacity=".25" />
            </filter>
          </defs>
          <rect width="800" height="390" fill="url(#blueprintGrid)" />
          <g opacity=".35" fill="none" stroke="#749586">
            <path
              d="M-20 310 Q130 350 275 320T610 338T820 306"
              strokeWidth="20"
            />
            <path
              d="M-20 310 Q130 350 275 320T610 338T820 306"
              stroke="#152f26"
              strokeWidth="16"
            />
            <path
              d="M-20 310 Q130 350 275 320T610 338T820 306"
              strokeDasharray="7 8"
            />
            <path d="M30 23H770" strokeWidth="2" />
            <path d="M30 16H770" strokeDasharray="15 8" />
          </g>
          <g
            filter="url(#buildingShadow)"
            stroke="#83a58d"
            strokeWidth="1"
            fill="url(#terminalRoof)"
          >
            <path d="M110 131L622 131 649 157 649 256 623 281 110 281 84 256 84 157Z" />
            <path d="M160 131V77L180 56H216L235 77V131Z" />
            <path d="M331 131V63L351 43H387L407 63V131Z" />
            <path d="M505 131V77L525 56H561L580 77V131Z" />
            <path d="M622 166H720L739 187V222L720 243H649V256" />
          </g>
          <g stroke="#90b49a" strokeWidth=".65" opacity=".5">
            <path d="M117 148H619M103 169H628M103 242H628M117 264H619M275 133V280M457 132V280M620 157V251" />
            <path d="M168 83H228M168 93H228M168 103H228M339 68H399M339 80H399M339 92H399M513 83H573M513 95H573M513 107H573" />
            {[
              140, 160, 180, 200, 220, 240, 295, 315, 335, 355, 375, 395, 415,
              435, 475, 495, 515, 535, 555, 575, 595,
            ].map((x) => (
              <path key={x} d={`M${x} 134V147 M${x} 265V278`} />
            ))}
          </g>
          <g
            fill="#a2baa3"
            fontSize="9"
            fontFamily="monospace"
            letterSpacing="2"
          >
            <text x="175" y="116">
              C8
            </text>
            <text x="347" y="116">
              D
            </text>
            <text x="526" y="116">
              E7
            </text>
            <text x="304" y="260">
              IMMIGRATION → CONCOURSES
            </text>
            <text x="335" y="307">
              TERMINAL FORECOURT
            </text>
            <text x="640" y="36">
              AIRCRAFT APRON
            </text>
          </g>
          <g fill="none" strokeWidth="2.5" strokeLinecap="round">
            <path
              className="flow-route alternate"
              d="M178 284V233Q178 222 190 222H400Q414 222 414 207V179Q414 169 426 169H540V120"
              stroke="#7dafa6"
              strokeDasharray="5 7"
            />
            <path
              className="flow-route"
              d="M178 284V194Q178 183 194 183H359Q371 183 371 168V121"
              stroke="#c5e59b"
              strokeDasharray="5 7"
            />
          </g>
          <circle cx="178" cy="284" r="6" fill="#d5eda9" />
          <circle
            className="location-ring"
            cx="178"
            cy="284"
            r="12"
            fill="none"
            stroke="#c5e59b"
          />
          <g fill="#c7dbc4" opacity=".7">
            <path d="M193 36l3-14 2 0 3 14 11 8v3l-11-4-1 8 4 4v2l-7-2-7 2v-2l4-4-1-8-11 4v-3z" />
            <path d="M536 36l3-14 2 0 3 14 11 8v3l-11-4-1 8 4 4v2l-7-2-7 2v-2l4-4-1-8-11 4v-3z" />
          </g>
        </svg>
        {checkpoints.map((cp, index) => {
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
                {cp.name}
                <span className="checkpoint-light" />
              </div>
              <strong key={`${horizon}-${wait}`}>
                {wait === null ? "Closed" : Math.round(wait)}
                <small>{wait !== null ? "min wait" : ""}</small>
              </strong>
              <div className="checkpoint-caption">
                {risk === "RED"
                  ? "↑ Intervention needed"
                  : risk === "ORANGE"
                    ? "↑ Rising pressure"
                    : risk === "YELLOW"
                      ? "● Attention"
                      : "✓ Healthy"}
              </div>
            </button>
          );
        })}
        <div className="map-gate">
          <Plane size={13} />
          <span>GATE {gate}</span>
        </div>
        <div className="map-passenger">
          <Users size={12} />
          Food C · Passenger location
        </div>
      </div>
      <div className="scene-toolbar">
        <span>
          <MoveUpRight size={17} />N<span className="scale-line" />
          Illustrative scale
        </span>
        <button
          aria-label={zoom ? "Zoom out map" : "Zoom in map"}
          onClick={() => setZoom(!zoom)}
        >
          {zoom ? <ZoomOut size={16} /> : <ZoomIn size={16} />}
        </button>
      </div>
      <div className="checkpoint-inspector">
        <div>
          <span className="inspector-label">SELECTED CHECKPOINT</span>
          <strong>
            {active.name}
            <small>
              {horizon ? `+${horizon} min forecast` : "Current state"}
            </small>
          </strong>
        </div>
        <div>
          <span className="inspector-label">WAIT RANGE</span>
          <strong>
            {horizon
              ? `${point.lower_bound}–${point.upper_bound ?? "∞"}`
              : (selectedWait ?? "Closed")}
            <small>min · assumption</small>
          </strong>
        </div>
        <div>
          <span className="inspector-label">QUEUE / LANES</span>
          <strong>
            {Math.round(horizon ? point.queue_length : active.queue)}
            <small>pax / {active.open_lanes} open</small>
          </strong>
        </div>
        <button onClick={onCompare}>
          Explore actions
          <ArrowUpRight size={14} />
        </button>
      </div>
    </div>
  );
}
