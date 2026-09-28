import PublicContext from "./PublicContext";
import { text } from "../i18n";
import { JourneyFlow, ResourceEfficiency, ModelQuality } from "./PilotPanels";
import { useEffect, useState, useRef } from "react";
import { api } from "../services/api";
export default function ExtraPages({
  tab,
  flights,
  comparison,
  overview,
}: {
  tab: string;
  flights: any[];
  comparison: any;
  overview: any;
}) {
  const flightDialog = useRef<HTMLDialogElement>(null);
  const [filter, setFilter] = useState("All");
  const [search, setSearch] = useState(""),
    [detail, setDetail] = useState<any>(null),
    [evaluation, setEvaluation] = useState<any>(null),
    [error, setError] = useState("");
  useEffect(() => {
    if (tab === "Performance")
      api("/evaluation")
        .then((data) => setEvaluation(Array.isArray(data?.results) ? data : null))
        .catch((e) => setError(e.message));
  }, [tab]);
  const best =
      overview.impact?.proposed ||
      comparison?.options.find((x: any) => x.name === comparison.recommended),
    base = overview.impact?.baseline || comparison?.options[0];
  const visibleFlights = flights
    .filter(
      (f) =>
        filter === "All" ||
        (filter === "Departures" && f.origin === "BKK") ||
        (filter === "Arrivals" && f.destination === "BKK") ||
        (filter === "Delayed" &&
          new Date(f.estimated_departure) > new Date(f.scheduled_departure)),
    )
    .filter((f) =>
      [f.flight_number, f.origin, f.destination, f.gate]
        .join(" ")
        .toLowerCase()
        .includes(search.toLowerCase()),
    );
  return (
    <section className="panel page-extra">
      <span className="tiny-tag">
        {text(" SIMULATED MVP RESULT — NOT ACTUAL AIRPORT PERFORMANCE ")}
      </span>
      {text(
        tab === "Flights" && (
          <>
            <h2>{text("Flight operations")}</h2>
            <p>{text(" MODELLED SCENARIO FLIGHT ")}</p>
            <p>
              {text(
                "All four modelled flights share Security A despite departing from different gates.",
              )}
            </p>
            <div className="flight-filters">
              {text(
                ["All", "Departures", "Arrivals", "Delayed"].map((x) => (
                  <button
                    key={x}
                    aria-pressed={filter === x}
                    className={filter === x ? "selected" : ""}
                    onClick={() => setFilter(x)}
                  >
                    {text(x)}
                  </button>
                )),
              )}
            </div>
            <input
              className="flight-search"
              aria-label={text("Search flights")}
              placeholder={text("Search flight, route or gate")}
              value={search}
              onChange={(e) => setSearch(e.target.value)}
            />
            <div className="extra-scroll">
              <table className="data-table">
                <thead>
                  <tr>
                    <th>{text("Flight")}</th>
                    <th>{text("Route")}</th>
                    <th>{text("Departure · ICT")}</th>
                    <th>{text("Gate")}</th>
                    <th>{text("Passenger cohort")}</th>
                    <th>{text("Shared checkpoint")}</th>
                    <th>{text("Status")}</th>
                    <th>{text("Details")}</th>
                  </tr>
                </thead>
                <tbody>
                  {text(
                    visibleFlights.length === 0 && (
                      <tr>
                        <td colSpan={8}>
                          {text(
                            " No flights match these filters in the synthetic dataset. ",
                          )}
                        </td>
                      </tr>
                    ),
                  )}
                  {text(
                    visibleFlights.map((f) => (
                      <tr key={f.id}>
                        <td>{text(f.flight_number)}</td>
                        <td>
                          {text(f.origin)}
                          {text(" → ")}
                          {text(f.destination)}
                        </td>
                        <td>
                          {text(
                            new Date(f.scheduled_departure).toLocaleTimeString(
                              "en-GB",
                              {
                                timeZone: "Asia/Bangkok",
                                hour: "2-digit",
                                minute: "2-digit",
                              },
                            ),
                          )}
                        </td>
                        <td>{text(f.gate)}</td>
                        <td>{f.passenger_cohort ?? 145}</td>
                        <td>{text("Security A")}</td>
                        <td>{text(f.status)}</td>
                        <td>
                          <button
                            onClick={() =>
                              api("/flights/" + f.id + "/operations")
                                .then((data) => {
                                  setDetail(data);
                                  flightDialog.current?.showModal();
                                })
                                .catch((e) => setError(e.message))
                            }
                          >
                            {text(" View ")}
                            {text(f.flight_number)}
                          </button>
                        </td>
                      </tr>
                    )),
                  )}
                </tbody>
              </table>
            </div>
            <dialog
              ref={flightDialog}
              className="situation-dialog flight-detail-dialog"
            >
              <button onClick={() => flightDialog.current?.close()}>
                {text(" Close flight details ")}
              </button>
              {text(
                detail && (
                  <div className="flight-drawer">
                    <span className="eyebrow">
                      {text("SYNTHETIC FLIGHT OPERATIONS")}
                    </span>
                    <h2>{text(detail.flight.flight_number)}</h2>
                    <p>
                      {text(detail.flight.origin)}
                      {text(" → ")}
                      {text(detail.flight.destination)}
                      {text(" · Gate")}
                      {text(" ")}
                      {text(detail.flight.gate)}
                    </p>
                    <h3>{text("Ground activity timeline")}</h3>
                    <ol className="flight-timeline">
                      {text(
                        detail.ground_handling.map((x: any) => (
                          <li key={x.id}>
                            <time>
                              {text(
                                new Date(x.planned_start).toLocaleTimeString(
                                  "en-GB",
                                  {
                                    timeZone: "Asia/Bangkok",
                                    hour: "2-digit",
                                    minute: "2-digit",
                                  },
                                ),
                              )}
                            </time>
                            <div>
                              <strong>{text(x.activity)}</strong>
                              <small>
                                {text(x.status)}
                                {text(" · ")}
                                {text(x.source_type)}
                              </small>
                            </div>
                          </li>
                        )),
                      )}
                    </ol>
                    <p>
                      {text(" Baggage event records: ")}
                      {text(detail.baggage_events.length)}
                      {text(" · Gate event records: ")}
                      {text(detail.gate_events.length)}
                    </p>
                    <p className="note">
                      {text(
                        " Planned times are synthetic fixture values. No actual completion or flight-specific delay probability is inferred. ",
                      )}
                    </p>
                  </div>
                ),
              )}
            </dialog>
          </>
        ),
      )}
      {text(
        tab === "Passenger flow" && (
          <JourneyFlow flow={overview.journey_flow} />
        ),
      )}
      {text(
        tab === "Performance" && (
          <>
            <div className="performance-hero">
              <span className="eyebrow">
                {text(" OPERATIONAL PERFORMANCE · SIMULATED SCENARIO ")}
              </span>
              <h2>
                {text(
                  best
                    ? (
                        (base.passenger_minutes - best.passenger_minutes) /
                        60
                      ).toLocaleString(undefined, { maximumFractionDigits: 1 })
                    : "Unavailable",
                )}
              </h2>
              <strong>{text("Passenger Hours Saved")}</strong>
              <p>
                {text(
                  "Estimated benefit of the proposed or accepted scenario.",
                )}
              </p>
            </div>
            <h2>{text("Operational outcome")}</h2>
            {text(
              best && base ? (
                <div className="metrics">
                  <div className="metric">
                    <p>{text("Passenger-minutes saved")}</p>
                    <h1>
                      {text(
                        (
                          base.passenger_minutes - best.passenger_minutes
                        ).toLocaleString(),
                      )}
                    </h1>
                  </div>
                  <div className="metric">
                    <p>{text("P95 wait · minutes")}</p>
                    <h1>
                      {text(base.p95_wait.toFixed(1))}
                      {text(" → ")}
                      {text(best.p95_wait.toFixed(1))}
                    </h1>
                  </div>
                  <div className="metric">
                    <p>{text("Additional staff")}</p>
                    <h1>{text(best.additional_staff)}</h1>
                  </div>
                </div>
              ) : (
                <p>{text("No feasible recommendation available.")}</p>
              ),
            )}
            <p>
              {text(
                " One scenario comparison; not a cumulative daily total. Prediction confidence is heuristic. ",
              )}
            </p>
            <ResourceEfficiency impact={overview.impact} />
            <ModelQuality evaluation={evaluation} />
            <PublicContext />
          </>
        ),
      )}
      {text(error && <p role="alert">{text(error)}</p>)}
    </section>
  );
}
