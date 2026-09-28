import { text } from "../i18n";
import { ResourceEfficiency } from "./PilotPanels";
import { useEffect, useState } from "react";
const format = (v: number | undefined) =>
  v == null
    ? "Unavailable"
    : v.toLocaleString(undefined, { maximumFractionDigits: 1 });
export default function DecisionWorkspace({
  comparison,
  busy,
  stale,
  onDecision,
}: {
  comparison: any;
  busy: boolean;
  stale: boolean;
  onDecision: (o: any, d: string) => void;
}) {
  const [selection, setSelection] = useState("");
  useEffect(() => {
    setSelection(comparison?.recommended || comparison?.options[0]?.name || "");
  }, [comparison?.recommended]);
  const base = comparison?.options[0],
    proposed =
      comparison?.options.find((x: any) => x.name === selection) || base;
  if (!base || !proposed)
    return (
      <p>{text("No comparison is available. Refresh the operational feed.")}</p>
    );
  const rows = [
    ["Network average wait", base.average_wait, proposed.average_wait, "min"],
    ["P95 cohort wait", base.p95_wait, proposed.p95_wait, "min"],
    ["Peak network queue", base.peak_queue, proposed.peak_queue, "pax"],
    ["Passenger-minutes saved", 0, proposed.passenger_minutes_saved, "pax·min"],
    ["Additional staff", 0, proposed.additional_staff, "staff"],
    [
      "Walking impact / passenger",
      base.walking_penalty,
      proposed.walking_penalty,
      "min",
    ],
    [
      "High-risk journey share",
      base.high_risk_journey_share * 100,
      proposed.high_risk_journey_share * 100,
      "%",
    ],
  ];
  return (
    <section className="decision-workspace">
      <div className="decision-steps">
        <span>{text("01 Situation")}</span>
        <span>{text("02 Strategy")}</span>
        <span>{text("03 Comparison & review")}</span>
      </div>
      <div className="decision-context">
        <div>
          <span className="eyebrow">{text("SITUATION")}</span>
          <h2>{text("Security A · forecast pressure")}</h2>
        </div>
        <p>
          {text(" Both checkpoints are included in the comparison. ")}
          <br />
          {text(
            " Reserve staffing and route eligibility are model assumptions. ",
          )}
        </p>
      </div>
      <div className="decision-layout">
        <fieldset className="strategy-list">
          <legend>{text("Select intervention strategy")}</legend>
          {text(
            comparison.options.map((o: any) => (
              <label
                key={o.name}
                className={selection === o.name ? "chosen" : ""}
              >
                <input
                  type="radio"
                  name="strategy"
                  value={o.name}
                  checked={selection === o.name}
                  onChange={() => setSelection(o.name)}
                />
                <span>
                  {text(o.name)}
                  {text(
                    o.name === comparison.recommended && (
                      <small>
                        {text("Recommended by configured utility score")}
                      </small>
                    ),
                  )}
                </span>
              </label>
            )),
          )}
        </fieldset>
        <div className="strategy-comparison">
          <table className="data-table">
            <thead>
              <tr>
                <th>{text("Outcome")}</th>
                <th>{text("Baseline")}</th>
                <th>{text("Proposed")}</th>
              </tr>
            </thead>
            <tbody>
              {text(
                rows.map(([name, b, a, unit]) => (
                  <tr key={String(name)}>
                    <td>{text(name)}</td>
                    <td>
                      {text(format(b as number))} {text(unit)}
                    </td>
                    <td>
                      {text(format(a as number))} {text(unit)}
                    </td>
                  </tr>
                )),
              )}
            </tbody>
          </table>
        </div>
      </div>
      <div className="decision-review">
        <div>
          <span className="eyebrow">{text("OPERATOR REVIEW")}</span>
          <h3>{text(proposed.name)}</h3>
          <p>{text(comparison.reason)}</p>
          <details>
            <summary>{text("View scoring formula")}</summary>
            <p>
              {text(
                "Wait reduction + 0.01 × passenger-minutes saved + 50 × high-risk share reduction − additional staff − walking penalty − 0.001 × cost proxy.",
              )}
            </p>
            <small>
              {text(" Score ")}
              {text(format(proposed.score))}
              {text(" · Cost proxy")}
              {text(" ")}
              {text(format(proposed.cost_proxy))}
              {text(" · Confidence")}
              {text(" ")}
              {text(format(proposed.confidence * 100))}
              {text("% (heuristic) ")}
            </small>
          </details>
          <h3>{text("Why recommended")}</h3>
          <p>
            {text("Wait reduction: ")}
            {text(
              proposed.average_wait < base.average_wait ? "Positive" : "None",
            )}
            {text(" · Passenger impact: ")}
            {text(proposed.passenger_minutes_saved > 0 ? "Positive" : "None")}
            {text(" · Staff: ")}
            {text(proposed.additional_staff)}
            {text(" additional · Walking: ")}
            {text(proposed.walking_penalty)}
            {text(" min / network passenger · Feasibility: ")}
            {text(proposed.feasible ? "Feasible" : "Not feasible")}
          </p>
        </div>
        <div>
          <button
            className="primary"
            disabled={
              busy ||
              stale ||
              !proposed.feasible ||
              proposed === base ||
              proposed.decision !== "pending"
            }
            onClick={() => onDecision(proposed, "accept")}
          >
            {text(" Submit recommendation ")}
          </button>
          <button
            disabled={
              busy || proposed === base || proposed.decision !== "pending"
            }
            onClick={() => onDecision(proposed, "reject")}
          >
            {text(" Reject option ")}
          </button>
        </div>
      </div>
      <ResourceEfficiency
        impact={{ baseline: base, proposed, basis: "CURRENT COMPARISON" }}
      />
      <p className="note">
        {text(
          " Submitting records human approval and updates the synthetic demo only. No airport equipment is controlled. Risk is the share of cohort waits exceeding a 35-minute assumed budget, not a flight-specific probability. ",
        )}
      </p>
    </section>
  );
}
