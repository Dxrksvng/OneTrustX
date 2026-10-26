import { useEffect, useState } from "react";
import { AlertTriangle, Clock3, Luggage, Plane, Users } from "lucide-react";
import { api } from "../services/api";
import { text } from "../i18n";

const HEADLINE: Record<string, string> = {
  NORMAL: "Baggage flow is normal. No action needed.",
  WATCH: "Bags are waiting longer than usual. No flight is at risk yet.",
  AT_RISK: "Bags are at risk of missing their flight.",
  VERIFY_DATA: "Scan data is missing. Verify before acting.",
};
const STATUS_LABEL: Record<string, string> = {
  NORMAL: "NORMAL",
  WATCH: "WATCH",
  AT_RISK: "AT RISK",
  VERIFY_DATA: "VERIFY DATA",
  OK: "OK",
  DELAY: "DELAY",
  RISK: "RISK",
  STALE: "NO SCANS",
};
// Reuses the platform's existing priority colours.
const TONE: Record<string, string> = {
  NORMAL: "GREEN",
  OK: "GREEN",
  WATCH: "YELLOW",
  RISK: "ORANGE",
  AT_RISK: "RED",
  DELAY: "RED",
  STALE: "",
  VERIFY_DATA: "",
};
const shown = (value: unknown) =>
  value === null || value === undefined ? "N/A" : String(value);

export default function BaggageControl() {
  const [catalog, setCatalog] = useState<any>(null),
    [scenario, setScenario] = useState("BAG-NORMAL"),
    [at, setAt] = useState<number | null>(null),
    [feed, setFeed] = useState(true),
    [view, setView] = useState<any>(null),
    [evaluation, setEvaluation] = useState<any>(null),
    [error, setError] = useState("");
  useEffect(() => {
    api("/trustx/baggage/scenarios")
      .then((c) => {
        setCatalog(c);
        setAt(c.default_at_min);
      })
      .catch((e) => setError(e.message));
    api("/trustx/baggage/evaluation")
      .then(setEvaluation)
      .catch(() => setEvaluation(null));
  }, []);
  useEffect(() => {
    if (at === null) return;
    api(
      `/trustx/baggage/control?scenario=${scenario}&at=${at}&resource_feed=${feed}`,
    )
      .then((v) => {
        setView(v);
        setError("");
      })
      .catch((e) => setError(e.message));
  }, [scenario, at, feed]);

  if (error)
    return (
      <section className="panel baggage-page">
        <div className="error" role="alert">
          <AlertTriangle size={18} />
          {text(error)}
        </div>
      </section>
    );
  if (!view || !catalog)
    return (
      <section className="panel baggage-page">
        <p>{text("Loading baggage view…")}</p>
      </section>
    );

  const { impact, next_action: action, bottleneck } = view,
    risky = impact.flights.filter((f: any) => f.bags_at_risk),
    range = (v: any) => (v ? `${v.median} (${v.min}–${v.max})` : "N/A");
  return (
    <div className="baggage-page">
      <section className="baggage-toolbar">
        <label>
          {text("Scenario")}
          <select
            value={scenario}
            onChange={(e) => setScenario(e.target.value)}
          >
            {catalog.scenarios.map((s: any) => (
              <option key={s.id} value={s.id}>
                {text(s.name)}
              </option>
            ))}
          </select>
        </label>
        <label>
          {text("Time")}
          <select value={at ?? 0} onChange={(e) => setAt(Number(e.target.value))}>
            {catalog.times.map((t: any) => (
              <option key={t.at_min} value={t.at_min}>
                {t.at}
              </option>
            ))}
          </select>
        </label>
        <label className="baggage-check">
          <input
            type="checkbox"
            checked={feed}
            onChange={(e) => setFeed(e.target.checked)}
          />
          {text("Ground-handler resource feed connected")}
        </label>
        <p>
          {text(view.scenario.summary)}{" "}
          <span className="tiny-tag">{text(view.scenario.evidence_tier)}</span>
        </p>
      </section>

      <section
        className={"baggage-status tone-" + (TONE[view.overall_status] || "NONE")}
        role="status"
      >
        <Luggage size={30} />
        <div>
          <small>
            {text("BAGGAGE FLOW")} · {view.at}
          </small>
          <h2>{text(HEADLINE[view.overall_status])}</h2>
        </div>
        <span className={"situation-priority " + TONE[view.overall_status]}>
          {text(STATUS_LABEL[view.overall_status])}
        </span>
      </section>

      <section className="metrics">
        <Tile
          icon={<AlertTriangle size={17} />}
          label="WHERE"
          value={bottleneck.stage || "No bottleneck"}
          detail={bottleneck.cause.text}
          attention={Boolean(bottleneck.stage)}
        />
        <Tile
          icon={<Plane size={17} />}
          label="FLIGHTS AT RISK"
          value={`${shown(impact.flights_at_risk)} / ${impact.flights_open}`}
          detail={`${shown(impact.bags_at_risk)} bags at risk · ${shown(impact.transfer_bags_at_risk)} transfer`}
          attention={Boolean(impact.flights_at_risk)}
        />
        <Tile
          icon={<Users size={17} />}
          label="ACTION OWNER"
          value={(action.owner || "None").replace("_", " ")}
          detail={
            action.approval === "HUMAN_REQUIRED"
              ? "Human approval required"
              : "No approval needed"
          }
        />
        <Tile
          icon={<Clock3 size={17} />}
          label="DECIDE BEFORE"
          value={action.deadline || "No deadline"}
          detail={`${shown(impact.bags_left_behind_so_far)} bags already left behind`}
        />
      </section>

      <section className="panel baggage-stages-panel">
        <div className="section-title">
          <div>
            <h2>{text("Stage-by-stage baggage flow")}</h2>
            <p>
              {text(
                "Each handoff shows bags waiting and how long the oldest has waited.",
              )}
            </p>
          </div>
          <span className="tiny-tag">{text("SIMULATED")}</span>
        </div>
        <ol className="baggage-stages">
          {view.stages.map((stage: any) => (
            <li key={stage.id} className={"tone-" + (TONE[stage.status] || "NONE")}>
              <span className={"situation-priority " + TONE[stage.status]}>
                {text(STATUS_LABEL[stage.status])}
              </span>
              <strong>{text(stage.label)}</strong>
              {stage.id === "check_in" ? (
                <b>{text("Entry point")}</b>
              ) : (
                <b>
                  {shown(stage.queue_bags)} {text("bags waiting")} ·{" "}
                  {shown(stage.oldest_bag_wait_min)} {text("min")}
                </b>
              )}
              {stage.note && <em>{text(stage.note)}</em>}
              <small>
                {text(stage.source)} · {text("last scan")} {shown(stage.last_scan)}
              </small>
            </li>
          ))}
        </ol>
      </section>

      <div className="baggage-two">
        <section className="panel">
          <h2>{text("Why the view says this")}</h2>
          {bottleneck.evidence.length ? (
            <ul>
              {bottleneck.evidence.map((item: string) => (
                <li key={item}>{text(item)}</li>
              ))}
            </ul>
          ) : (
            <p>{text("Every stage is clearing bags within its threshold.")}</p>
          )}
          <p>
            <b>{text("Cause")}</b> ·{" "}
            <span className="tiny-tag">{text(bottleneck.cause.status)}</span>{" "}
            {text(bottleneck.cause.text)}
          </p>
          <small>{text(impact.note)}</small>
        </section>
        <section className="panel baggage-action">
          <span className="eyebrow">{text("RECOMMENDED RECOVERY PRIORITY")}</span>
          <h2>{text(action.action)}</h2>
          {action.escalation && <p>{text(action.escalation)}</p>}
          <p>
            <b>{text("Owner")}</b> · {text((action.owner || "None").replace("_", " "))}{" "}
            · <b>{text("Deadline")}</b> · {text(action.deadline || "None")}
          </p>
          <small>
            {text(
              "One TrustX recommends; the operator decides. No airport equipment is controlled.",
            )}
          </small>
        </section>
      </div>

      {risky.length > 0 && (
        <section className="situations">
          <div className="section-title">
            <div>
              <h2>{text("Flights in priority order")}</h2>
              <p>{text("Earliest hold-close first.")}</p>
            </div>
          </div>
          <div className="extra-scroll">
            <table className="data-table">
              <thead>
                <tr>
                  {["Flight", "Departs", "Hold closes", "Loaded", "Bags at risk", "Transfer at risk", "Reason"].map(
                    (h) => (
                      <th key={h}>{text(h)}</th>
                    ),
                  )}
                </tr>
              </thead>
              <tbody>
                {risky.map((f: any) => (
                  <tr key={f.flight}>
                    <td>
                      <strong>{f.flight}</strong>
                    </td>
                    <td>{f.etd}</td>
                    <td>
                      {f.hold_closes}
                      <small>
                        {f.minutes_to_close} {text("min")}
                      </small>
                    </td>
                    <td>
                      {f.bags_loaded} / {f.bags_expected}
                    </td>
                    <td>{f.bags_at_risk}</td>
                    <td>{f.transfer_bags_at_risk}</td>
                    <td>{text(f.reason)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </section>
      )}

      {evaluation && (
        <section className="situations">
          <div className="section-title">
            <div>
              <h2>{text("Repeated simulation")}</h2>
              <p>
                {text("Median (min–max) over")}{" "}
                {evaluation.scenarios["BAG-NORMAL"].runs} {text("seeded runs per scenario.")}{" "}
                {text("Synthetic flights, bags and capacities; not Suvarnabhumi performance.")}
              </p>
            </div>
            <span className="tiny-tag">{text("SIMULATED")}</span>
          </div>
          <div className="extra-scroll">
            <table className="data-table">
              <thead>
                <tr>
                  {["Scenario", "Bags missed, equal share", "Bags missed, priority order", "Warning lead (min)", "Flight precision", "Flight recall"].map(
                    (h) => (
                      <th key={h}>{text(h)}</th>
                    ),
                  )}
                </tr>
              </thead>
              <tbody>
                {Object.entries(evaluation.scenarios).map(([id, r]: any) => (
                  <tr key={id}>
                    <td>
                      <strong>{text(r.name)}</strong>
                    </td>
                    <td>{range(r.bags_missed_plan_policy)}</td>
                    <td>{range(r.bags_missed_priority_policy)}</td>
                    <td>{range(r.detection_lead_min)}</td>
                    <td>{shown(r.flight_precision)}</td>
                    <td>{shown(r.flight_recall)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </section>
      )}

      <section className="panel baggage-inputs">
        <h2>{text("Data used for this view")}</h2>
        <ul>
          {view.inputs_used.map((item: string) => (
            <li key={item}>{text(item)}</li>
          ))}
        </ul>
        <small>
          {text(view.privacy)}{" "}
          {text(
            "One TrustX builds on existing systems; it does not replace BRS, AODB or A-CDM.",
          )}
        </small>
      </section>
    </div>
  );
}

function Tile({ icon, label, value, detail, attention = false }: any) {
  return (
    <article className={"metric " + (attention ? "attention" : "")}>
      <div className="metric-label">
        {text(label)}
        {icon}
      </div>
      <div className="metric-value baggage-tile-value">{text(value)}</div>
      <p>{text(detail)}</p>
    </article>
  );
}
