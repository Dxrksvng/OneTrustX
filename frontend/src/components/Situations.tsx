import { text } from "../i18n";
import { useRef, useState } from "react";
export default function Situations({
  overview,
  onAnalyse,
}: {
  overview: any;
  onAnalyse: () => void;
}) {
  const dialog = useRef<HTMLDialogElement>(null);
  const [chosen, setChosen] = useState<any>(null);
  const [filter, setFilter] = useState("All");
  const rows = overview.checkpoints.map((c: any) => {
    const p = c.forecast.find((x: any) => x.horizon === 30);
    return {
      id: c.id,
      name: c.name,
      priority: p.risk_level,
      description:
        p.risk_level === "GREEN"
          ? "Stable processing"
          : "Forecast processing pressure",
      impact: `${Math.round(p.queue_length)} queued`,
      window: "+30 min",
      current: c.current_wait,
      range: `${p.lower_bound}–${p.upper_bound ?? "unavailable"}`,
      kind: "checkpoint",
    };
  });
  if (overview.scenario.gate === "E7")
    rows.push({
      id: "gate-change",
      name: "Gate C8 → E7",
      priority: "ORANGE",
      description: "Passenger route changed",
      impact: "Demo journey",
      window: "Current scenario",
      kind: "gate",
    });
  const rank: Record<string, number> = {
    RED: 0,
    ORANGE: 1,
    YELLOW: 2,
    GREEN: 3,
  };
  rows.sort((a: any, b: any) => rank[a.priority] - rank[b.priority]);
  return (
    <section className="situations">
      <div className="section-title">
        <div>
          <h2>{text("Operational situations")}</h2>
          <p>
            {text(
              " Prioritised from the current model. No inferred stand conflicts or unobserved incidents. ",
            )}
          </p>
        </div>
        <label>
          {text(" Status")}
          {text(" ")}
          <select value={filter} onChange={(e) => setFilter(e.target.value)}>
            <option>{text("All")}</option>
            <option>{text("Requires attention")}</option>
          </select>
        </label>
      </div>
      <div className="extra-scroll">
        <table className="data-table">
          <thead>
            <tr>
              <th>{text("Priority")}</th>
              <th>{text("Situation")}</th>
              <th>{text("Impact")}</th>
              <th>{text("Window")}</th>
              <th>{text("Review")}</th>
            </tr>
          </thead>
          <tbody>
            {text(
              rows
                .filter((r: any) => filter === "All" || r.priority !== "GREEN")
                .map((r: any) => (
                  <tr key={r.id}>
                    <td>
                      <span className={"situation-priority " + r.priority}>
                        {text(
                          r.priority === "RED"
                            ? "CRITICAL"
                            : r.priority === "ORANGE"
                              ? "HIGH"
                              : r.priority === "YELLOW"
                                ? "WATCH"
                                : "STABLE",
                        )}
                      </span>
                    </td>
                    <td>
                      <strong>{text(r.name)}</strong>
                      <small>{text(r.description)}</small>
                    </td>
                    <td>{text(r.impact)}</td>
                    <td>{text(r.window)}</td>
                    <td>
                      <button
                        onClick={() => {
                          setChosen(r);
                          dialog.current?.showModal();
                        }}
                      >
                        {text(" Investigate ")}
                        {text(r.name)}
                      </button>
                    </td>
                  </tr>
                )),
            )}
          </tbody>
        </table>
      </div>
      <dialog ref={dialog} className="situation-dialog">
        <button onClick={() => dialog.current?.close()}>
          {text("Close situation")}
        </button>
        {text(
          chosen && (
            <>
              <span className="eyebrow">
                {text("OPERATIONAL ASSESSMENT · SIMULATED")}
              </span>
              <h2>{text(chosen.name)}</h2>
              <p>{text(chosen.description)}</p>
              {text(
                chosen.kind === "checkpoint" ? (
                  <>
                    <div className="situation-numbers">
                      <div>
                        <small>{text("Current wait")}</small>
                        <strong>
                          {text(chosen.current ?? "Unavailable")}
                          {text(" min")}
                        </strong>
                      </div>
                      <div>
                        <small>{text("Forecast +30")}</small>
                        <strong>
                          {text(chosen.range)}
                          {text(" min")}
                        </strong>
                      </div>
                    </div>
                    <p>
                      {text(" Forecast queue: ")}
                      {text(chosen.impact)}
                      {text(
                        ". This is not a count of individually affected passengers. ",
                      )}
                    </p>
                  </>
                ) : (
                  <p>
                    {text(
                      " Recalculate the passenger route and boarding buffer for the new gate. ",
                    )}
                  </p>
                ),
              )}
              <button
                className="primary"
                onClick={() => {
                  dialog.current?.close();
                  onAnalyse();
                }}
              >
                {text(" Analyse options ")}
              </button>
              <p className="note">
                {text(
                  " Operational causal assumptions, not proof. The operator remains responsible for reviewing available staff and accessible routing. ",
                )}
              </p>
            </>
          ),
        )}
      </dialog>
    </section>
  );
}
