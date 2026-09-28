import { text } from "../i18n";
import { useEffect, useState } from "react";
import { api } from "../services/api";
const n = (value: number | null | undefined) =>
  value == null
    ? "Not available"
    : value.toLocaleString(undefined, { maximumFractionDigits: 1 });
export function ResourceEfficiency({ impact }: { impact: any }) {
  const b = impact?.baseline,
    p = impact?.proposed;
  if (!b || !p)
    return (
      <p>
        {text(
          "Resource comparison paused until a fresh, feasible scenario is available.",
        )}
      </p>
    );
  return (
    <section className="panel section-gap">
      <span className="eyebrow">
        {text("RESOURCE EFFICIENCY · SIMULATED MVP RESULT")}
      </span>
      <h2>{text("Use existing capacity more effectively.")}</h2>
      <p>
        {text(
          "Optimize existing airport capacity before adding permanent physical infrastructure.",
        )}
      </p>
      <p>
        {text(impact.basis)}
        {text(
          " · Both security checkpoints, from initial queue until all cohorts are processed.",
        )}
      </p>
      <div className="extra-scroll">
        <table className="data-table">
          <thead>
            <tr>
              <th>{text("Metric")}</th>
              <th>{text("Baseline")}</th>
              <th>{text("Proposed / accepted")}</th>
            </tr>
          </thead>
          <tbody>
            {text(
              [
                [
                  "Passenger delay + extra walking (pax·min)",
                  b.passenger_minutes,
                  p.passenger_minutes,
                ],
                ["P95 cohort wait (min)", b.p95_wait, p.p95_wait],
                ["Staff-minutes", b.staff_minutes, p.staff_minutes],
                [
                  "Active lane-minutes",
                  b.active_lane_minutes,
                  p.active_lane_minutes,
                ],
                [
                  "Resource utilization (%)",
                  b.resource_utilization * 100,
                  p.resource_utilization * 100,
                ],
                [
                  "Additional walking (pax·min)",
                  b.additional_walking_minutes,
                  p.additional_walking_minutes,
                ],
                [
                  "Walking / redirected passenger (min)",
                  b.walking_per_redirected_passenger,
                  p.walking_per_redirected_passenger,
                ],
                [
                  "High-risk journey share (%)",
                  b.high_risk_journey_share * 100,
                  p.high_risk_journey_share * 100,
                ],
                [
                  "Cohort drain window (min)",
                  b.measurement_window_min,
                  p.measurement_window_min,
                ],
              ].map(([label, a, z]) => (
                <tr key={String(label)}>
                  <td>{text(label)}</td>
                  <td>{text(n(a as number))}</td>
                  <td>{text(n(z as number))}</td>
                </tr>
              )),
            )}
          </tbody>
        </table>
      </div>
      <p>
        {text(
          "Infrastructure expansion required: none for this intervention. An existing spare lane and reserve staff are assumptions.",
        )}
      </p>
      <p className="note">
        {text(
          "Staff and lanes remain active until cohort drain; improvements in every resource metric are not guaranteed. High-risk share means checkpoint waits exceeding the assumed 35-minute journey budget, not a missed-flight probability. A zero means no modelled cohorts exceeded that threshold. No CO₂ savings are claimed.",
        )}
      </p>
    </section>
  );
}
export function JourneyFlow({ flow }: { flow: any }) {
  const [h, setH] = useState(30);
  const p = flow.plans.find((x: any) => x.horizon === h);
  return (
    <section>
      <h2>{text("Airport Journey Flow")}</h2>
      <span className="tiny-tag">
        {text("ILLUSTRATIVE JOURNEY FLOW · SYNTHETIC PROCESS TOPOLOGY")}
      </span>
      <div className="horizon-tabs">
        {text(
          [15, 30, 60].map((x) => (
            <button key={x} aria-pressed={h === x} onClick={() => setH(x)}>
              {text("+")}
              {text(x)}
              {text(" min")}
            </button>
          )),
        )}
      </div>
      <div className="journey-flow-scroll">
        <svg
          viewBox="0 0 1260 360"
          role="img"
          aria-label={text(
            "580 passengers from terminal arrival through check-in, bag drop, security, domestic bypass or immigration, concourse and gate zones",
          )}
        >
          <g fill="none" stroke="#7793a8" opacity=".45">
            {text(
              [
                [80, 180, 240, 180, 580],
                [240, 180, 390, 180, 580],
                [390, 180, 560, 100, p.security_a],
                [390, 180, 560, 260, p.security_b],
                [560, 100, 730, 180, p.security_a],
                [560, 260, 730, 180, p.security_b],
                [730, 180, 880, 90, 290],
                [730, 180, 880, 270, 290],
                [880, 90, 1030, 180, 290],
                [880, 270, 1030, 180, 290],
                [1030, 180, 1180, 180, 580],
              ].map(([x, y, z, w, count], i) => (
                <path
                  key={i}
                  d={`M${x} ${y} C${(x + z) / 2} ${y},${(x + z) / 2} ${w},${z} ${w}`}
                  strokeWidth={Math.max(4, count / 16)}
                />
              )),
            )}
          </g>
          <g fill="#17384d" textAnchor="middle" fontSize="15">
            {text(
              [
                [80, 180, "Terminal Arrival", 580],
                [240, 180, "Check-in", 580],
                [390, 180, "Bag Drop", 580],
                [560, 100, "Security A", p.security_a],
                [560, 260, "Security B", p.security_b],
                [730, 180, "Processed flow", 580],
                [880, 90, "Immigration", 290],
                [880, 270, "Domestic bypass", 290],
                [1030, 180, "Concourse", 580],
                [1180, 180, "Gate Zones", 580],
              ].map(([x, y, label, count]) => (
                <g key={String(label)}>
                  <rect
                    x={Number(x) - 65}
                    y={Number(y) - 34}
                    width="130"
                    height="68"
                    rx="5"
                    fill="#f4f6f7"
                    stroke="#cbd5dc"
                  />
                  <text x={x} y={Number(y) - 3}>
                    {text(label)}
                  </text>
                  <text x={x} y={Number(y) + 21}>
                    {text(count)}
                    {text(" pax")}
                  </text>
                </g>
              )),
            )}
          </g>
        </svg>
      </div>
      <p>
        {text("Gate allocation: ")}
        {text(
          Object.entries(p.gates)
            .map(([gate, count]) => `${gate}: ${count}`)
            .join(" · "),
        )}
      </p>
      <p>
        {text(
          "580 representative flight passengers · 290 international · 290 domestic (immigration bypass). All use check-in and bag drop in this illustrative route plan. Line width represents simulated passenger volume.",
        )}
      </p>
      <p className="note">
        {text(
          "This is a full-cohort routing plan at the selected forecast horizon, not simultaneous occupancy. Queue simulation covers ",
        )}
        {text(p.network_demand)}
        {text(" passengers including ")}
        {text(p.initial_queue)}
        {text(" already queued and ")}
        {text(p.new_network_arrivals)}
        {text(
          " new arrivals across the full 60-minute window. It includes background demand; 580 is the representative flight cohort, not the network KPI denominator.",
        )}
      </p>
      <a href="/simulator">{text("Compare routing options →")}</a>
    </section>
  );
}
export function Integration() {
  return (
    <section className="panel">
      <span className="eyebrow">{text("SYSTEM INTEGRATION")}</span>
      <h2>{text("Existing intelligence → One TrustX decision layer")}</h2>
      <p>
        {text(
          "One TrustX does not replace existing passenger-flow intelligence. It adds a prescriptive decision and simulation layer on top of it.",
        )}
      </p>
      <div className="integration-chain">
        <div>
          <h3>{text("Existing airport systems")}</h3>
          <p>
            {text(
              "AODB · Flight Information · Passenger Flow / Smart Flow · PVS · CUPPS / CUSS · Gate · Baggage · Ground Handling",
            )}
          </p>
          <span className="tiny-tag">
            {text("FUTURE PRODUCTION CONNECTOR")}
          </span>
          <p>
            {text(
              "Conceptual interfaces only. Access, contracts, operational ownership and validation are required.",
            )}
          </p>
        </div>
        <div>
          <h3>{text("Normalization / event layer")}</h3>
          <p>
            {text("Public context cache: OurAirports · Open-Meteo · OpenSky")}
          </p>
          <span className="tiny-tag">{text("PUBLIC API / PUBLIC DATA")}</span>
          <p>
            {text(
              "Queues · anonymous journeys · lane capacity · flight fixtures",
            )}
          </p>
          <span className="tiny-tag">{text("SYNTHETIC ADAPTER")}</span>
        </div>
        <div>
          <h3>{text("One TrustX")}</h3>
          <p>{text("Predict → Simulate → Compare → Recommend → Audit")}</p>
          <span className="tiny-tag">{text("MVP CONNECTED")}</span>
          <p>
            {text(
              "FastAPI · PostgreSQL · deterministic queue engine · graph routing",
            )}
          </p>
        </div>
        <div>
          <h3>{text("Human operator")}</h3>
          <p>
            {text(
              "Approve · Reject · Override → Airport operations / passenger re-plan → Measure outcome",
            )}
          </p>
          <strong>
            {text("No autonomous airport equipment control in the MVP.")}
          </strong>
        </div>
      </div>
      <h2>{text("Pilot / Field Validation Plan")}</h2>
      <ol>
        <li>
          {text(
            "Historical replay / backtesting with permitted operational data.",
          )}
        </li>
        <li>
          {text(
            "Shadow mode at two checkpoints; no operational interventions.",
          )}
        </li>
        <li>
          {text(
            "Human decision-support pilot with airport-approved constraints.",
          )}
        </li>
        <li>
          {text(
            "Controlled operational integration following validation and governance.",
          )}
        </li>
      </ol>
      <p>
        {text(
          "Evaluate MAE, precision, recall, false alarm rate, warning lead time, P95 wait, passenger-minutes, staff-minutes, lane-minutes, utilization and high-risk journey share.",
        )}
      </p>
      <p className="note">
        {text(
          "A proposed validation plan, not a deployment claim. No existing vendor capability gaps are asserted.",
        )}
      </p>
    </section>
  );
}
export function DecisionHistory() {
  const [rows, setRows] = useState<any[]>([]),
    [error, setError] = useState("");
  useEffect(() => {
    api("/decision-history")
      .then(setRows)
      .catch((e) => setError(e.message));
  }, []);
  return (
    <section className="panel section-gap decision-history">
      <h2>{text("One decision. One traceable lifecycle.")}</h2>
      {text(error && <p role="alert">{text(error)}</p>)}
      {text(
        !rows.length && (
          <p>{text("No reviewed decisions in this demo session.")}</p>
        ),
      )}
      {text(
        rows.map((r) => (
          <article className="audit-row" key={r.decision_id}>
            <h3>{text(r.action)}</h3>
            <p>
              {text(r.operator_action)}
              {text(" · ")}
              {text(r.operator)}
              {text(" · ")}
              {text(r.reason)}
            </p>
            <ol>
              <li>
                {text(new Date(r.prediction_created).toLocaleTimeString())}
                {text(" · Prediction created: Security A +30 wait ")}
                {text(n(r.forecast_wait))}
                {text(" min")}
              </li>
              <li>
                {text("Recommendation generated: ")}
                {text(r.action)}
              </li>
              <li>
                {text(new Date(r.reviewed_at).toLocaleTimeString())}
                {text(" · Decision reviewed: ")}
                {text(r.operator_action)}
              </li>
              {text(
                r.result && (
                  <>
                    <li>{text("Synthetic intervention applied")}</li>
                    <li>
                      {text("Predicted network average wait: ")}
                      {text(n(r.result.after_predicted))}
                      {text(" min")}
                    </li>
                    <li>
                      {text("Observed simulated outcome: ")}
                      {text(n(r.result.after_actual))}
                      {text(" min")}
                    </li>
                    <li>
                      {text("Forecast error (observed − predicted): ")}
                      {text(n(r.result.prediction_error))}
                      {text(" min")}
                    </li>
                  </>
                ),
              )}
            </ol>
            <details>
              <summary>{text("Trace IDs")}</summary>
              <p>
                {text("prediction_id: ")}
                {text(r.prediction_id)}
              </p>
              <p>
                {text("recommendation_id: ")}
                {text(r.recommendation_id)}
              </p>
              <p>
                {text("decision_id: ")}
                {text(r.decision_id)}
              </p>
            </details>
          </article>
        )),
      )}
    </section>
  );
}
export function ModelQuality({ evaluation }: { evaluation: any }) {
  if (!evaluation) return <p>{text("Loading evaluation…")}</p>;
  const rows = evaluation.results.filter((r: any) => r.model === "fluid");
  return (
    <section>
      <h2>{text("Model quality · offline synthetic evaluation")}</h2>
      <p>
        {text(
          "Current MVP decision engine uses deterministic queue simulation. ML candidates are evaluated offline and are not promoted until they outperform baseline methods and pass validation.",
        )}
      </p>
      <p>{text(evaluation.split)}</p>
      <div className="extra-scroll">
        <table className="data-table">
          <thead>
            <tr>
              <th>{text("Horizon")}</th>
              <th>{text("MAE")}</th>
              <th>{text("Precision")}</th>
              <th>{text("Recall")}</th>
              <th>{text("F1")}</th>
              <th>{text("False alarm rate")}</th>
              <th>{text("Warning lead time")}</th>
            </tr>
          </thead>
          <tbody>
            {text(
              rows.map((r: any) => (
                <tr key={r.horizon_min}>
                  <td>
                    {text("+")}
                    {text(r.horizon_min)}
                    {text(" min")}
                  </td>
                  <td>{text(n(r.mae))}</td>
                  <td>
                    {text(n(r.congestion_precision * 100))}
                    {text("%")}
                  </td>
                  <td>
                    {text(n(r.congestion_recall * 100))}
                    {text("%")}
                  </td>
                  <td>
                    {text(n(r.f1 * 100))}
                    {text("%")}
                  </td>
                  <td>
                    {text(
                      r.false_alarm_rate == null
                        ? "Not evaluated"
                        : n(r.false_alarm_rate * 100) + "%",
                    )}
                  </td>
                  <td>
                    {text(n(r.median_detected_lead_time_min))}
                    {text(" min")}
                  </td>
                </tr>
              )),
            )}
          </tbody>
        </table>
      </div>
      <p className="note">
        {text(
          "Offline fluid baseline on synthetic evaluation data; not a calibrated guarantee for this demo or a real airport. Warning lead time reports detected events only.",
        )}
      </p>
      <details>
        <summary>{text("View Technical Evaluation")}</summary>
        <p>{text(evaluation.promotion)}</p>
        <div className="extra-scroll">
          <table className="data-table">
            <thead>
              <tr>
                <th>{text("Model")}</th>
                <th>{text("Horizon")}</th>
                <th>{text("MAE")}</th>
                <th>{text("RMSE")}</th>
                <th>{text("Precision")}</th>
                <th>{text("Recall")}</th>
                <th>{text("F1")}</th>
                <th>{text("False alarm rate")}</th>
                <th>{text("Lead time")}</th>
              </tr>
            </thead>
            <tbody>
              {text(
                evaluation.results.map((r: any) => (
                  <tr key={r.model + r.horizon_min}>
                    <td>{text(r.model)}</td>
                    <td>{text(r.horizon_min)}</td>
                    <td>{text(n(r.mae))}</td>
                    <td>{text(n(r.rmse))}</td>
                    <td>{text(n(r.congestion_precision))}</td>
                    <td>{text(n(r.congestion_recall))}</td>
                    <td>{text(n(r.f1))}</td>
                    <td>{text(n(r.false_alarm_rate))}</td>
                    <td>{text(n(r.median_detected_lead_time_min))}</td>
                  </tr>
                )),
              )}
            </tbody>
          </table>
        </div>
      </details>
    </section>
  );
}
