import { text } from "../i18n";
import { useRef, useState } from "react";
import { api } from "../services/api";
import { ResourceEfficiency } from "./PilotPanels";
const steps = [
  "Normal operation",
  "Departure wave begins",
  "Future congestion detected",
  "Compare interventions",
  "Recommended response",
  "Human approval",
  "Passenger Safe Time",
  "Gate change / journey re-plan",
  "Measured impact",
];
export default function GuidedDemo({
  refresh,
  overview,
  journey,
}: {
  refresh: () => Promise<void>;
  overview: any;
  comparison: any;
  journey: any;
}) {
  const [step, setStep] = useState(-1),
    [busy, setBusy] = useState(false),
    [error, setError] = useState(""),
    [measurement, setMeasurement] = useState<any>(null);
  const selected = useRef<any>(null),
    options = useRef<any[]>([]),
    result = useRef<any>(null),
    beforeJourney = useRef<any>(null);
  async function advance(next: number) {
    setBusy(true);
    setError("");
    try {
      if (next === 0) {
        await api("/demo/event", { event: "reset" });
        await api("/demo/event", { event: "normal" });
        setMeasurement(null);
      }
      if (next === 1) await api("/demo/event", { event: "peak" });
      if (next === 3 || next === 4) {
        const c = await api("/recommendations");
        options.current = c.options;
        selected.current = c.options.find((x: any) => x.name === c.recommended);
        if (!selected.current)
          throw Error("No feasible recommendation. Reset the demo.");
      }
      if (next === 5) {
        await api(
          "/recommendations/" +
            selected.current.recommendation_id +
            "/decision",
          {
            decision: "accept",
            reason:
              "Demo Operator reviewed staffing and eligible routes in presentation mode.",
          },
        );
        result.current = (await api("/results"))[0];
      }
      if (next === 6)
        beforeJourney.current = await api("/passenger/demo-passenger/journey");
      if (next === 7) await api("/demo/event", { event: "gate-change" });
      if (next === 8)
        setMeasurement(
          await api("/results/" + result.current.id + "/measure", {}),
        );
      await refresh();
      setStep(next);
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setBusy(false);
    }
  }
  const a = overview.checkpoints[0];
  return (
    <section className="story-mode" aria-label={text("Guided demo")}>
      <aside>
        <span className="eyebrow">{text("GUIDED DEMONSTRATION")}</span>
        <ol>
          {text(
            steps.map((s, i) => (
              <li key={s} aria-current={i === step ? "step" : undefined}>
                <span>{text(String(i + 1).padStart(2, "0"))}</span>
                {text(s)}
              </li>
            )),
          )}
        </ol>
      </aside>
      <div className="story-stage">
        <span className="tiny-tag">
          {text("SIMULATED MVP RESULT — NOT ACTUAL AIRPORT PERFORMANCE")}
        </span>
        <h2>
          {text(step < 0 ? "From foresight to passenger action" : steps[step])}
        </h2>
        {text(
          step < 3 && (
            <div className="story-numbers">
              <div>
                <small>{text("Security A · now")}</small>
                <strong>
                  {text(a.current_wait)}
                  <small>{text("min")}</small>
                </strong>
              </div>
              <div>
                <small>{text("+30 min forecast")}</small>
                <strong>
                  {text(a.forecast[1].predicted_wait_min)}
                  <small>{text("min")}</small>
                </strong>
              </div>
            </div>
          ),
        )}
        {text(
          step === 2 && (
            <p>
              {text("580 representative synthetic flight passengers · ")}
              {text(a.forecast[1].confidence * 100)}
              {text("% heuristic confidence · Not calibrated.")}
            </p>
          ),
        )}
        {text(
          step === 3 && (
            <div className="story-options">
              {text(
                options.current.map((o: any) => (
                  <div key={o.name}>
                    <h3>{text(o.name)}</h3>
                    <strong>
                      {text(o.series[29].wait_a)}
                      {text(" min")}
                    </strong>
                    <p>{text("Security A · +30")}</p>
                    <p>
                      {text("Network P95: ")}
                      {text(o.p95_wait)}
                      {text(" min")}
                    </p>
                  </div>
                )),
              )}
            </div>
          ),
        )}
        {text(
          (step === 4 || step === 5) && (
            <>
              <h3>{text(selected.current?.name)}</h3>
              <p>
                {text("Additional staff: ")}
                {text(selected.current?.additional_staff)}
                {text(" · Extra walking: ")}
                {text(selected.current?.walking_penalty)}
                {text(" min per network passenger.")}
              </p>
              <p>
                {text(
                  step === 4
                    ? "Human approval is required before the simulated intervention is applied."
                    : "Approved by Demo Operator. Applied to this session only. No airport equipment is controlled.",
                )}
              </p>
            </>
          ),
        )}
        {text(
          (step === 6 || step === 7) && (
            <>
              <div className="story-numbers">
                <div>
                  <small>{text("Safe Time")}</small>
                  <strong>
                    {text(
                      step === 7
                        ? `${beforeJourney.current?.safe_time_min} → ${journey.safe_time_min}`
                        : journey.safe_time_min,
                    )}
                    <small>{text("min")}</small>
                  </strong>
                </div>
              </div>
              <h3>
                {text(journey.risk_level)}
                {text(" · Gate ")}
                {text(journey.gate)}
              </h3>
              <p>{text(journey.path.join(" → "))}</p>
              <p>
                {text("Walking: ")}
                {text(journey.walking_time_min)}
                {text(" min · Processing: ")}
                {text(journey.processing_time_min)}
                {text(" min · Buffer: ")}
                {text(journey.safety_buffer_min)}
                {text(" min")}
              </p>
            </>
          ),
        )}
        {text(
          step === 8 && (
            <>
              <div className="story-numbers">
                <div>
                  <small>{text("Predicted mean wait")}</small>
                  <strong>
                    {text(measurement?.after_predicted)}
                    <small>{text("min")}</small>
                  </strong>
                </div>
                <div>
                  <small>{text("Observed simulated mean")}</small>
                  <strong>
                    {text(measurement?.after_actual)}
                    <small>{text("min")}</small>
                  </strong>
                </div>
              </div>
              <p>
                {text("Forecast error: ")}
                {text(measurement?.prediction_error)}
                {text(
                  " min. Deterministic replay uses 97% of planned service throughput (ASSUMPTION), not real telemetry.",
                )}
              </p>
              <ResourceEfficiency impact={overview.impact} />
              <a href="/app/audit">{text("View decision lifecycle →")}</a>
            </>
          ),
        )}
        {text(error && <p role="alert">{text(error)}</p>)}
        <div className="hero-actions">
          <button disabled={busy} onClick={() => advance(0)}>
            {text("Start / restart guided demo")}
          </button>
          {text(
            step >= 0 && step < 8 && (
              <button
                className="primary"
                disabled={busy}
                onClick={() => advance(step + 1)}
              >
                {text(step === 4 ? "Approve demo intervention" : "Next step")}
              </button>
            ),
          )}
        </div>
        <p className="note">
          {text(
            "Presenter-controlled story. No automatic approval or hidden reset between operations and passenger actions.",
          )}
        </p>
      </div>
    </section>
  );
}
