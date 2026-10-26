import PublicContext from "./components/PublicContext";
import {
  text,
  useLanguage,
  LanguageSwitch,
  setLanguage as setGlobalLanguage,
} from "./i18n";
import { Integration, DecisionHistory } from "./components/PilotPanels";
import { useCallback, useEffect, useState, useRef } from "react";
import {
  Activity,
  ArrowRight,
  ArrowUpRight,
  Clock3,
  FlaskConical,
  Layers3,
  LayoutDashboard,
  Luggage,
  Map,
  Plane,
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
import AnimatedNumber from "./components/AnimatedNumber";
import DataSources from "./components/DataSources";
import GuidedDemo from "./components/GuidedDemo";
import ExtraPages from "./components/ExtraPages";
import ComparisonReveal from "./components/ComparisonReveal";
import DecisionWorkspace from "./components/DecisionWorkspace";
import Situations from "./components/Situations";
import BaggageControl from "./components/BaggageControl";
const routes: Record<string, string> = {
  "Airport now": "/overview",
  Baggage: "/baggage",
  "Future map": "/future",
  "Operations control": "/operations",
  "What-if lab": "/simulator",
  Flights: "/flights",
  "Passenger flow": "/passenger-flow",
  Performance: "/performance",
  "Passenger journey": "/journey",
  "Decision log": "/app/audit",
  "Data & sources": "/sources",
  "System Integration": "/integration",
};
const aliases: Record<string, string> = {
  "/app": "/overview",
  "/trustx": "/baggage",
  "/app/future": "/future",
  "/app/operations": "/operations",
  "/app/simulator": "/simulator",
  "/app/flights": "/flights",
  "/app/flow": "/passenger-flow",
  "/app/performance": "/performance",
  "/passenger/TT401": "/journey",
  "/app/sources": "/sources",
  "/trust": "/sources",
  "/audit": "/app/audit",
  "/future-flow": "/passenger-flow",
  "/passenger-journey": "/journey",
};
const routeTab = () =>
  Object.keys(routes).find(
    (k) =>
      routes[k] ===
      (aliases[window.location.pathname] || window.location.pathname),
  ) || "Airport now";
const notice = "Simulated MVP Result — Not actual airport performance.";
const tabs = [
  { name: "Airport now", icon: Map },
  { name: "Baggage", icon: Luggage },
  { name: "Future map", icon: Layers3 },
  { name: "Operations control", icon: LayoutDashboard },
  { name: "What-if lab", icon: FlaskConical },
  { name: "Flights", icon: Plane },
  { name: "Passenger flow", icon: Users },
  { name: "Performance", icon: Activity },
  { name: "Passenger journey", icon: Route },
  { name: "Decision log", icon: History },
  { name: "Data & sources", icon: Database },
  { name: "System Integration", icon: Layers3 },
];
const fmt = (x: number | null | undefined) =>
  x == null
    ? "Unavailable"
    : x.toLocaleString(undefined, { maximumFractionDigits: 1 });
const i18n = {
  en: { safe: "Safe time", continue: "Continue journey" },
  th: { safe: "เวลาที่เหลืออย่างปลอดภัย", continue: "เดินทางต่อ" },
};

function normalizeComparison(raw: any) {
  const source = Array.isArray(raw?.options) ? raw.options : [];
  const defaults = [
    { name: "No action", average_wait: 39, score: 0 },
    { name: "Open reserve lane", average_wait: 26, score: 72 },
    { name: "Redirect passengers", average_wait: 29, score: 61 },
    { name: "Combined intervention", average_wait: 18, score: 92 },
  ];
  const options = defaults.map((fallback, index) => {
    const item = source[index] || fallback;
    const average = Number(item.average_wait ?? fallback.average_wait);
    return {
      ...fallback,
      ...item,
      name: String(item.name ?? fallback.name),
      additional_staff: Number(item.additional_staff ?? item.staff ?? 0),
      walking_penalty: Number(item.walking_penalty ?? 0),
      series: Array.isArray(item.series)
        ? item.series
        : Array.from({ length: 5 }, (_, i) => ({
            minute: i * 15,
            wait_a: Math.max(5, average + Math.round((i - 2) * 2)),
          })),
    };
  });
  const recommended =
    typeof raw?.recommended === "string"
      ? raw.recommended
      : String(raw?.recommended?.name ?? options[3].name);
  return { ...raw, options, recommended };
}

function normalizeOverview(raw: any) {
  const checkpoints = Array.isArray(raw?.checkpoints) ? raw.checkpoints : [];
  return {
    ...raw,
    checkpoints: checkpoints.map((checkpoint: any) => ({
      ...checkpoint,
      forecast:
        Array.isArray(checkpoint.forecast) && checkpoint.forecast.length > 1
          ? checkpoint.forecast
          : [0, 15, 30, 45, 60].map((minute) => ({
              minute,
              predicted_wait_min: Number(checkpoint.predicted_wait_min ?? 0),
              lower_bound: Math.max(0, Number(checkpoint.predicted_wait_min ?? 0) - 5),
              upper_bound: Number(checkpoint.predicted_wait_min ?? 0) + 5,
              confidence: 0.72,
            })),
    })),
    journey_flow:
      raw?.journey_flow && Array.isArray(raw.journey_flow.plans)
        ? raw.journey_flow
        : {
            plans: [15, 30, 60].map((horizon) => ({
              horizon,
              security_a: 280,
              security_b: 90,
            })),
          },
  };
}

function normalizeJourney(raw: any) {
  const path = Array.isArray(raw?.path) && raw.path.length ? raw.path : ["Food C", "Security A", "Airside", "Gate C8"];
  const segments = Array.isArray(raw?.segments) ? raw.segments : [];
  return {
    ...raw,
    path,
    segments: path.slice(1).map((_: string, index: number) => ({
      walking_min: Number(segments[index]?.walking_min ?? (index === 0 ? 2 : 5)),
      processing_min: Number(segments[index]?.processing_min ?? (index === 0 ? 12 : 0)),
    })),
  };
}

export default function App() {
  const activeLanguage = useLanguage();
  const demoDialog = useRef<HTMLDialogElement>(null);
  const initialization = useRef<Promise<unknown> | null>(null);
  const copilotDialog = useRef<HTMLDialogElement>(null);
  const [presentation, setPresentation] = useState(false);
  const [tab, setTab] = useState(routeTab),
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
    [reason, setReason] = useState(
      "Reviewed staffing and passenger routing constraints.",
    ),
    [menu, setMenu] = useState(false),
    [previousSafe, setPreviousSafe] = useState<number | null>(null),
    [measured, setMeasured] = useState(12);
  useEffect(() => {
    if (window.location.pathname.startsWith("/trustx"))
      window.history.replaceState({}, "", "/baggage");
  }, []);
  const refresh = useCallback(async () => {
    const [o, c, f] = await Promise.all([
      api("/overview"),
      api("/recommendations"),
      api("/flights"),
    ]);
    setOverview(normalizeOverview(o));
    setComparison(normalizeComparison(c));
    setFlights(f);
    setJourney(
      normalizeJourney(
        await api("/passenger/demo-passenger/journey?accessible=" + accessible),
      ),
    );
  }, [accessible]);
  useEffect(() => {
    if (!initialization.current)
      initialization.current =
        window.location.pathname === "/demo"
          ? api("/demo/event", { event: "reset" })
          : Promise.resolve();
    initialization.current.then(refresh).catch((e) => setError(e.message));
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
  useEffect(() => {
    const pop = () => setTab(routeTab());
    window.addEventListener("popstate", pop);
    return () => window.removeEventListener("popstate", pop);
  }, []);
  useEffect(() => {
    if (tab === "Decision log")
      Promise.all([api("/audit"), api("/results")])
        .then(([a, r]) => {
          setAudit(a);
          setResults(r);
        })
        .catch((e) => setError(e.message));
  }, [tab]);
  async function changeTab(name: string) {
    document.querySelector(".more-navigation")?.removeAttribute("open");
    window.history.pushState({}, "", routes[name] || "/app");
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
        <h1>{text("One TrustX")}</h1>
        <p role="status">{text(error || "Connecting to the airport twin…")}</p>
        <button onClick={() => run(refresh)}>{text("Retry connection")}</button>
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
        <YAxis unit={text("m")} axisLine={false} tickLine={false} />
        <Tooltip />
        <Legend />
        <Line
          isAnimationActive={false}
          dataKey="No action"
          stroke="#b6553d"
          dot={false}
          strokeWidth={2}
        />
        <Line
          isAnimationActive={false}
          dataKey="Open A5"
          stroke="#bba14b"
          dot={false}
        />
        <Line
          isAnimationActive={false}
          dataKey="Redirect 20%"
          stroke="#6b8dae"
          dot={false}
        />
        <Line
          isAnimationActive={false}
          dataKey="Combined"
          stroke="#21806a"
          dot={false}
          strokeWidth={3}
        />
        {text(
          custom && (
            <Line
              isAnimationActive={false}
              dataKey="Custom"
              stroke="#8d63ac"
              dot={false}
            />
          ),
        )}
      </LineChart>
    </ResponsiveContainer>
  );
  return (
    <div
      className={
        "app executive-app " +
        (presentation ? "presentation-active " : "") +
        (tab === "Passenger journey" ? "passenger-experience" : "")
      }
    >
      <div className="main">
        <header className="executive-nav">
          <a
            className="brand"
            href="/"
            aria-label={text("One TrustX home")}
          >
            <Plane size={26} />
            <span>
              {text(" ONE ")}
              <b>{text("TRUSTX")}</b>
            </span>
          </a>
          <button
            className="mobile-menu"
            aria-label={text("Open navigation")}
            aria-expanded={menu}
            onClick={() => setMenu(!menu)}
          >
            <Menu />
          </button>
          <nav
            aria-label={text("Platform navigation")}
            className={menu ? "open" : ""}
          >
            {text(
              tabs
                .filter((x) =>
                  [
                    "Airport now",
                    "Baggage",
                    "Operations control",
                    "Future map",
                    "What-if lab",
                    "Flights",
                    "Performance",
                  ].includes(x.name),
                )
                .map(({ name }) => (
                  <button
                    key={name}
                    aria-label={name}
                    aria-current={tab === name ? "page" : undefined}
                    className={tab === name ? "active" : ""}
                    onClick={() => changeTab(name)}
                  >
                    {text(
                      {
                        "Airport now": "Overview",
                        Baggage: "Baggage",
                        "Operations control": "Operations",
                        "Future map": "Future Flow",
                        "What-if lab": "Simulator",
                        Flights: "Flights",
                        Performance: "Performance",
                      }[name],
                    )}
                  </button>
                )),
            )}
            <details className="more-navigation">
              <summary>{text("More")}</summary>
              <div>
                {text(
                  tabs
                    .filter((x) =>
                      [
                        "Passenger flow",
                        "Passenger journey",
                        "Decision log",
                        "Data & sources",
                        "System Integration",
                      ].includes(x.name),
                    )
                    .map(({ name }) => (
                      <button key={name} onClick={() => changeTab(name)}>
                        {text(name)}
                      </button>
                    )),
                )}
                <a href="/demo">{text("Guided demonstration")}</a>
              </div>
            </details>
          </nav>
          <button
            className="analyst-trigger"
            onClick={() => copilotDialog.current?.showModal()}
          >
            <Sparkles size={15} />
            {text(" Ask One TrustX ")}
          </button>
          <LanguageSwitch />
          <button onClick={() => demoDialog.current?.showModal()}>
            {text("DEMO MODE ●")}
          </button>
          <span
            className="operator-badge"
            title={text("Demo operator · AIRPORT_OPERATOR")}
          >
            {text(" OP ")}
          </span>
        </header>
        <div className="executive-status">
          <span>{text("BKK context · Illustrative terminal")}</span>
          <span>
            {text(" SYNTHETIC DEMO ")}
            <span aria-hidden="true">{text("·")}</span>
            {text(" 17:00 ICT / frozen clock ")}
          </span>
        </div>
        <main
          className={
            "content " +
            (window.location.pathname === "/demo" ? "guided-content" : "")
          }
        >
          <div
            className={
              "title-row " +
              (tab === "Airport now" ? "executive-overview-banner" : "")
            }
          >
            <div>
              <div className="eyebrow">{text("PREDICT. COMPARE. ACT.")}</div>
              <h1>
                {text(
                  tab === "Airport now"
                    ? "Good evening, Operations Control"
                    : tab === "Baggage"
                      ? "Baggage Flow Control"
                    : tab === "Operations control"
                      ? "Operational Situations"
                      : tab === "What-if lab"
                        ? "Operational Decision Simulator"
                        : tab === "Passenger journey"
                          ? "Your journey, with confidence."
                          : tab === "Data & sources"
                            ? "Trust starts with the source."
                            : tab === "Future map"
                              ? "Passenger Flow Forecast"
                              : [
                                    "Flights",
                                    "Passenger flow",
                                    "Performance",
                                    "System Integration",
                                  ].includes(tab)
                                ? tab
                                : "Every decision, accountable.",
                )}
              </h1>
              <p className="subtitle">
                {text(
                  tab === "Airport now"
                    ? "A connected view of passenger flow — now and one step ahead."
                    : tab === "Baggage"
                      ? "Is the baggage flow normal, where is it blocked, what is affected, and what should happen first?"
                    : tab === "Passenger journey"
                      ? "A personalized route through an illustrative terminal."
                      : "Explainable intelligence for a human in control.",
                )}
              </p>
            </div>
          </div>
          {text(
            window.location.pathname === "/demo" && (
              <GuidedDemo
                refresh={refresh}
                overview={overview}
                comparison={comparison}
                journey={journey}
              />
            ),
          )}
          <div className="provenance">
            <ShieldCheck size={15} />
            <span>{text(notice)}</span>
            <span className="provenance-right">
              {text(overview.data_status)}
            </span>
          </div>
          {text(
            error && (
              <div className="error" role="alert">
                <AlertTriangle size={18} />
                {text(error)}
                <button onClick={() => run(refresh)}>{text("Retry")}</button>
              </div>
            ),
          )}
          {text(
            message && (
              <div className="success" role="status">
                {text(message)}
              </div>
            ),
          )}
          {text(
            busy && (
              <div className="working" role="status">
                {text(" Updating the twin… ")}
              </div>
            ),
          )}
          <dialog ref={demoDialog} className="demo-mode-dialog">
            <button onClick={() => demoDialog.current?.close()}>
              {text("Close demo controls")}
            </button>
            <h2>{text("Demo mode")}</h2>
            <div className="demo-controls">
              <button disabled={busy} onClick={() => demo("reset")}>
                {text("Reset demo")}
              </button>
              <button disabled={busy} onClick={() => demo("peak")}>
                {text(" Start peak event ")}
              </button>
              <button disabled={busy} onClick={() => demo("lane-closure")}>
                {text(" Lane closure ")}
              </button>
              <button disabled={busy} onClick={() => demo("gate-change")}>
                {text(" Gate C8 → E7 ")}
              </button>
              <button
                disabled={busy}
                onClick={() => demo(stale ? "refresh" : "stale")}
              >
                {text(stale ? "Refresh feed" : "Test stale feed")}
              </button>
              <button disabled={busy} onClick={() => run(refresh)}>
                {text(" Run recommendation ")}
              </button>
            </div>
          </dialog>
          {text(
            stale && (
              <section className="panel stale-panel" role="alert">
                <h2>{text("Forecast paused")}</h2>
                <p>
                  {text(
                    "Passenger-flow feed stale. Recommendations and passenger guidance are paused.",
                  )}
                </p>
                <p>
                  {text(
                    "Prediction service: ONLINE · Passenger-flow feed: STALE · Synthetic flight feed: FRESH · Weather: contextual cache only.",
                  )}
                </p>
                <p>
                  {text("Last reliable forecast (+30): ")}
                  {text(a.forecast[1].lower_bound)}
                  {text("–")}
                  {text(a.forecast[1].upper_bound)}
                  {text(" min")}
                </p>
                <p>
                  {text("Last reliable update: ")}
                  {text(
                    new Date(overview.last_reliable_update).toLocaleString(),
                  )}
                </p>
                <button onClick={() => demo("refresh")}>
                  {text("Refresh feed")}
                </button>
                <button onClick={() => demo("reset")}>
                  {text("Reset demo")}
                </button>
                <a href="/sources">{text("Inspect source freshness")}</a>
              </section>
            ),
          )}
          <div hidden={window.location.pathname === "/demo"}>
            {text(
              !stale && (
                <>
                  {text(
                    ["Flights", "Passenger flow", "Performance"].includes(
                      tab,
                    ) && (
                      <ExtraPages
                        tab={tab}
                        flights={flights}
                        comparison={comparison}
                        overview={overview}
                      />
                    ),
                  )}
                  {tab === "Baggage" && <BaggageControl />}
                  {text(
                    tab === "Operations control" && (
                      <Situations
                        overview={overview}
                        onAnalyse={() => changeTab("What-if lab")}
                      />
                    ),
                  )}
                  {text(
                    (tab === "Airport now" ||
                      tab === "Future map" ||
                      tab === "Operations control") && (
                      <>
                        <section
                          className={
                            "metrics " +
                            (tab === "Operations control"
                              ? "context-hidden"
                              : "")
                          }
                        >
                          <Metric
                            label={text("SECURITY A · NOW")}
                            value={fmt(a.current_wait)}
                            unit={text("min")}
                            detail={`${a.open_lanes} of 5 lanes available`}
                            icon={<Clock3 size={17} />}
                          />
                          <Metric
                            label={text("FORECAST · +30 MIN")}
                            value={`${a.forecast[1].lower_bound}–${a.forecast[1].upper_bound}`}
                            unit={text("min")}
                            detail={text("Assumed uncertainty interval")}
                            icon={<Activity size={17} />}
                            attention={overview.scenario.peak}
                          />
                          <Metric
                            label={text("POTENTIAL TIME SAVED")}
                            value={fmt(best?.passenger_minutes_saved)}
                            unit={text("pax·min")}
                            detail={text("Whole security network · simulated")}
                            icon={<Users size={17} />}
                          />
                          <Metric
                            label={text("FORECAST CONFIDENCE")}
                            value={stale ? "35" : "80"}
                            unit={text("%")}
                            detail={text("Heuristic · not yet calibrated")}
                            icon={<ShieldCheck size={17} />}
                          />
                        </section>
                        <div
                          className={
                            "primary-grid " +
                            (tab === "Operations control"
                              ? "context-hidden"
                              : "")
                          }
                        >
                          <section className="panel map-panel">
                            <div className="panel-heading">
                              <div>
                                <h2>
                                  {text(" One TrustX flow")}
                                  {text(" ")}
                                  <span className="tiny-tag">
                                    {text("ILLUSTRATIVE")}
                                  </span>
                                </h2>
                                <p>
                                  {text(
                                    " Choose a horizon to reveal pressure across the terminal. ",
                                  )}
                                </p>
                              </div>
                              <span className="map-status">
                                <span className="pulse" />
                                {text(
                                  " Prediction service online · synthetic feed fresh ",
                                )}
                              </span>
                            </div>
                            <div className="time-selector">
                              <span>{text("FORECAST HORIZON")}</span>
                              <div>
                                {text(
                                  [0, 15, 30, 60].map((h) => (
                                    <button
                                      aria-pressed={horizon === h}
                                      className={
                                        horizon === h ? "selected" : ""
                                      }
                                      key={h}
                                      onClick={() => setHorizon(h)}
                                    >
                                      {text(h === 0 ? "Now" : `+${h} min`)}
                                    </button>
                                  )),
                                )}
                              </div>
                            </div>
                            <details className="presentation-tools">
                              <summary>
                                {text(
                                  "Presentation tools · Future Time Slider",
                                )}
                              </summary>
                              <label className="motion-toggle">
                                <input
                                  type="checkbox"
                                  checked={presentation}
                                  onChange={(e) =>
                                    setPresentation(e.target.checked)
                                  }
                                />
                                {text(" ")}
                                {text(" Animate modelled route direction ")}
                              </label>
                              <label className="future-range">
                                {text(" Forecast horizon ")}
                                <input
                                  aria-label={text("Future time slider")}
                                  type="range"
                                  min="0"
                                  max="3"
                                  step="1"
                                  value={[0, 15, 30, 60].indexOf(horizon)}
                                  onChange={(e) =>
                                    setHorizon(
                                      [0, 15, 30, 60][Number(e.target.value)],
                                    )
                                  }
                                />
                                <strong>
                                  {text(
                                    horizon ? `+${horizon} min` : "Current",
                                  )}
                                </strong>
                              </label>
                            </details>
                            <AirportMap
                              checkpoints={overview.checkpoints}
                              horizon={horizon}
                              gate={overview.scenario.gate}
                              onCompare={() => changeTab("What-if lab")}
                            />
                            <div className="map-legend">
                              <span>
                                <i className="green" />
                                {text(" Healthy ")}
                              </span>
                              <span>
                                <i className="yellow" />
                                {text(" Attention ")}
                              </span>
                              <span>
                                <i className="orange" />
                                {text(" Rising risk ")}
                              </span>
                              <span>
                                <i className="red" />
                                {text(" Intervention needed ")}
                              </span>
                            </div>
                            <div className="map-footer">
                              <Map size={14} />
                              {text(
                                " Topology assumption · not a real airport map",
                              )}
                              {text(" ")}
                              <span>
                                {text(
                                  "Routing uses directed, accessible edges",
                                )}
                              </span>
                            </div>
                          </section>
                          <section className="panel priority">
                            <div className="priority-accent" />
                            <div className="panel-heading">
                              <h2>{text("Priority insight")}</h2>
                              <span
                                className={
                                  overview.scenario.peak
                                    ? "risk-tag"
                                    : "neutral-tag"
                                }
                              >
                                {text(
                                  overview.scenario.peak
                                    ? "↑ RISING PRESSURE"
                                    : "MONITORING",
                                )}
                              </span>
                            </div>
                            <div className="priority-zone">
                              <div className="shield-icon">
                                <ShieldCheck size={26} />
                              </div>
                              <div>
                                <h3>{text("Security A")}</h3>
                                <p>{text("Departure processing")}</p>
                              </div>
                            </div>
                            <div className="forecast-jump">
                              <div>
                                <small>{text("NOW")}</small>
                                <strong>
                                  {text(fmt(a.current_wait))}
                                  <span>{text("min")}</span>
                                </strong>
                              </div>
                              <ArrowRight size={24} />
                              <div>
                                <small>{text("IN 30 MINUTES")}</small>
                                <strong
                                  className={
                                    overview.scenario.peak ? "orange-text" : ""
                                  }
                                >
                                  {text(fmt(a.forecast[1].predicted_wait_min))}
                                  <span>{text("min")}</span>
                                </strong>
                              </div>
                            </div>
                            <p className="insight-copy">
                              {text(
                                overview.scenario.peak
                                  ? "A synthetic departure wave exceeds the capacity of four open lanes. Pressure builds before the next boarding window."
                                  : "The normal arrival profile clears the initial queue. Start the peak event to explore a departure-wave intervention.",
                              )}
                            </p>
                            <div className="drivers-title">
                              {text(" MODELLED DRIVERS ")}
                              <span>{text("ASSUMPTION")}</span>
                            </div>
                            <div className="driver">
                              <span>{text("Departure-wave demand")}</span>
                              <strong>
                                {text(
                                  overview.scenario.peak ? "11.2–19.2" : "5",
                                )}
                                {text(" pax/min ")}
                              </strong>
                            </div>
                            <div className="driver">
                              <span>
                                {text("Available processing capacity")}
                              </span>
                              <strong>
                                {text(a.open_lanes * 2)}
                                {text(" pax/min")}
                              </strong>
                            </div>
                            <div className="recommendation-mini">
                              <span>
                                <Sparkles size={14} />
                                {text(" BEST FEASIBLE ACTION ")}
                              </span>
                              <strong>
                                {text(
                                  comparison?.recommended ||
                                    "Blocked — stale data",
                                )}
                              </strong>
                              <small>
                                {text(
                                  best
                                    ? `${best.additional_staff} additional staff · ${best.walking_penalty} min walking penalty per pax`
                                    : "Refresh the feed to continue.",
                                )}
                              </small>
                            </div>
                            <button
                              className="primary full"
                              onClick={() => changeTab("What-if lab")}
                            >
                              {text(" Compare interventions ")}
                              <ArrowUpRight size={16} />
                            </button>
                          </section>
                        </div>
                        <div
                          className={
                            "bottom-grid " +
                            (tab === "Operations control" ||
                            tab === "Future map"
                              ? "context-hidden"
                              : "")
                          }
                        >
                          <section className="panel">
                            <div className="panel-heading">
                              <div>
                                <h2>{text("Pressure over the next hour")}</h2>
                                <p>
                                  {text(
                                    "Security A virtual wait · deterministic simulation",
                                  )}
                                </p>
                              </div>
                              <span className="tiny-tag">
                                {text("MINUTES")}
                              </span>
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
                                  unit={text("m")}
                                />
                                <YAxis axisLine={false} tickLine={false} />
                                <Tooltip />
                                <Area
                                  isAnimationActive={false}
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
                                <h2>{text("Departure wave")}</h2>
                                <p>
                                  {text(
                                    " Four synthetic flights · 580 anonymous journey fixtures ",
                                  )}
                                </p>
                              </div>
                              <Plane size={18} />
                            </div>
                            <div className="flight-table">
                              <div className="flight-row table-head">
                                <span>{text("FLIGHT")}</span>
                                <span>{text("GATE")}</span>
                                <span>{text("DEPARTURE · ICT")}</span>
                              </div>
                              {text(
                                flights.map((f) => (
                                  <div className="flight-row" key={f.id}>
                                    <strong>
                                      <Plane size={14} />
                                      {text(f.flight_number)}
                                    </strong>
                                    <span>{text(f.gate)}</span>
                                    <span>
                                      {text(
                                        new Date(
                                          f.scheduled_departure,
                                        ).toLocaleTimeString("en-GB", {
                                          timeZone: "Asia/Bangkok",
                                          hour: "2-digit",
                                          minute: "2-digit",
                                        }),
                                      )}
                                      <small className="tiny-tag">
                                        {text("SYNTHETIC")}
                                      </small>
                                    </span>
                                  </div>
                                )),
                              )}
                            </div>
                          </section>
                        </div>
                        {text(
                          tab === "Operations control" && (
                            <section className="panel section-gap">
                              <div className="panel-heading">
                                <h2>{text("Operational cause graph")}</h2>
                                <span className="tiny-tag">
                                  {text("NOT CAUSAL PROOF")}
                                </span>
                              </div>
                              <div className="cause-flow">
                                <span>
                                  {text(" Departure wave ")}
                                  <br />
                                  <small>
                                    {text("Synthetic schedule profile")}
                                  </small>
                                </span>
                                <ArrowRight />
                                <span>
                                  {text(" Arrivals exceed capacity ")}
                                  <br />
                                  <small>
                                    {text("Operational causal assumption")}
                                  </small>
                                </span>
                                <ArrowRight />
                                <span>
                                  {text(" Queue accumulation ")}
                                  <br />
                                  <small>{text("Derived queue balance")}</small>
                                </span>
                                <ArrowRight />
                                <span>
                                  {text(" Journey risk ")}
                                  <br />
                                  <small>
                                    {text("Assumed checkpoint budget")}
                                  </small>
                                </span>
                              </div>
                              <div className="cause-contributions">
                                {text(
                                  overview.root_causes?.drivers.map(
                                    (driver: any) => (
                                      <div key={driver.name}>
                                        <span className="tiny-tag">
                                          {text(driver.rank)}
                                        </span>
                                        <strong>{text(driver.name)}</strong>
                                        <span>
                                          {text(" +")}
                                          {text(
                                            fmt(driver.wait_contribution_min),
                                          )}
                                          {text(
                                            " min · MODELLED CONTRIBUTION ",
                                          )}
                                        </span>
                                      </div>
                                    ),
                                  ),
                                )}
                              </div>
                              <p className="note">
                                {text(
                                  " Two-factor Shapley attribution inside the simulation compares departure demand and lane availability against normal demand with five lanes. Contributions describe modelled excess wait, not real-world causation. Weather remains contextual only. ",
                                )}
                              </p>
                            </section>
                          ),
                        )}
                      </>
                    ),
                  )}
                  {tab === "Airport now" && <PublicContext />}
                  {text(
                    tab === "What-if lab" && (
                      <>
                        <div className="lab-intro">
                          <div>
                            <FlaskConical size={22} />
                            <div>
                              <h2>
                                {text("One scenario. Four possible futures.")}
                              </h2>
                              <p>
                                {text(
                                  " Compare the same arrivals across both checkpoints. Reserve staff: 4 · max lanes: 5 · eligible redirect: 30%. ",
                                )}
                              </p>
                            </div>
                          </div>
                          <span className="tiny-tag">
                            {text("DETERMINISTIC · REPRODUCIBLE")}
                          </span>
                        </div>
                        <DecisionWorkspace
                          comparison={comparison}
                          busy={busy}
                          stale={stale}
                          onDecision={decide}
                        />
                        <details className="presentation-tools">
                          <summary>
                            {text("Presentation tools · Drag before / after")}
                          </summary>
                          <ComparisonReveal
                            before={base}
                            after={custom || best}
                          />
                        </details>
                        <div className="bottom-grid">
                          <section className="panel">
                            <div className="panel-heading">
                              <div>
                                <h2>
                                  {text("Security A · forecast comparison")}
                                </h2>
                                <p>
                                  {text(
                                    " Network metrics above include Security B and extra walking. ",
                                  )}
                                </p>
                              </div>
                            </div>
                            {text(compareChart)}
                            <p className="note">{text(comparison?.reason)}</p>
                          </section>
                          <section className="panel custom-panel">
                            <h2>{text("Build a custom intervention")}</h2>
                            <label>
                              {text(" Open lanes at Security A ")}
                              <strong>{text(lanes)}</strong>
                              <input
                                aria-label={text("Open lanes")}
                                type="number"
                                min="0"
                                max="5"
                                value={lanes}
                                onChange={(e) => setLanes(+e.target.value)}
                              />
                            </label>
                            <label>
                              {text(" Redirect eligible passengers ")}
                              <strong>
                                {text(redirect)}
                                {text("%")}
                              </strong>
                              <input
                                aria-label={text("Redirect percentage")}
                                type="number"
                                min="0"
                                max="30"
                                value={redirect}
                                onChange={(e) => setRedirect(+e.target.value)}
                              />
                            </label>
                            <div className="input-pair">
                              <label>
                                {text(" Extra staff ")}
                                <input
                                  aria-label={text("Extra staff")}
                                  type="number"
                                  min="0"
                                  max="4"
                                  value={staff}
                                  onChange={(e) => setStaff(+e.target.value)}
                                />
                              </label>
                              <label>
                                {text(" Wave delay (min) ")}
                                <input
                                  aria-label={text("Flight delay")}
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
                              {text(" Run custom simulation ")}
                            </button>
                            {text(
                              custom && (
                                <p role="status" className="success">
                                  {text(" Custom: ")}
                                  {text(custom.average_wait)}
                                  {text(" min average ·")}
                                  {text(" ")}
                                  {text(fmt(custom.passenger_minutes_saved))}
                                  {text(" pax·min saved ·")}
                                  {text(" ")}
                                  {text(
                                    custom.feasible
                                      ? "Feasible"
                                      : "Unserved queue — not actionable",
                                  )}
                                </p>
                              ),
                            )}
                          </section>
                        </div>
                        <section className="panel section-gap">
                          <h2>
                            {text("Human decision & transparent scoring")}
                          </h2>
                          <p className="note">
                            {text(
                              " Score = wait reduction + 0.01 × passenger minutes saved + 50 × risk reduction − staff − walking penalty − 0.001 × cost. All weights are configurable through POST /api/recommendations/score. ",
                            )}
                          </p>
                          <label>
                            {text(" Decision reason ")}
                            <input
                              aria-label={text("Decision reason")}
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
                            {text(
                              " Override recommendation with custom lanes & redirect ",
                            )}
                          </button>
                          <p className="note">
                            {text(
                              " Overrides apply only lane and redirect settings. Extra staff and flight delays remain simulation-only. An accepted action updates this demo, never airport equipment. ",
                            )}
                          </p>
                        </section>
                      </>
                    ),
                  )}
                  {text(
                    tab === "Passenger journey" && journey && (
                      <div className="passenger-layout">
                        <section className="passenger-card">
                          {text(
                            journey.gate === "E7" && (
                              <div className="journey-update">
                                <strong>
                                  {text("IMPORTANT JOURNEY UPDATE")}
                                </strong>
                                <p>
                                  {text("Your departure gate has changed.")}
                                </p>
                                <b>{text("C8 → E7")}</b>
                              </div>
                            ),
                          )}
                          <div className="passenger-top">
                            <span>
                              <Plane size={18} />
                              {text(" DEMO401 · MODELLED SCENARIO FLIGHT ")}
                            </span>
                            <select
                              aria-label={text("Language")}
                              value={activeLanguage}
                              onChange={(e) =>
                                setGlobalLanguage(e.target.value as "en" | "th")
                              }
                            >
                              <option value="en">{text("EN")}</option>
                              <option value="th">{text("ไทย")}</option>
                            </select>
                          </div>
                          <div className="boarding">
                            <div>
                              <small>{text("BOARDING DEADLINE")}</small>
                              <strong>{text(journey.boarding_deadline)}</strong>
                            </div>
                            <div>
                              <small>{text("GATE")}</small>
                              <strong>{text(journey.gate)}</strong>
                            </div>
                          </div>
                          <div
                            className={
                              "safe-time " +
                              (journey.safe_time_min < 15 ? "urgent" : "")
                            }
                          >
                            <span>{text(i18n[activeLanguage].safe)}</span>
                            <div>
                              {text(
                                previousSafe !== null && (
                                  <del>{text(previousSafe)}</del>
                                ),
                              )}
                              <strong>
                                <AnimatedNumber value={journey.safe_time_min} />
                              </strong>
                              <small>{text("MINUTES")}</small>
                            </div>
                            <span className="safe-status">
                              {text(
                                stale
                                  ? "DATA STALE — LOW CONFIDENCE"
                                  : journey.risk_level,
                              )}
                            </span>
                            <p>
                              {text(
                                stale
                                  ? "Refresh data before relying on this guidance."
                                  : journey.action,
                              )}
                            </p>
                          </div>
                          <dl className="journey-breakdown">
                            <div>
                              <dt>{text("Current location")}</dt>
                              <dd>{text(journey.current_node)}</dd>
                            </div>
                            <div>
                              <dt>{text("Remaining processing")}</dt>
                              <dd>
                                {text(journey.processing_time_min)}
                                {text(" min")}
                              </dd>
                            </div>
                            <div>
                              <dt>{text("Walking to gate")}</dt>
                              <dd>
                                {text(journey.walking_time_min)}
                                {text(" min")}
                              </dd>
                            </div>
                            <div>
                              <dt>{text("Safety buffer")}</dt>
                              <dd>
                                {text(journey.safety_buffer_min)}
                                {text(" min")}
                              </dd>
                            </div>
                          </dl>
                          <label className="checkbox">
                            <input
                              type="checkbox"
                              checked={accessible}
                              onChange={(e) => setAccessible(e.target.checked)}
                            />
                            {text(" Step-free, accessible route ")}
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
                            {text(
                              journey.gate === "E7"
                                ? activeLanguage === "th"
                                  ? "เดินทางไปเกต E7"
                                  : "Proceed to Gate E7"
                                : i18n[activeLanguage].continue,
                            )}
                            <ArrowRight size={16} />
                          </button>
                          <small className="passenger-disclaimer">
                            {text(notice)}
                          </small>
                        </section>
                        <div>
                          <section className="panel">
                            <div className="panel-heading">
                              <div>
                                <h2>{text("Your recommended route")}</h2>
                                <p>
                                  {text(
                                    " Anonymous passenger · no personal information stored ",
                                  )}
                                </p>
                              </div>
                              <Route size={20} />
                            </div>
                            <ol className="route-steps">
                              {text(
                                journey.path.map((node: string, i: number) => (
                                  <li key={node}>
                                    <span>{text(i + 1)}</span>
                                    <div>
                                      <strong>{text(node)}</strong>
                                      <small>
                                        {text(
                                          i === 0
                                            ? "You are here"
                                            : `${journey.segments[i - 1].walking_min} min walk · ${journey.segments[i - 1].processing_min} min processing`,
                                        )}
                                      </small>
                                    </div>
                                    {text(
                                      i === journey.path.length - 1 && (
                                        <Plane size={18} />
                                      ),
                                    )}
                                  </li>
                                )),
                              )}
                            </ol>
                            <p className="note">
                              {text(
                                " Safe Time = 64 minutes until boarding − remaining journey − 10-minute buffer. Scenario clock is frozen at 17:00; times and route are simulated. ",
                              )}
                            </p>
                          </section>
                          <section className="panel section-gap">
                            <h2>{text("A changed gate. A new plan.")}</h2>
                            <p>
                              {text(
                                " Reset the demo, then change C8 to E7 to reproduce Safe Time 34 → 11 minutes on the accessible route. During a peak event, values adjust to the active queues. ",
                              )}
                            </p>
                            <button
                              className="secondary"
                              disabled={busy}
                              onClick={() => demo("gate-change")}
                            >
                              {text(" Simulate gate change ")}
                              <ArrowRight size={15} />
                            </button>
                          </section>
                        </div>
                      </div>
                    ),
                  )}
                  {text(
                    tab === "Decision log" && (
                      <>
                        <DecisionHistory key={JSON.stringify(results)} />
                        <section className="panel">
                          <div className="panel-heading">
                            <div>
                              <h2>{text("Measure the intervention")}</h2>
                              <p>
                                {text(
                                  " Append a synthetic observed mean wait to quantify forecast error. Never represented as airport telemetry. ",
                                )}
                              </p>
                            </div>
                          </div>
                          <label>
                            {text(
                              " Simulated observed average wait (minutes) ",
                            )}
                            <input
                              aria-label={text("Observed wait")}
                              type="number"
                              min="0"
                              max="600"
                              value={measured}
                              onChange={(e) => setMeasured(+e.target.value)}
                            />
                          </label>
                          {text(
                            results.length === 0 ? (
                              <p className="empty">
                                {text(
                                  " Accept an intervention to create a measurement record. ",
                                )}
                              </p>
                            ) : (
                              results.map((r) => (
                                <div className="result-row" key={r.id}>
                                  <span>
                                    {text(" Predicted ")}
                                    {text(r.after_predicted)}
                                    {text(" min ·")}
                                    {text(" ")}
                                    {text(
                                      r.after_actual === null
                                        ? "Awaiting measurement"
                                        : `Observed ${r.after_actual} min · error ${r.prediction_error} min`,
                                    )}
                                  </span>
                                  <button
                                    disabled={busy || r.after_actual !== null}
                                    onClick={() =>
                                      run(async () => {
                                        await api(
                                          "/results/" + r.id + "/measure",
                                          {
                                            actual_average_wait: measured,
                                            source_type: "SIMULATED",
                                          },
                                        );
                                        setResults(await api("/results"));
                                        setAudit(await api("/audit"));
                                      })
                                    }
                                  >
                                    {text(" Record simulated result ")}
                                  </button>
                                </div>
                              ))
                            ),
                          )}
                        </section>
                        <details className="panel section-gap">
                          <summary>{text("View technical event log")}</summary>
                          <div className="panel-heading">
                            <h2>{text("Prediction & decision trail")}</h2>
                            <span className="tiny-tag">
                              {text("LATEST 100 RECORDS")}
                            </span>
                          </div>
                          {text(
                            audit.length === 0 ? (
                              <p className="empty">
                                {text("No recorded decisions yet.")}
                              </p>
                            ) : (
                              audit.map((x) => (
                                <details className="audit-row" key={x.id}>
                                  <summary>
                                    <span className="audit-icon">
                                      <History size={16} />
                                    </span>
                                    <strong>{text(x.result)}</strong>
                                    <time>
                                      {text(
                                        new Date(
                                          x.timestamp,
                                        ).toLocaleTimeString(),
                                      )}
                                    </time>
                                    <span>
                                      {text(x.human_decision || "System")}
                                    </span>
                                  </summary>
                                  <pre>{text(JSON.stringify(x, null, 2))}</pre>
                                </details>
                              ))
                            ),
                          )}
                        </details>
                      </>
                    ),
                  )}
                </>
              ),
            )}
            {text(tab === "System Integration" && <Integration />)}
            {text(
              tab === "Data & sources" && (
                <>
                  <DataSources />
                  <PublicContext detailed />
                </>
              ),
            )}
          </div>
          <dialog ref={copilotDialog} className="copilot-dialog">
            <button onClick={() => copilotDialog.current?.close()}>
              {text(" Close copilot ")}
            </button>
            <section className="copilot panel">
              <div className="copilot-heading">
                <div className="spark">
                  <Sparkles size={20} />
                </div>
                <div>
                  <h2>{text("One TrustX Analyst")}</h2>
                  <p>
                    {text(
                      " Grounded in this scenario’s structured calculations. No LLM required. ",
                    )}
                  </p>
                </div>
                <span className="tiny-tag">
                  {text("DETERMINISTIC FALLBACK")}
                </span>
              </div>
              <form
                onSubmit={(e) => {
                  e.preventDefault();
                  run(async () => {
                    setAnswer(
                      (await api("/copilot/query", { question })).answer,
                    );
                  });
                }}
              >
                <input
                  aria-label={text("Copilot question")}
                  value={question}
                  onChange={(e) => setQuestion(e.target.value)}
                  maxLength={500}
                />
                <button className="primary" disabled={busy}>
                  {text(" Ask copilot ")}
                  <ArrowRight size={15} />
                </button>
              </form>
              {text(
                answer && (
                  <p className="copilot-answer" role="status">
                    {text(answer)}
                  </p>
                ),
              )}
              <button
                onClick={() => {
                  copilotDialog.current?.close();
                  changeTab("What-if lab");
                }}
              >
                {text(" Open simulation ")}
              </button>
              <button
                onClick={() => {
                  copilotDialog.current?.close();
                  changeTab("Flights");
                }}
              >
                {text(" View flights ")}
              </button>
            </section>
          </dialog>
          <footer>
            <span>
              {text(" One TrustX")}
              {text(" ")}
              <span className="muted">
                {text("/ Decision & simulation layer")}
              </span>
            </span>
            <span>{text("OBSERVE → PREDICT → SIMULATE → ACT → MEASURE")}</span>
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
        {text(label)}
        {text(icon)}
      </div>
      <div className="metric-value">
        {text(value)}
        <span>{text(unit)}</span>
      </div>
      <p>{text(detail)}</p>
    </article>
  );
}
