import { text } from "../i18n";
import { useEffect, useState } from "react";
import { Database, ExternalLink, RefreshCw } from "lucide-react";
import { api } from "../services/api";
export default function DataSources() {
  const [data, setData] = useState<any>(null),
    [error, setError] = useState("");
  async function load() {
    setError("");
    try {
      setData(await api("/public/context"));
    } catch (e) {
      setError((e as Error).message);
    }
  }
  useEffect(() => {
    load();
  }, []);
  return (
    <>
      <section className="panel">
        <div className="panel-heading">
          <div>
            <h2>{text("Know what supports the decision.")}</h2>
            <p>
              {text(
                " Public context and synthetic operations have different purposes. ",
              )}
            </p>
          </div>
          <Database size={21} />
        </div>
        <div className="source-explanation">
          <strong>
            {text("Operations are synthetic. Outcomes are simulated.")}
          </strong>
          <p>
            {text(
              " Queues, passenger journeys, staffing, baggage and flight fixtures come from a deterministic local generator. Public aircraft positions do not provide passenger counts or queue measurements. ",
            )}
          </p>
        </div>
        <div className="source-matrix">
          {text(
            [
              [
                "SYNTHETIC",
                "Flights · 580 anonymous journeys · checkpoint flows",
                "Deterministic fixtures, never airport records",
              ],
              [
                "SIMULATED",
                "Forecasts · what-if outcomes · Safe Time",
                "Calculated by the simulation and routing engines",
              ],
              [
                "ASSUMPTION",
                "Terminal layout · processing rates · confidence",
                "Explicit modelling choices, not validated airport facts",
              ],
              [
                "REAL_PUBLIC",
                "Airport metadata · weather · aircraft states",
                "Cached public context, kept separate from operations",
              ],
              [
                "DERIVED",
                "Transformed values with source lineage",
                "Reserved for source-based features; no causal proof",
              ],
            ].map(([type, scope, note]) => (
              <div key={type}>
                <span className="tiny-tag">{text(type)}</span>
                <strong>
                  {text(scope)}
                  <small>{text(note)}</small>
                </strong>
              </div>
            )),
          )}
        </div>
      </section>
      <section className="panel section-gap">
        <div className="panel-heading">
          <div>
            <h2>{text("Public feed provenance")}</h2>
            <p>
              {text(
                " Refresh reads the local cache; it does not silently fetch live operational data. ",
              )}
            </p>
          </div>
          <button onClick={load}>
            <RefreshCw size={14} />
            {text(" Refresh status ")}
          </button>
        </div>
        {text(
          error && (
            <p className="error" role="alert">
              {text(error)}
            </p>
          ),
        )}
        {text(
          !data && !error && (
            <p role="status">{text("Loading source metadata…")}</p>
          ),
        )}
        {text(
          data &&
            Object.entries(data.feeds || {}).map(([name, value]) => {
              const feed = value as any;
              return (
                <div className="source-feed" key={name}>
                  <div>
                    <strong>
                      {text(name.replaceAll("_", " "))}
                      {text(" · ")}
                      {text(feed.provider)}
                    </strong>
                    <small>
                      {text(
                        feed.retrieved_at
                          ? "Retrieved " +
                              new Date(feed.retrieved_at).toLocaleString()
                          : "No successful retrieval",
                      )}
                    </small>
                  </div>
                  <span className="tiny-tag">{text(feed.source_type)}</span>
                  <span className={feed.stale ? "risk-tag" : "neutral-tag"}>
                    {text(feed.stale ? "CACHE STALE" : "CACHE FRESH")}
                  </span>
                  {text(
                    feed.documentation_url && (
                      <a
                        href={feed.documentation_url}
                        target="_blank"
                        rel="noreferrer"
                        aria-label={"Open " + name + " source"}
                      >
                        <ExternalLink size={15} />
                      </a>
                    ),
                  )}
                </div>
              );
            }),
        )}
        <p className="note">
          {text(
            " A stale or unavailable public feed never becomes a fresh synthetic measurement. These feeds do not determine operational confidence in this MVP. ",
          )}
        </p>
      </section>
    </>
  );
}
