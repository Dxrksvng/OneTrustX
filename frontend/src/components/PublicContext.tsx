import { useEffect, useState } from "react";
import {
  ResponsiveContainer,
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
} from "recharts";
import { api } from "../services/api";
import { text } from "../i18n";
export default function PublicContext({
  detailed = false,
}: {
  detailed?: boolean;
}) {
  const [data, setData] = useState<any>(null),
    [catalog, setCatalog] = useState<any>(null),
    [error, setError] = useState("");
  useEffect(() => {
    api("/data/context")
      .then(setData)
      .catch((e) => setError(e.message));
    if (detailed)
      api("/data/catalog")
        .then(setCatalog)
        .catch((e) => setError(e.message));
  }, [detailed]);
  if (error)
    return (
      <section className="panel section-gap">
        <h2>{text("Historical public context")}</h2>
        <p role="alert">{text(error)}</p>
        <p>
          {text(
            "Public cache unavailable. Modelled demo remains available; no real observations are fabricated.",
          )}
        </p>
      </section>
    );
  if (!data) return <p>{text("Loading public data cache…")}</p>;
  if (!Array.isArray(data.bkk_daily))
    return (
      <section className="panel section-gap">
        <span className="eyebrow">{text("PUBLIC CONTEXT")}</span>
        <h2>{text("Historical public context")}</h2>
        <p>
          {text(
            "The public context cache is not available in this demo deployment. Operational values remain synthetic and clearly labelled.",
          )}
        </p>
      </section>
    );
  const latest = data.bkk_daily.at(-1),
    benchmark = data.benchmark;
  return (
    <section className="panel section-gap public-context">
      <div className="panel-heading">
        <div>
          <span className="eyebrow">
            {text("REAL PUBLIC · HISTORICAL CONTEXT")}
          </span>
          <h2>{text("Suvarnabhumi Airport · BKK")}</h2>
          <p>
            {text(
              "Operational checkpoint configuration is modelled for the MVP; it is not BKK telemetry.",
            )}
          </p>
        </div>
        <a href="/sources">{text("View source lineage →")}</a>
      </div>
      <div className="public-facts">
        <div>
          <small>{text("CAAT · published BKK daily passengers")}</small>
          <strong>{latest?.passengers.toLocaleString() || "—"}</strong>
          <span>
            {latest?.date} · {text("arrivals + departures")}
          </span>
        </div>
        <div>
          <small>{text("CBP · external immigration benchmark")}</small>
          <strong>{benchmark?.records?.toLocaleString() || "—"}</strong>
          <span>{text("hourly observations · US only")}</span>
        </div>
        <div>
          <small>{text("BTS · real flight benchmark")}</small>
          <strong>
            {data.bts_daily
              .reduce((n: number, r: any) => n + r.flights, 0)
              .toLocaleString()}
          </strong>
          <span>{text("February 2025 · US domestic")}</span>
        </div>
      </div>
      <div className="bottom-grid">
        <div>
          <h3>{text("Thailand passenger history · CAAT")}</h3>
          <p className="note">
            {text(
              "National monthly totals, not BKK-only or live terminal occupancy.",
            )}
          </p>
          <ResponsiveContainer width="100%" height={200}>
            <LineChart data={data.thailand_monthly}>
              <XAxis
                dataKey="date"
                tickFormatter={(v: string) => v.slice(0, 7)}
                minTickGap={30}
              />
              <YAxis
                width={48}
                tickFormatter={(v: number) => (v / 1e6).toFixed(0) + "M"}
              />
              <Tooltip />
              <Line
                dataKey="passengers"
                stroke="#164e7a"
                dot={false}
                isAnimationActive={false}
              />
            </LineChart>
          </ResponsiveContainer>
        </div>
        <div>
          <h3>{text("External queue plausibility range")}</h3>
          <p>
            {text(
              "US immigration average-wait observations · January–March 2025",
            )}
          </p>
          <div className="public-facts">
            <div>
              <small>P10</small>
              <strong>{benchmark?.wait_quantiles?.p10} min</strong>
            </div>
            <div>
              <small>P50</small>
              <strong>{benchmark?.wait_quantiles?.p50} min</strong>
            </div>
            <div>
              <small>P95</small>
              <strong>{benchmark?.wait_quantiles?.p95} min</strong>
            </div>
          </div>
          <p className="note">
            {text(
              "These observations constrain external plausibility checks only. CBP booth throughput is not BKK security throughput; no BKK calibration is claimed.",
            )}
          </p>
        </div>
      </div>
      <div className="bottom-grid">
        <div>
          <h3>{text("Real US flight delay context · BTS")}</h3>
          <p className="note">
            {text(
              "Mean departure delay by date · US domestic flights only. Not BKK operations.",
            )}
          </p>
          <ResponsiveContainer width="100%" height={180}>
            <LineChart data={data.bts_daily}>
              <XAxis
                dataKey="flight_date"
                tickFormatter={(v: string) => v.slice(5)}
                minTickGap={25}
              />
              <YAxis width={36} />
              <Tooltip />
              <Line
                dataKey="mean_departure_delay"
                name={text("Departure delay · min")}
                stroke="#b99a5b"
                dot={false}
                isAnimationActive={false}
              />
            </LineChart>
          </ResponsiveContainer>
        </div>
        <div>
          <h3>{text("BKK historical weather · Open-Meteo")}</h3>
          <p className="note">
            {text(
              "Monthly mean temperature · 2025 reanalysis, not METAR telemetry.",
            )}
          </p>
          <ResponsiveContainer width="100%" height={180}>
            <LineChart
              data={data.weather_monthly.filter(
                (r: any) => r.metric === "temperature_2m",
              )}
            >
              <XAxis dataKey="month" minTickGap={30} />
              <YAxis width={36} />
              <Tooltip />
              <Line
                dataKey="mean"
                name="°C"
                stroke="#164e7a"
                dot={false}
                isAnimationActive={false}
              />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>
      {detailed && catalog && (
        <>
          <figure className="public-airport-photo">
            <img
              src="/images/airport/bkk-night.webp"
              alt={text(
                "Suvarnabhumi Airport terminal architecture at night, historical photograph",
              )}
            />
            <figcaption>
              <a href="https://commons.wikimedia.org/wiki/File:Suvarnabhumi_Airport_Bangkok_by_Night.jpg">
                {text("Historical airport photograph · Wikigod · CC BY 3.0")}
              </a>{" "}
              ·{" "}
              <a href="https://creativecommons.org/licenses/by/3.0/">
                CC BY 3.0
              </a>{" "}
              · resized / WebP
            </figcaption>
          </figure>
          <h2>{text("Dataset quality & lineage")}</h2>
          <p>
            {text(
              "Freshness describes cached retrieval, not current airport telemetry. Historical dates stay visible.",
            )}
          </p>
          {Object.entries(
            catalog.datasets.reduce((g: any, r: any) => {
              (g[r.source_name] ??= []).push(r);
              return g;
            }, {}),
          ).map(([name, items]) => (
            <details className="source-feed-details" key={name}>
              <summary>
                {name.toUpperCase()} · {text("REAL_PUBLIC")} ·{" "}
                {(items as any[])
                  .reduce((n, r) => n + r.records, 0)
                  .toLocaleString()}{" "}
                {text("records")}
              </summary>
              {(items as any[]).map((r) => (
                <div className="source-feed" key={r.id}>
                  <div>
                    <strong>{r.id}</strong>
                    <small>
                      {r.source_geography} · {r.date_from} → {r.date_to}
                    </small>
                    <small>
                      {text("Retrieved")} {r.retrieved_at}
                    </small>
                    <small>
                      {text("Missing")} {r.missing_percent}% ·{" "}
                      {text("Duplicates")} {r.duplicate_percent}%
                    </small>
                  </div>
                  <span>{r.freshness}</span>
                  <a href={r.source_url} target="_blank" rel="noreferrer">
                    {text("Source document ↗")}
                  </a>
                </div>
              ))}
            </details>
          ))}
          {catalog.unavailable.map((r: any) => (
            <div className="source-feed" key={r.source_name}>
              <strong>{r.source_name}</strong>
              <span>{text("UNAVAILABLE")}</span>
              <p>{text(r.reason)}</p>
              <a href={r.source_url} target="_blank" rel="noreferrer">
                {text("Official source ↗")}
              </a>
            </div>
          ))}
          <details>
            <summary>{text("View external benchmark evaluation")}</summary>
            <p>{text(benchmark?.split || "")}</p>
            <p>{text(benchmark?.scope || "")}</p>
            <p>{text(benchmark?.promotion || "")}</p>
            <div className="extra-scroll">
              <table className="data-table">
                <thead>
                  <tr>
                    {[
                      "Model",
                      "Split",
                      "Records",
                      "MAE",
                      "RMSE",
                      "Precision",
                      "Recall",
                      "F1",
                      "False alarm rate",
                    ].map((x) => (
                      <th key={x}>{text(x)}</th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {(benchmark?.results || []).map((r: any) => (
                    <tr key={r.model + r.split}>
                      <td>{r.model}</td>
                      <td>{text(r.split)}</td>
                      <td>{r.records}</td>
                      {[
                        "mae",
                        "rmse",
                        "precision",
                        "recall",
                        "f1",
                        "false_alarm_rate",
                      ].map((k) => (
                        <td key={k}>{r[k].toFixed(2)}</td>
                      ))}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </details>
        </>
      )}
    </section>
  );
}
