import { useCallback, useEffect, useState } from "react";
import {
  Activity,
  ArrowRight,
  ArrowUpRight,
  Check,
  ChevronRight,
  Clock3,
  FlaskConical,
  Layers3,
  LayoutDashboard,
  Map,
  Plane,
  RefreshCw,
  ShieldCheck,
  Sparkles,
  Users,
  Route,
  History,
  Menu,
  AlertTriangle,
  Database,
} from "lucide-react";
import {
  ResponsiveContainer,
  AreaChart,
  Area,
  CartesianGrid,
  XAxis,
  YAxis,
  Tooltip,
  LineChart,
  Line,
  Legend,
} from "recharts";
import { api } from "./services/api";
import AirportMap from "./components/AirportMap";
import DataSources from "./components/DataSources";
const notice = "Simulated MVP Result — Not actual airport performance.";
const tabs = [
  { name: "Airport now", icon: Map },
  { name: "Operations control", icon: LayoutDashboard },
  { name: "What-if lab", icon: FlaskConical },
  { name: "Passenger journey", icon: Route },
  { name: "Decision log", icon: History },
  { name: "Data & sources", icon: Database },
];
const fmt = (x: number | null | undefined) =>
  x == null
    ? "Unavailable"
    : x.toLocaleString(undefined, { maximumFractionDigits: 1 });
const i18n = {
  en: { safe: "Safe time", continue: "Continue journey" },
  th: { safe: "เวลาที่เหลืออย่างปลอดภัย", continue: "เดินทางต่อ" },
};
export default function App() {
  const [tab, setTab] = useState("Airport now"),
    [horizon, setHorizon] = useState(30),
    [overview, setOverview] = useState<any>(null),
    [comparison, setComparison] = useState<any>(null),
    [audit, setAudit] = useState<any[]>([]),
    [results, setResults] = useState<any[]>([]),
    [flights, setFlights] = useState<any[]>([]);
  const [error, setError] = useState(""),
    [busy, setBusy] = useState(false),
    [message, setMessage] = useState(""),
    [lanes, setLanes] = useState(5),
    [redirect, setRedirect] = useState(12),
    [staff, setStaff] = useState(0),
    [delay, setDelay] = useState(0),
    [custom, setCustom] = useState<any>(null),
    [question, setQuestion] = useState("Why will Security A become congested?"),
    [answer, setAnswer] = useState(""),
    [accessible, setAccessible] = useState(true),
    [journey, setJourney] = useState<any>(null),
    [language, setLanguage] = useState<"en" | "th">("en"),
    [reason, setReason] = useState(
      "Reviewed staffing and passenger routing constraints.",
    ),
    [menu, setMenu] = useState(false),
    [previousSafe, setPreviousSafe] = useState<number | null>(null),
    [measured, setMeasured] = useState(12);
  const refresh = useCallback(async () => {
    const [o, c, f] = await Promise.all([
      api("/overview"),
      api("/recommendations"),
      api("/flights"),
    ]);
    setOverview(o);
    setComparison(c);
    setFlights(f);
    setJourney(
      await api("/passenger/demo-passenger/journey?accessible=" + accessible),
    );
  }, [accessible]);
  useEffect(() => {
    refresh().catch((e) => setError(e.message));
  }, [refresh]);
  useEffect(() => {
    const timer = setInterval(
      () => refresh().catch((e) => setError(e.message)),
      60000,
    );
    return () => clearInterval(timer);
  }, [refresh]);
  async function run(fn: () => Promise<void>) {
    setBusy(true);
    setError("");
    setMessage("");
    try {
      await fn();
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setBusy(false);
    }
  }
  async function demo(event: string) {
    await run(async () => {
      if (event === "gate-change")
        setPreviousSafe(journey?.safe_time_min ?? null);
      if (event === "reset") {
        setPreviousSafe(null);
        setCustom(null);
      }
      await api("/demo/event", { event });
      await refresh();
      setMessage(
        event === "reset"
          ? "Demo reset to 17:00. Audit history retained."
          : "Demo event applied. Forecast and passenger route recalculated.",
      );
    });
  }
  async function decide(option: any, decision: string) {
    await run(async () => {
      await api("/recommendations/" + option.recommendation_id + "/decision", {
        decision,
        reason,
        ...(decision === "override"
          ? {
              intervention: {
                lanes,
                redirect: redirect / 100,
                staff: 0,
                flight_delay: 0,
              },
            }
          : {}),
      });
      await refresh();
      setMessage(
        "Human decision recorded: " +
          decision +
          ". Demo state updated when applicable.",
      );
    });
  }
  async function changeTab(name: string) {
    setTab(name);
    setMenu(false);
    if (name === "Decision log")
      await run(async () => {
        setAudit(await api("/audit"));
        setResults(await api("/results"));
      });
  }
  if (!overview)
    return (
      <main className="loading">
        <Layers3 size={42} />
        <h1>Airport TimeTwin</h1>
        <p role="status">{error || "Connecting to the airport twin…"}</p>
        <button onClick={() => run(refresh)}>Retry connection</button>
      </main>
    );
  const a = overview.checkpoints[0],
    best = comparison?.options.find(
      (x: any) => x.name === comparison.recommended,
    ),
    base = comparison?.options[0],
    stale = overview.scenario.stale;
  const chart =
    base?.series.map((x: any, i: number) => ({
      minute: x.minute,
      "No action": x.wait_a,
      "Open A5": comparison.options[1].series[i].wait_a,
      "Redirect 20%": comparison.options[2].series[i].wait_a,
      Combined: comparison.options[3].series[i].wait_a,
      ...(custom ? { Custom: custom.series[i].wait_a } : {}),
    })) || [];
  const compareChart = (
    <ResponsiveContainer width="100%" height={260}>
      <LineChart data={chart}>
        <CartesianGrid
          strokeDasharray="3 4"
          vertical={false}
          stroke="#e4e9e5"
        />
        <XAxis
          dataKey="minute"
          tickLine={false}
          axisLine={false}
          label={{
            value: "Minutes from scenario time",
            position: "insideBottom",
            offset: -3,
          }}
          height={45}
        />
        <YAxis unit="m" axisLine={false} tickLine={false} />
        <Tooltip />
        <Legend />
        <Line
          dataKey="No action"
          stroke="#b6553d"
          dot={false}
          strokeWidth={2}
        />
        <Line dataKey="Open A5" stroke="#bba14b" dot={false} />
        <Line dataKey="Redirect 20%" stroke="#6b8dae" dot={false} />
        <Line dataKey="Combined" stroke="#21806a" dot={false} strokeWidth={3} />
        {custom && <Line dataKey="Custom" stroke="#8d63ac" dot={false} />}
      </LineChart>
    </ResponsiveContainer>
  );
  return (
    <div className="app">
      <aside className={menu ? "sidebar expanded" : "sidebar"}>
        <a className="brand" href="#" aria-label="Airport TimeTwin home">
          <div className="brand-icon">
            <Layers3 size={23} />
          </div>
          <span>
            Airport<span className="brand-light">TimeTwin</span>
          </span>
        </a>
        <div className="workspace">
          <span className="airport-icon">
            <Plane size={18} />
          </span>
          <div>
            Illustrative airport
            <small>Terminal 1 · Synthetic environment</small>
          </div>
        </div>
        <div className="nav-label">WORKSPACE</div>
        <nav>
          {tabs.map(({ name, icon: Icon }) => (
            <button
              key={name}
              className={tab === name ? "nav active" : "nav"}
              onClick={() => changeTab(name)}
            >
              <Icon size={18} />
              {name}
              {tab === name && <span className="nav-dot" />}
            </button>
          ))}
        </nav>
        <div className="sidebar-bottom">
          <div className="mode">
            <span className="pulse" />
            <span>
              Decision support mode<small>Human approval required</small>
            </span>
          </div>
          <div className="profile">
            <div className="avatar">OP</div>
            <div>
              Demo operator<small>AIRPORT_OPERATOR · Demo auth</small>
            </div>
          </div>
        </div>
      </aside>
      <div className="main">
        <header className="topbar">
          <div>
            <button
              className="mobile-menu"
              aria-label="Open navigation"
              onClick={() => setMenu(!menu)}
            >
              <Menu />
            </button>
            <span className="crumb">Workspace</span>
            <ChevronRight size={14} />
            <strong>{tab}</strong>
          </div>
          <div className="header-right">
            <div className="experience-switch">
              <button
                className={tab !== "Passenger journey" ? "selected" : ""}
                onClick={() => setTab("Airport now")}
              >
                Operations
              </button>
              <button
                className={tab === "Passenger journey" ? "selected" : ""}
                onClick={() => setTab("Passenger journey")}
              >
                Passenger
              </button>
            </div>
            <span className="tag">SYNTHETIC DEMO</span>
            <span className="time">
              <Clock3 size={14} />
              17:00 ICT <span className="muted">/ frozen clock</span>
            </span>
          </div>
        </header>
        <main className="content" key={tab}>
          <div className="title-row">
            <div>
              <div className="eyebrow">PREDICT. COMPARE. ACT.</div>
              <h1>
                {tab === "Airport now"
                  ? "See the next bottleneck."
                  : tab === "Operations control"
                    ? "Turn foresight into action."
                    : tab === "What-if lab"
                      ? "Test the decision first."
                      : tab === "Passenger journey"
                        ? "Your time, with confidence."
                        : tab === "Data & sources"
                          ? "Trust starts with the source."
                          : "Every decision, accountable."}
              </h1>
              <p className="subtitle">
                {tab === "Airport now"
                  ? "A connected view of passenger flow — now and one step ahead."
                  : tab === "Passenger journey"
                    ? "A personalized route through an illustrative terminal."
                    : "Explainable intelligence for a human in control."}
              </p>
            </div>
            <button
              className="secondary"
              disabled={busy}
              onClick={() => demo("reset")}
            >
              <RefreshCw size={15} />
              Reset demo
            </button>
          </div>
          <div className="provenance">
            <ShieldCheck size={15} />
            <span>{notice}</span>
            <span className="provenance-right">{overview.data_status}</span>
          </div>
          {error && (
            <div className="error" role="alert">
              <AlertTriangle size={18} />
              {error}
              <button onClick={() => run(refresh)}>Retry</button>
            </div>
          )}
          {message && (
            <div className="success" role="status">
              {message}
            </div>
          )}
          {busy && (
            <div className="working" role="status">
              Updating the twin…
            </div>
          )}
          <details className="scenario-drawer" open>
            <summary>
              <FlaskConical size={14} />
              <span>Demo scenario studio</span>
              <small>Reset, create an event, and see what changes</small>
              <ChevronRight size={14} />
            </summary>
            <div className="demo-controls">
              <span>SCENARIO CONTROLS</span>
              <button disabled={busy} onClick={() => demo("peak")}>
                Start peak event
              </button>
              <button disabled={busy} onClick={() => demo("lane-closure")}>
                Lane closure
              </button>
              <button disabled={busy} onClick={() => demo("gate-change")}>
                Gate C8 → E7
              </button>
              <button
                disabled={busy}
                onClick={() => demo(stale ? "refresh" : "stale")}
              >
                {stale ? "Refresh feed" : "Test stale feed"}
              </button>
              <button disabled={busy} onClick={() => run(refresh)}>
                Run recommendation
              </button>
            </div>
          </details>
          {(tab === "Airport now" || tab === "Operations control") && (
            <>
              <section className="metrics">
                <Metric
                  label="SECURITY A · NOW"
                  value={fmt(a.current_wait)}
                  unit="min"
                  detail={`${a.open_lanes} of 5 lanes available`}
                  icon={<Clock3 size={17} />}
                />
                <Metric
                  label="FORECAST · +30 MIN"
                  value={`${a.forecast[1].lower_bound}–${a.forecast[1].upper_bound}`}
                  unit="min"
                  detail="Assumed uncertainty interval"
                  icon={<Activity size={17} />}
                  attention={overview.scenario.peak}
                />
                <Metric
                  label="POTENTIAL TIME SAVED"
                  value={fmt(best?.passenger_minutes_saved)}
                  unit="pax·min"
                  detail="Whole security network · simulated"
                  icon={<Users size={17} />}
                />
                <Metric
                  label="FORECAST CONFIDENCE"
                  value={stale ? "35" : "80"}
                  unit="%"
                  detail="Heuristic · not yet calibrated"
                  icon={<ShieldCheck size={17} />}
                />
              </section>
              <div className="primary-grid">
                <section className="panel map-panel">
                  <div className="panel-heading">
                    <div>
                      <h2>
                        Airport flow twin{" "}
                        <span className="tiny-tag">ILLUSTRATIVE</span>
                      </h2>
                      <p>
                        Choose a horizon to reveal pressure across the terminal.
                      </p>
                    </div>
                    <span className="map-status">
                      <span className="pulse" />
                      Model connected
                    </span>
                  </div>
                  <div className="time-selector">
                    <span>FORECAST HORIZON</span>
                    <div>
                      {[0, 15, 30, 60].map((h) => (
                        <button
                          aria-pressed={horizon === h}
                          className={horizon === h ? "selected" : ""}
                          key={h}
                          onClick={() => setHorizon(h)}
                        >
                          {h === 0 ? "Now" : `+${h} min`}
                        </button>
                      ))}
                    </div>
                  </div>
                  <AirportMap
                    checkpoints={overview.checkpoints}
                    horizon={horizon}
                    gate={overview.scenario.gate}
                    onCompare={() => setTab("What-if lab")}
                  />
                  <div className="map-legend">
                    <span>
                      <i className="green" />
                      Healthy
                    </span>
                    <span>
                      <i className="yellow" />
                      Attention
                    </span>
                    <span>
                      <i className="orange" />
                      Rising risk
                    </span>
                    <span>
                      <i className="red" />
                      Intervention needed
                    </span>
                  </div>
                  <div className="map-footer">
                    <Map size={14} />
                    Topology assumption · not a real airport map{" "}
                    <span>Routing uses directed, accessible edges</span>
                  </div>
                </section>
                <section className="panel priority">
                  <div className="priority-accent" />
                  <div className="panel-heading">
                    <h2>Priority insight</h2>
                    <span
                      className={
                        overview.scenario.peak ? "risk-tag" : "neutral-tag"
                      }
                    >
                      {overview.scenario.peak
                        ? "↑ RISING PRESSURE"
                        : "MONITORING"}
                    </span>
                  </div>
                  <div className="priority-zone">
                    <div className="shield-icon">
                      <ShieldCheck size={26} />
                    </div>
                    <div>
                      <h3>Security A</h3>
                      <p>Departure processing</p>
                    </div>
                  </div>
                  <div className="forecast-jump">
                    <div>
                      <small>NOW</small>
                      <strong>
                        {fmt(a.current_wait)}
                        <span>min</span>
                      </strong>
                    </div>
                    <ArrowRight size={24} />
                    <div>
                      <small>IN 30 MINUTES</small>
                      <strong
                        className={overview.scenario.peak ? "orange-text" : ""}
                      >
                        {fmt(a.forecast[1].predicted_wait_min)}
                        <span>min</span>
                      </strong>
                    </div>
                  </div>
                  <p className="insight-copy">
                    {overview.scenario.peak
                      ? "A synthetic departure wave exceeds the capacity of four open lanes. Pressure builds before the next boarding window."
                      : "The normal arrival profile clears the initial queue. Start the peak event to explore a departure-wave intervention."}
                  </p>
                  <div className="drivers-title">
                    MODELLED DRIVERS <span>ASSUMPTION</span>
                  </div>
                  <div className="driver">
                    <span>Departure-wave demand</span>
                    <strong>
                      {overview.scenario.peak ? "15.2" : "5"} pax/min
                    </strong>
                  </div>
                  <div className="driver">
                    <span>Available processing capacity</span>
                    <strong>{a.open_lanes * 2} pax/min</strong>
                  </div>
                  <div className="recommendation-mini">
                    <span>
                      <Sparkles size={14} /> BEST FEASIBLE ACTION
                    </span>
                    <strong>
                      {comparison?.recommended || "Blocked — stale data"}
                    </strong>
                    <small>
                      {best
                        ? `${best.additional_staff} additional staff · ${best.walking_penalty} min walking penalty per pax`
                        : "Refresh the feed to continue."}
                    </small>
                  </div>
                  <button
                    className="primary full"
                    onClick={() => setTab("What-if lab")}
                  >
                    Compare interventions
                    <ArrowUpRight size={16} />
                  </button>
                </section>
              </div>
              <div className="bottom-grid">
                <section className="panel">
                  <div className="panel-heading">
                    <div>
                      <h2>Pressure over the next hour</h2>
                      <p>Security A virtual wait · deterministic simulation</p>
                    </div>
                    <span className="tiny-tag">MINUTES</span>
                  </div>
                  <ResponsiveContainer width="100%" height={220}>
                    <AreaChart data={base?.series || []}>
                      <defs>
                        <linearGradient
                          id="waitFill"
                          x1="0"
                          y1="0"
                          x2="0"
                          y2="1"
                        >
                          <stop
                            offset="0%"
                            stopColor="#b77750"
                            stopOpacity={0.22}
                          />
                          <stop
                            offset="100%"
                            stopColor="#b77750"
                            stopOpacity={0}
                          />
                        </linearGradient>
                      </defs>
                      <CartesianGrid
                        strokeDasharray="3 4"
                        vertical={false}
                        stroke="#e4e9e5"
                      />
                      <XAxis
                        dataKey="minute"
                        tickLine={false}
                        axisLine={false}
                        unit="m"
                      />
                      <YAxis axisLine={false} tickLine={false} />
                      <Tooltip />
                      <Area
                        dataKey="wait_a"
                        name="Predicted wait"
                        type="monotone"
                        stroke="#b77750"
                        fill="url(#waitFill)"
                        strokeWidth={2}
                      />
                    </AreaChart>
                  </ResponsiveContainer>
                </section>
                <section className="panel">
                  <div className="panel-heading">
                    <div>
                      <h2>Departure wave</h2>
                      <p>
                        Four synthetic flights · 580 anonymous journey fixtures
                      </p>
                    </div>
                    <Plane size={18} />
                  </div>
                  <div className="flight-table">
                    <div className="flight-row table-head">
                      <span>FLIGHT</span>
                      <span>GATE</span>
                      <span>DEPARTURE · ICT</span>
                    </div>
                    {flights.map((f) => (
                      <div className="flight-row" key={f.id}>
                        <strong>
                          <Plane size={14} />
                          {f.flight_number}
                        </strong>
                        <span>{f.gate}</span>
                        <span>
                          {new Date(f.scheduled_departure).toLocaleTimeString(
                            "en-GB",
                            {
                              timeZone: "Asia/Bangkok",
                              hour: "2-digit",
                              minute: "2-digit",
                            },
                          )}
                          <small className="tiny-tag">SYNTHETIC</small>
                        </span>
                      </div>
                    ))}
                  </div>
                </section>
              </div>
              {tab === "Operations control" && (
                <section className="panel section-gap">
                  <div className="panel-heading">
                    <h2>Operational cause graph</h2>
                    <span className="tiny-tag">NOT CAUSAL PROOF</span>
                  </div>
                  <div className="cause-flow">
                    <span>
                      Departure wave
                      <br />
                      <small>Synthetic schedule profile</small>
                    </span>
                    <ArrowRight />
                    <span>
                      Arrivals exceed capacity
                      <br />
                      <small>Operational causal assumption</small>
                    </span>
                    <ArrowRight />
                    <span>
                      Queue accumulation
                      <br />
                      <small>Derived queue balance</small>
                    </span>
                    <ArrowRight />
                    <span>
                      Journey risk
                      <br />
                      <small>Assumed checkpoint budget</small>
                    </span>
                  </div>
                  <div className="cause-contributions">
                    {overview.root_causes?.drivers.map((driver: any) => (
                      <div key={driver.name}>
                        <span className="tiny-tag">{driver.rank}</span>
                        <strong>{driver.name}</strong>
                        <span>
                          {driver.contribution_percent === null
                            ? "No excess wait"
                            : `${driver.contribution_percent}% · ${driver.wait_contribution_min} min`}
                        </span>
                      </div>
                    ))}
                  </div>
                  <p className="note">
                    Two-factor Shapley attribution inside the simulation
                    compares departure demand and lane availability against
                    normal demand with five lanes. Percentages explain modelled
                    excess wait, not real-world causation. Weather remains
                    contextual only.
                  </p>
                </section>
              )}
            </>
          )}
          {tab === "What-if lab" && (
            <>
              <div className="lab-intro">
                <div>
                  <FlaskConical size={22} />
                  <div>
                    <h2>One scenario. Four possible futures.</h2>
                    <p>
                      Compare the same arrivals across both checkpoints. Reserve
                      staff: 4 · max lanes: 5 · eligible redirect: 30%.
                    </p>
                  </div>
                </div>
                <span className="tiny-tag">DETERMINISTIC · REPRODUCIBLE</span>
              </div>
              <section className="options">
                {comparison?.options.map((o: any) => (
                  <article
                    className={
                      "panel option " +
                      (o.name === comparison.recommended ? "recommended" : "")
                    }
                    key={o.name}
                  >
                    {o.name === comparison.recommended && (
                      <div className="recommended-ribbon">
                        <Check size={13} />
                        RECOMMENDED
                      </div>
                    )}
                    <h3>{o.name}</h3>
                    <div className="option-value">
                      {fmt(o.average_wait)}
                      <span>min avg wait</span>
                    </div>
                    <dl>
                      <div>
                        <dt>P95 cohort wait</dt>
                        <dd>{fmt(o.p95_wait)} min</dd>
                      </div>
                      <div>
                        <dt>Peak network queue</dt>
                        <dd>{fmt(o.peak_queue)} pax</dd>
                      </div>
                      <div>
                        <dt>Passenger minutes saved</dt>
                        <dd>{fmt(o.passenger_minutes_saved)}</dd>
                      </div>
                      <div>
                        <dt>Additional staff</dt>
                        <dd>{o.additional_staff}</dd>
                      </div>
                      <div>
                        <dt>Walking penalty / pax</dt>
                        <dd>{o.walking_penalty} min</dd>
                      </div>
                      <div>
                        <dt>Risk proxy (&gt;35m)</dt>
                        <dd>{fmt(o.missed_flight_risk * 100)}%</dd>
                      </div>
                      <div>
                        <dt>Cost proxy / score</dt>
                        <dd>
                          {fmt(o.cost_proxy)} / {fmt(o.score)}
                        </dd>
                      </div>
                    </dl>
                    <button
                      className={
                        o.name === comparison.recommended
                          ? "primary full"
                          : "secondary full"
                      }
                      disabled={busy || stale || !o.feasible}
                      onClick={() => decide(o, "accept")}
                    >
                      Accept {o.name === "No Action" ? "no action" : "action"}
                      <ArrowRight size={14} />
                    </button>
                    <button
                      className="text-button"
                      disabled={busy}
                      onClick={() => decide(o, "reject")}
                    >
                      Reject option
                    </button>
                  </article>
                ))}
              </section>
              <div className="bottom-grid">
                <section className="panel">
                  <div className="panel-heading">
                    <div>
                      <h2>Security A · forecast comparison</h2>
                      <p>
                        Network metrics above include Security B and extra
                        walking.
                      </p>
                    </div>
                  </div>
                  {compareChart}
                  <p className="note">{comparison?.reason}</p>
                </section>
                <section className="panel custom-panel">
                  <h2>Build a custom intervention</h2>
                  <label>
                    Open lanes at Security A <strong>{lanes}</strong>
                    <input
                      aria-label="Open lanes"
                      type="range"
                      min="0"
                      max="5"
                      value={lanes}
                      onChange={(e) => setLanes(+e.target.value)}
                    />
                  </label>
                  <label>
                    Redirect eligible passengers <strong>{redirect}%</strong>
                    <input
                      aria-label="Redirect percentage"
                      type="range"
                      min="0"
                      max="30"
                      value={redirect}
                      onChange={(e) => setRedirect(+e.target.value)}
                    />
                  </label>
                  <div className="input-pair">
                    <label>
                      Extra staff
                      <input
                        aria-label="Extra staff"
                        type="number"
                        min="0"
                        max="4"
                        value={staff}
                        onChange={(e) => setStaff(+e.target.value)}
                      />
                    </label>
                    <label>
                      Wave delay (min)
                      <input
                        aria-label="Flight delay"
                        type="number"
                        min="0"
                        max="30"
                        value={delay}
                        onChange={(e) => setDelay(+e.target.value)}
                      />
                    </label>
                  </div>
                  <button
                    className="primary full"
                    disabled={busy || stale}
                    onClick={() =>
                      run(async () => {
                        setCustom(
                          await api("/simulation", {
                            lanes,
                            redirect: redirect / 100,
                            staff,
                            flight_delay: delay,
                          }),
                        );
                      })
                    }
                  >
                    <FlaskConical size={16} />
                    Run custom simulation
                  </button>
                  {custom && (
                    <p role="status" className="success">
                      Custom: {custom.average_wait} min average ·{" "}
                      {fmt(custom.passenger_minutes_saved)} pax·min saved ·{" "}
                      {custom.feasible
                        ? "Feasible"
                        : "Unserved queue — not actionable"}
                    </p>
                  )}
                </section>
              </div>
              <section className="panel section-gap">
                <h2>Human decision & transparent scoring</h2>
                <p className="note">
                  Score = wait reduction + 0.01 × passenger minutes saved + 50 ×
                  risk reduction − staff − walking penalty − 0.001 × cost. All
                  weights are configurable through POST
                  /api/recommendations/score.
                </p>
                <label>
                  Decision reason
                  <input
                    aria-label="Decision reason"
                    value={reason}
                    onChange={(e) => setReason(e.target.value)}
                    maxLength={400}
                  />
                </label>
                <button
                  className="secondary"
                  disabled={busy || stale || !best}
                  onClick={() => decide(best, "override")}
                >
                  Override recommendation with custom lanes & redirect
                </button>
                <p className="note">
                  Overrides apply only lane and redirect settings. Extra staff
                  and flight delays remain simulation-only. An accepted action
                  updates this demo, never airport equipment.
                </p>
              </section>
            </>
          )}
          {tab === "Passenger journey" && journey && (
            <div className="passenger-layout">
              <section className="passenger-card">
                <div className="passenger-top">
                  <span>
                    <Plane size={18} />
                    TT401 · Synthetic Airways
                  </span>
                  <select
                    aria-label="Language"
                    value={language}
                    onChange={(e) => setLanguage(e.target.value as "en" | "th")}
                  >
                    <option value="en">EN</option>
                    <option value="th">ไทย</option>
                  </select>
                </div>
                <div className="boarding">
                  <div>
                    <small>BOARDING DEADLINE</small>
                    <strong>{journey.boarding_deadline}</strong>
                  </div>
                  <div>
                    <small>GATE</small>
                    <strong>{journey.gate}</strong>
                  </div>
                </div>
                <div
                  className={
                    "safe-time " + (journey.safe_time_min < 15 ? "urgent" : "")
                  }
                >
                  <span>{i18n[language].safe}</span>
                  <div>
                    {previousSafe !== null && <del>{previousSafe}</del>}
                    <strong>{journey.safe_time_min}</strong>
                    <small>MINUTES</small>
                  </div>
                  <span className="safe-status">
                    {stale ? "DATA STALE — LOW CONFIDENCE" : journey.risk_level}
                  </span>
                  <p>
                    {stale
                      ? "Refresh data before relying on this guidance."
                      : journey.action}
                  </p>
                </div>
                <dl className="journey-breakdown">
                  <div>
                    <dt>Current location</dt>
                    <dd>{journey.current_node}</dd>
                  </div>
                  <div>
                    <dt>Remaining processing</dt>
                    <dd>{journey.processing_time_min} min</dd>
                  </div>
                  <div>
                    <dt>Walking to gate</dt>
                    <dd>{journey.walking_time_min} min</dd>
                  </div>
                  <div>
                    <dt>Safety buffer</dt>
                    <dd>{journey.safety_buffer_min} min</dd>
                  </div>
                </dl>
                <label className="checkbox">
                  <input
                    type="checkbox"
                    checked={accessible}
                    onChange={(e) => setAccessible(e.target.checked)}
                  />
                  Step-free, accessible route
                </label>
                <button
                  className="primary full"
                  disabled={busy || stale}
                  onClick={() =>
                    run(async () => {
                      setJourney(
                        await api(
                          "/passenger/demo-passenger/journey?accessible=" +
                            accessible,
                        ),
                      );
                      setMessage(
                        "Route refreshed. Follow the steps shown beside your Safe Time.",
                      );
                    })
                  }
                >
                  {i18n[language].continue}
                  <ArrowRight size={16} />
                </button>
                <small className="passenger-disclaimer">{notice}</small>
              </section>
              <div>
                <section className="panel">
                  <div className="panel-heading">
                    <div>
                      <h2>Your recommended route</h2>
                      <p>
                        Anonymous passenger · no personal information stored
                      </p>
                    </div>
                    <Route size={20} />
                  </div>
                  <ol className="route-steps">
                    {journey.path.map((node: string, i: number) => (
                      <li key={node}>
                        <span>{i + 1}</span>
                        <div>
                          <strong>{node}</strong>
                          <small>
                            {i === 0
                              ? "You are here"
                              : i === journey.path.length - 1
                                ? "Boarding destination"
                                : "Accessible route segment"}
                          </small>
                        </div>
                        {i === journey.path.length - 1 && <Plane size={18} />}
                      </li>
                    ))}
                  </ol>
                  <p className="note">
                    Safe Time = 64 minutes until boarding − remaining journey −
                    10-minute buffer. Scenario clock is frozen at 17:00; times
                    and route are simulated.
                  </p>
                </section>
                <section className="panel section-gap">
                  <h2>A changed gate. A new plan.</h2>
                  <p>
                    Reset the demo, then change C8 to E7 to reproduce Safe Time
                    34 → 11 minutes on the accessible route. During a peak
                    event, values adjust to the active queues.
                  </p>
                  <button
                    className="secondary"
                    disabled={busy}
                    onClick={() => demo("gate-change")}
                  >
                    Simulate gate change
                    <ArrowRight size={15} />
                  </button>
                </section>
              </div>
            </div>
          )}
          {tab === "Decision log" && (
            <>
              <section className="panel">
                <div className="panel-heading">
                  <div>
                    <h2>Measure the intervention</h2>
                    <p>
                      Append a synthetic observed mean wait to quantify forecast
                      error. Never represented as airport telemetry.
                    </p>
                  </div>
                </div>
                <label>
                  Simulated observed average wait (minutes)
                  <input
                    aria-label="Observed wait"
                    type="number"
                    min="0"
                    max="600"
                    value={measured}
                    onChange={(e) => setMeasured(+e.target.value)}
                  />
                </label>
                {results.length === 0 ? (
                  <p className="empty">
                    Accept an intervention to create a measurement record.
                  </p>
                ) : (
                  results.map((r) => (
                    <div className="result-row" key={r.id}>
                      <span>
                        Predicted {r.after_predicted} min ·{" "}
                        {r.after_actual === null
                          ? "Awaiting measurement"
                          : `Observed ${r.after_actual} min · error ${r.prediction_error} min`}
                      </span>
                      <button
                        disabled={busy || r.after_actual !== null}
                        onClick={() =>
                          run(async () => {
                            await api("/results/" + r.id + "/measure", {
                              actual_average_wait: measured,
                              source_type: "SIMULATED",
                            });
                            setResults(await api("/results"));
                            setAudit(await api("/audit"));
                          })
                        }
                      >
                        Record simulated result
                      </button>
                    </div>
                  ))
                )}
              </section>
              <section className="panel section-gap">
                <div className="panel-heading">
                  <h2>Prediction & decision trail</h2>
                  <span className="tiny-tag">LATEST 100 RECORDS</span>
                </div>
                {audit.length === 0 ? (
                  <p className="empty">No recorded decisions yet.</p>
                ) : (
                  audit.map((x) => (
                    <details className="audit-row" key={x.id}>
                      <summary>
                        <span className="audit-icon">
                          <History size={16} />
                        </span>
                        <strong>{x.result}</strong>
                        <time>
                          {new Date(x.timestamp).toLocaleTimeString()}
                        </time>
                        <span>{x.human_decision || "System"}</span>
                      </summary>
                      <pre>{JSON.stringify(x, null, 2)}</pre>
                    </details>
                  ))
                )}
              </section>
            </>
          )}
          {tab === "Data & sources" && <DataSources />}
          <section className="copilot panel">
            <div className="copilot-heading">
              <div className="spark">
                <Sparkles size={20} />
              </div>
              <div>
                <h2>Ask the operations copilot</h2>
                <p>
                  Grounded in this scenario’s structured calculations. No LLM
                  required.
                </p>
              </div>
              <span className="tiny-tag">DETERMINISTIC FALLBACK</span>
            </div>
            <form
              onSubmit={(e) => {
                e.preventDefault();
                run(async () => {
                  setAnswer((await api("/copilot/query", { question })).answer);
                });
              }}
            >
              <input
                aria-label="Copilot question"
                value={question}
                onChange={(e) => setQuestion(e.target.value)}
                maxLength={500}
              />
              <button className="primary" disabled={busy}>
                Ask copilot
                <ArrowRight size={15} />
              </button>
            </form>
            {answer && (
              <p className="copilot-answer" role="status">
                {answer}
              </p>
            )}
          </section>
          <footer>
            <span>
              Airport TimeTwin{" "}
              <span className="muted">/ Decision & simulation layer</span>
            </span>
            <span>OBSERVE → PREDICT → SIMULATE → ACT → MEASURE</span>
          </footer>
        </main>
      </div>
    </div>
  );
}
function Metric({ label, value, unit, detail, icon, attention = false }: any) {
  return (
    <article className={"metric " + (attention ? "attention" : "")}>
      <div className="metric-label">
        {label}
        {icon}
      </div>
      <div className="metric-value">
        {value}
        <span>{unit}</span>
      </div>
      <p>{detail}</p>
    </article>
  );
}
