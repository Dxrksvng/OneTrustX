import { text } from "../i18n";
import { useState } from "react";
export default function ComparisonReveal({
  before,
  after,
}: {
  before: any;
  after: any;
}) {
  const [position, setPosition] = useState(50);
  if (!before || !after) return null;
  return (
    <section className="panel reveal-panel">
      <div className="panel-heading">
        <h2>{text("Compare two possible futures")}</h2>
        <span className="tiny-tag">{text("SIMULATED · NETWORK AVERAGE")}</span>
      </div>
      <div className="comparison-reveal">
        <div className="reveal-state after">
          <span>{text("WITH SELECTED INTERVENTION")}</span>
          <strong>
            {text(after.average_wait.toFixed(1))} <small>{text("min")}</small>
          </strong>
          <p>
            {text("P95: ")}
            {text(after.p95_wait.toFixed(1))}
            {text(" min")}
          </p>
        </div>
        <div
          className="reveal-state before"
          style={{ clipPath: `inset(0 ${100 - position}% 0 0)` }}
        >
          <span>{text("NO ACTION")}</span>
          <strong>
            {text(before.average_wait.toFixed(1))} <small>{text("min")}</small>
          </strong>
          <p>
            {text("P95: ")}
            {text(before.p95_wait.toFixed(1))}
            {text(" min")}
          </p>
        </div>
        <div className="reveal-divider" style={{ left: `${position}%` }}>
          {text(" ↔ ")}
        </div>
      </div>
      <label>
        {text(" Drag to compare before and after ")}
        <input
          aria-label={text("Before and after comparison")}
          type="range"
          min="0"
          max="100"
          value={position}
          onChange={(e) => setPosition(Number(e.target.value))}
        />
      </label>
      <p className="note">
        {text(" Simulated MVP Result — Not actual airport performance. ")}
      </p>
    </section>
  );
}
