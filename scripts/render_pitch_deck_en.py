"""English Preliminary Pitch deck in the SKY Innovation Spark visual theme (navy, white cards, red accents).

Numbers come from the same measured source as the Thai deck (imported from render_pitch_deck), so the two never diverge.
Print with: node frontend/scripts/print-deck.mjs docs/onetrustx_PreliminaryPitch_EN.html docs/onetrustx_PreliminaryPitch_EN.pdf
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import render_pitch_deck as base  # noqa: E402

ROOT, n, pct = base.ROOT, base.n, base.pct
FLOOD, FLIGHT, TRUST, RUNS = base.FLOOD, base.FLIGHT, base.TRUST, base.RUNS
F1, LEAD, SILENT_RAW, SILENT_VER = base.F1, base.LEAD, base.SILENT_RAW, base.SILENT_VER
CAUGHT, INJECTED = base.CAUGHT, base.INJECTED

CSS = """
@page { size: 1440px 810px; margin: 0; }
* { box-sizing: border-box; margin: 0; padding: 0; }
:root { --navy:#071428; --navy2:#0c2347; --red:#e5172b; --redsoft:#fde9ea; --ink:#0b1f3a; --mute:#5b6b82; --line:#d9e1ec; --green:#1f57c3; --greensoft:#e7efff; --white:#fff; }
html { font-family: 'Inter', sans-serif; color: var(--ink); -webkit-print-color-adjust: exact; print-color-adjust: exact; }
.slide { width: 1440px; height: 810px; position: relative; overflow: hidden; break-after: page; display: flex; flex-direction: column; padding: 38px 60px 24px;
  background: linear-gradient(160deg, #0a1b38 0%, var(--navy) 55%, #050d1d 100%); color: #fff; }
.slide:last-child { break-after: auto; }
.slide::before { content: ""; position: absolute; top: -30px; right: 96px; width: 44px; height: 120px; background: var(--red); transform: skewX(-32deg); }
.slide::after { content: ""; position: absolute; top: -30px; right: 36px; width: 44px; height: 120px; background: #2f5fb3; transform: skewX(-32deg); }
.head { position: relative; z-index: 2; }
.badge { display: inline-flex; align-items: center; gap: 12px; font-weight: 700; font-size: 17px; letter-spacing: .6px; text-transform: uppercase; color: #cfdcf0; }
.badge i { font-style: normal; width: 34px; height: 34px; border-radius: 8px; background: var(--red); color: #fff; display: inline-flex; align-items: center; justify-content: center; font-size: 19px; font-weight: 800; }
.brand { position: absolute; top: 44px; right: 190px; z-index: 3; font-weight: 800; letter-spacing: 3px; font-size: 15px; color: #fff; }
.brand b { color: #fff; }
.brand { border-bottom: 3px solid #fff; padding-bottom: 4px; }
h1 { font-family: 'Montserrat', sans-serif; font-weight: 800; font-size: 48px; line-height: 1.08; letter-spacing: -.5px; margin-top: 14px; text-transform: uppercase; max-width: 1150px; }
h1 em { font-style: normal; color: var(--red); }
.rule { width: 360px; height: 4px; margin: 12px 0 14px; background: linear-gradient(90deg, #fff 0 45%, var(--red) 45% 70%, #4a79c4 70%); border-radius: 2px; }
.sub { font-size: 19px; line-height: 1.5; color: #cfdcf0; max-width: 1150px; position: relative; z-index: 2; }
.sub b { color: #fff; }
.body { position: relative; z-index: 2; margin-top: 12px; display: flex; flex-direction: column; gap: 12px; flex: 1; justify-content: space-between; }
.row { display: flex; gap: 16px; } .col { display: flex; flex-direction: column; gap: 12px; }
.card { background: #fff; color: var(--ink); border-radius: 20px; padding: 18px 24px; position: relative; overflow: hidden; }
.card.dark { background: none; color: #fff; box-shadow: none; border-radius: 0; padding: 4px 0; overflow: visible; }
.card.red { border-left: 7px solid var(--red); }
.card.green { background: var(--greensoft); border-left: 7px solid var(--green); }
.card h3 { font-family: 'Montserrat', sans-serif; font-size: 22px; font-weight: 800; line-height: 1.25; }
.eyebrow { font-size: 13.5px; font-weight: 700; letter-spacing: 1.3px; text-transform: uppercase; color: var(--mute); }
.card.dark .eyebrow { color: #b7c9e6; }
.big { font-family: 'Montserrat', sans-serif; font-size: 52px; font-weight: 800; color: var(--red); line-height: 1; letter-spacing: -1px; }
.lbl { font-size: 16px; color: var(--mute); line-height: 1.4; margin-top: 4px; }
.chip { white-space: nowrap; display: inline-block; font-size: 13px; font-weight: 700; padding: 3px 11px; border-radius: 99px; background: #e8eef7; color: #26406a; letter-spacing: .3px; }
.chip.red { background: var(--redsoft); color: var(--red); } .chip.ok { background: var(--greensoft); color: var(--green); } .chip.sim { background: #fff; color: var(--red); border: 1.5px solid var(--red); } .chip.src { background: #e8eef7; color: #26406a; }
.flow { display: flex; align-items: stretch; gap: 8px; }
.node { flex: 1; background: #f3f6fb; border: 1px solid var(--line); border-top: 5px solid #26406a; border-radius: 12px; padding: 12px 8px; text-align: center; display: flex; flex-direction: column; justify-content: center; gap: 3px; color: var(--ink); }
.node b { font-size: 17.5px; line-height: 1.2; font-weight: 700; } .node small { font-size: 13.5px; color: var(--mute); line-height: 1.3; }
.node.hot { border-top-color: var(--red); background: var(--redsoft); } .node.grn { border-top-color: var(--green); background: var(--greensoft); } .node.amb { border-top-color: #4a79c4; background: #eef3fc; }
.arr { align-self: center; color: var(--red); font-size: 22px; font-weight: 800; }
table { width: 100%; border-collapse: collapse; font-size: 17px; }
th { text-align: left; font-size: 13.5px; letter-spacing: 1px; text-transform: uppercase; color: var(--mute); font-weight: 700; padding: 8px 12px; border-bottom: 2px solid var(--red); }
td { padding: 8px 12px; border-bottom: 1px solid var(--line); vertical-align: top; line-height: 1.4; }
td.k { font-weight: 800; white-space: nowrap; font-family: 'Montserrat', sans-serif; }
.foot { position: relative; z-index: 2; margin-top: auto; margin-top: 14px; display: flex; align-items: center; gap: 14px; padding: 8px 2px 0; background: none; font-size: 13.5px; color: #b7c9e6; line-height: 1.4; }
.foot .bang { flex: none; width: 28px; height: 28px; border-radius: 50%; background: var(--red); color: #fff; font-weight: 800; display: flex; align-items: center; justify-content: center; font-size: 17px; }
.foot .pg { margin-left: auto; font-weight: 800; color: #fff; white-space: nowrap; }
.bar { height: 28px; border-radius: 6px; }
.quote { text-align: center; font-family: 'Montserrat', sans-serif; font-weight: 800; font-size: 23px; line-height: 1.35; }
.quote span { color: var(--red); }
"""


def foot(note, page):
    return f"<div class='foot'><span class='bang'>!</span><span>{note}</span><span class='pg'>{page} / 8</span></div>"


def slide(num, tag, title, sub, body, note):
    s = f"<p class='sub'>{sub}</p>" if sub else ""
    return (
        f"<section class='slide'><span class='brand'>ONE <b>TRUSTX</b></span><div class='head'><span class='badge'><i>{num}</i>{tag}</span>"
        f"<h1>{title}</h1><div class='rule'></div>{s}</div><div class='body'>{body}</div>{foot(note, num)}</section>"
    )


def s1():
    chain = [
        ("Heavy rain", "116 mm on 25 Sep", ""),
        ("Flooded roads", "CAAT notice, 26 Sep", ""),
        ("Staff can't arrive", "baggage carts failed too", "amb"),
        ("Baggage backlog", "10,000+ bags in 4 days", "hot"),
        ("Flights affected", "cuts · cargo suspended", "hot"),
    ]
    flow = "<span class='arr'>→</span>".join(
        f"<div class='node {c}'><b>{t}</b><small>{d}</small></div>" for t, d, c in chain
    )
    stats = [
        ("24M", "bags mishandled worldwide in 2025"),
        ("$6.3B", "annual industry cost (~$260 per bag)"),
        ("39%", "of mishandling happens at transfer"),
    ]
    st = "".join(
        f"<div class='card' style='flex:1'><div class='big'>{a}</div><div class='lbl'>{b}</div><span class='chip src'>SITA 2026</span></div>"
        for a, b in stats
    )
    body = f"""<div class='card'><div class='eyebrow' style='margin-bottom:10px'>Real incident · Suvarnabhumi, 25–30 Sep 2026</div><div class='flow'>{flow}</div>
<p style='margin-top:12px;font-size:16.5px;color:var(--mute);line-height:1.5'>On 29 Sep Thai Airways' CEO said ~5,000 bags remained; ~8,000 were still outstanding on 30 Sep. 131 military personnel were deployed, cargo acceptance was suspended 30 Sep–6 Oct and flights were reduced.</p></div>
<div class='row'>{st}</div><div class='quote'>The question we chose: <span>when baggage is delayed, where is it stuck, why — and what do we do first?</span></div>"""
    return slide(
        1,
        "Problem / Pain Point",
        "A baggage delay is not just <em>a baggage problem</em>",
        "During disruptions, baggage, flight and ground-resource signals sit in different systems and teams — so the <b>bottleneck, its impact and the next action are found late.</b>",
        body,
        "Sources: Open-Meteo (rain), CAAT 30/2569, The Nation, The Star (incident), SITA Baggage IT Insights 2026. “Mishandled” = delayed, damaged or misrouted — not permanently lost. News figures change day to day.",
    )


def s2():
    stages = [
        ("Check-in", ""),
        ("Screening", ""),
        ("Sorting", "amb"),
        ("Loading", "hot"),
        ("Transfer", "hot"),
        ("Arrival", "amb"),
    ]
    fl = "<span class='arr'>→</span>".join(
        f"<div class='node {c}'><b>{t}</b></div>" for t, c in stages
    )
    body = f"""<div class='row' style='align-items:stretch'>
<div class='card red' style='flex:1.15'><span class='chip red'>PRIMARY USER</span><h3 style='margin:10px 0 6px;font-size:25px'>Baggage / Ground Operations Controller</h3>
<div class='lbl' style='font-size:17px'>Decides every minute where to send people and equipment first — with data spread across systems, and a lot of calling and walking to confirm it.</div></div>
<div class='card' style='flex:1'><span class='chip'>SECONDARY USERS & BENEFICIARIES</span>
<div style='margin-top:10px;font-size:17.5px;line-height:1.75'><b>Airline OCC</b> — wait for bags or send them on<br><b>Airport Operations</b> — see across teams<br><b>Ground handlers</b> — get a work order when short-staffed<br><b>Passengers</b> — bags arrive with them</div></div></div>
<div class='card'><div class='eyebrow' style='margin-bottom:10px'>Baggage journey — every arrow is a handoff between teams</div><div class='flow'>{fl}</div>
<p style='margin-top:12px;font-size:16.5px;color:var(--mute);line-height:1.5'>SKY itself points to handoffs as where baggage goes wrong, and SITA finds <b style='color:var(--red)'>39%</b> of mishandling occurs at transfer — many parties, limited connection time.</p></div>
<div class='quote'>When baggage stops moving, <span>who knows WHY first?</span></div>"""
    return slide(
        2,
        "Target User / Stakeholder",
        "Who feels it — and <em>where it breaks</em>",
        None,
        body,
        "Sources: SKY Innovation Spark Kick-off (1 Oct 2026) on baggage process and handoffs; SITA Baggage IT Insights 2026.",
    )


def s3():
    layers = [
        (
            "Data Integration",
            "Scans, flight schedule and staffing become one event format.",
        ),
        (
            "Trusted Event History",
            "Every record has a source, a time and a freshness check — auditable.",
        ),
        ("Common Operational State", "One shared status of the six baggage stages."),
        (
            "AI Decision Intelligence",
            "Detect bottleneck · Predict at-risk flights · Recommend order · Coordinate owners",
        ),
    ]
    cards = "".join(
        f"<div class='card red' style='padding:12px 22px'><h3 style='font-size:19px'>{t}</h3><div class='lbl' style='font-size:15.5px;margin-top:2px'>{d}</div></div>"
        for t, d in layers
    )
    body = f"""<div class='row' style='align-items:stretch;flex:1'>
<div class='col' style='flex:1.25'>{cards}</div>
<div class='col' style='flex:1'>
<div class='card green'><div class='eyebrow' style='color:var(--green)'>Overlay, not replacement</div><h3 style='margin:8px 0 6px;font-size:23px'>We don't build another baggage tracker</h3><div class='lbl' style='font-size:16.5px;color:#2b4a3c'>BRS already tracks bags. We take signals from BRS, AODB and ground teams and work out where it is stuck, what it affects and what to do first.</div></div>
<div class='card'><div class='eyebrow'>Four questions, one screen</div><div style='font-size:18px;line-height:1.85;margin-top:8px;font-weight:600'>① Is it normal?<br>② Which stage is stuck?<br>③ Which flights, how many bags?<br>④ What first — and by when?</div></div></div></div>"""
    return slide(
        3,
        "Proposed Solution",
        "One TrustX: <em>baggage disruption intelligence</em>",
        "Combines baggage, flight, resource and disruption signals to <b>detect bottlenecks early, predict downstream impact and recommend recovery priorities</b> — the operator decides.",
        body,
        "Same four layers as One TrustX in round one, applied to baggage data. The system recommends; people decide; no airport equipment is controlled.",
    )


def s4():
    steps = [
        ("Ingest", "scans · schedule · staffing", ""),
        ("Verify & label", "source · freshness · duplicates", ""),
        ("Shared state", "6 stages: waiting, how long", "amb"),
        ("Detect", "stage over threshold", "hot"),
        ("Predict", "flights that won't make it", "hot"),
        ("Recommend", "order by hold-close", "hot"),
        ("Human decides", "approve · reject · edit", "grn"),
    ]
    fl = "<span class='arr'>→</span>".join(
        f"<div class='node {c}'><b>{t}</b><small>{d}</small></div>" for t, d, c in steps
    )
    stg = [
        ("Check-in", "OK", "ok", "entry"),
        ("Screening", "OK", "ok", "0 bags"),
        ("Sorting", "OK", "ok", "27 bags · 5 min"),
        ("Loading", "DELAY", "red", "202 bags · 35 min"),
        ("Transfer", "OK", "ok", "24 bags · 25 min"),
        ("Arrival", "OK", "ok", "129 bags · 25 min"),
    ]
    st = "".join(
        f"<div style='flex:1;border-radius:12px;padding:10px 12px;{'background:var(--redsoft);border:1px solid #f3b4ba' if c == 'red' else 'background:#f3f6fb;border:1px solid var(--line)'}'><span class='chip {c}'>{s}</span><div style='font-weight:800;font-size:17px;margin-top:6px'>{t}</div><div style='font-size:13.5px;color:var(--mute)'>{d}</div></div>"
        for t, s, c, d in stg
    )
    body = f"""<div class='card dark' style='padding:14px 18px'><div class='flow'>{fl.replace("background:#f3f6fb", "")}</div></div>
<div class='card'><div style='display:flex;justify-content:space-between;align-items:center'><div class='eyebrow'>Example from the model · flood scenario · 08:30</div><span class='chip sim'>SIMULATED DATA</span></div>
<div class='row' style='margin-top:10px;gap:10px'>{st}</div>
<div class='row' style='margin-top:12px'>
<div style='flex:1;font-size:16.5px;line-height:1.65'><b style='color:var(--red)'>IMPACT</b> 3 of 10 flights at risk · 60 bags at risk, 44 transfer<br><b style='color:var(--green)'>CAUSE</b> (if ground data connected) staff at 55% of plan, carts 4 of 5</div>
<div style='flex:1;border-left:2px solid var(--line);padding-left:18px;font-size:16.5px;line-height:1.65'><b style='color:var(--red)'>RECOMMEND</b> give loading capacity to TT403 first (closes 08:55), then TT404, TT405<br><span class='chip red'>OWNER: GROUND HANDLER · HUMAN APPROVAL REQUIRED</span></div></div></div>
<div class='sub' style='font-size:16.5px;color:#cfdcf0'>Without ground-handler data the system still shows <b>where</b> it is stuck — and says “cause unknown” instead of guessing.</div>"""
    return slide(
        4,
        "How It Works / Solution Journey",
        "From signal to <em>decision</em>",
        None,
        body,
        "Computed by the simulation (seed 42) on synthetic data — not real airport data. Try it at onetrustx.vercel.app/baggage",
    )


def s5():
    rows = [
        (
            "BRS / BHS",
            "Where is this bag? Right aircraft? Alerts for no-show bags and wrong container.",
            "Reads flow by stage against flight deadlines: where it is stuck and which flights are at risk.",
        ),
        (
            "AODB",
            "When does each flight depart and arrive, which gate.",
            "Uses it as the deadline for prioritising — no duplication.",
        ),
        (
            "A-CDM",
            "Airport partners working to flight milestones.",
            "Not rebuilt. Adds per-flight baggage-readiness risk as one more input.",
        ),
        (
            "Ground handler",
            "Knows own staffing, not the whole baggage line.",
            "Gets the order of flights to serve first when people are short.",
        ),
    ]
    tb = "".join(
        f"<tr><td class='k'>{a}</td><td>{b}</td><td>{c}</td></tr>" for a, b, c in rows
    )
    body = f"""<div class='card' style='padding:8px 20px'><table><tr><th style='width:150px'>System</th><th style='width:44%'>Answers</th><th>One TrustX adds</th></tr>{tb}</table></div>
<div class='row' style='align-items:stretch'>
<div class='card green' style='flex:1.3'><div class='eyebrow' style='color:var(--green)'>The line to remember</div><div style='font-family:Montserrat;font-weight:800;font-size:25px;line-height:1.35;margin-top:6px'>BRS tracks the bag.<br>One TrustX manages the disruption around the bag.</div><div class='lbl' style='margin-top:6px'>We build on existing signals — we don't claim BRS can't do something.</div></div>
<div class='card' style='flex:1'><div class='eyebrow'>Trusted data</div><div style='font-size:18px;line-height:1.6;margin-top:8px'>Every event keeps its source, time and the decision made on it — traceable end to end.</div></div></div>"""
    return slide(
        5,
        "Value & Differentiation",
        "How we differ from what <em>SKY already runs</em>",
        None,
        body,
        "BRS capabilities are taken from SKY ICT's public project page; actual deployments may do more — to be confirmed with SKY. A-CDM and AODB as described at Kick-off.",
    )


def s6():
    need = [
        ("BRS / BHS", "Scan counts per stage, per flight", "Required"),
        ("AODB", "Departure times, on-block times, gate", "Required"),
        ("DCS / BRS", "Expected bags per flight, connecting flight", "Required"),
        ("Ground handler", "Staff vs plan, baggage carts", "Cause"),
        ("BHS", "Belt and sorter status", "Cause"),
    ]
    tb = "".join(
        f"<tr><td class='k'>{a}</td><td>{b}</td><td><span class='chip {'ok' if c == 'Required' else ''}'>{c}</span></td></tr>"
        for a, b, c in need
    )
    body = f"""<div class='row' style='align-items:stretch;flex:1'>
<div class='card' style='flex:1.15;padding:10px 20px'><div class='eyebrow' style='margin:6px 0'>Data needed — aggregate counts, no personal data</div><table>{tb}</table>
<p style='font-size:13.5px;color:var(--mute);margin:6px 0 2px;line-height:1.4'>To confirm with SKY: BRS can export per-stage scan timestamps as aggregate counts.</p>
<div style='border-top:1px solid var(--line);margin-top:6px;padding-top:6px;font-size:14.5px;line-height:1.5'><b style='color:var(--red)'>RISK → MITIGATION</b><br>No handler data → still works, just no cause<br>Scans lost or late → asks for verification, never guesses<br>Thresholds differ in reality → validate with experts first</div></div>
<div class='col' style='flex:1'>
<div class='card'><h3 style='margin-bottom:6px'>How it would run</h3><div style='font-size:17px;line-height:1.7'>① Read-only<br>② A human approves every recommendation<br>③ Controls no equipment<br>④ If One TrustX stops, existing systems carry on</div></div>
<div class='card' style='padding:8px'><img src='screenshots/report/live-baggage-flood.jpg' style='width:100%;height:205px;object-fit:cover;object-position:top left;border-radius:12px;display:block'><div style='font-size:13px;color:var(--mute);margin:6px 8px 2px'>Working prototype: onetrustx.vercel.app/baggage (synthetic data)</div></div></div></div>"""
    return slide(
        6,
        "Feasibility",
        "Buildable — <em>on data SKY already has</em>",
        None,
        body,
        "The prototype runs on synthetic data with every parameter labelled (15: real 2 · benchmark 1 · derived 1 · assumption 11). Main risks: access to ground-handler data and expert validation of thresholds.",
    )


def s7():
    top = FLOOD["bags_missed_total_plan"]
    w2 = FLOOD["bags_missed_total_priority"] / top * 78
    kpis = [
        (
            pct(FLOOD["bags_missed_reduction_pct"]),
            "fewer bags left behind",
            f"{n(top)} → {n(FLOOD['bags_missed_total_priority'])} bags over {RUNS} runs",
        ),
        (
            pct(FLOOD["transfer_bags_missed_reduction_pct"]),
            "fewer transfer bags left behind",
            f"{n(FLOOD['transfer_bags_missed_total_plan'])} → {n(FLOOD['transfer_bags_missed_total_priority'])} bags",
        ),
        (
            f"{F1}%",
            "F1 of flight-level warnings",
            f"precision {FLIGHT['flight_precision']} · recall {FLIGHT['flight_recall']}",
        ),
        (
            f"{LEAD['median']:g} min",
            "warning before first bag is missed",
            f"range {LEAD['min']}–{LEAD['max']} min",
        ),
        (
            f"{pct(SILENT_RAW, 0)} → {pct(SILENT_VER, 0)}",
            "status wrong without a warning, when data has faults",
            f"{n(CAUGHT)}/{n(INJECTED)} injected faults caught · 0/{n(TRUST['clean_records'])} good records rejected",
        ),
    ]
    kp = "".join(
        f"<div class='card' style='padding:12px 18px'><div style='display:flex;align-items:baseline;gap:12px'><div style='font-family:Montserrat;font-weight:800;font-size:30px;color:var(--red);white-space:nowrap'>{a}</div><div style='font-size:15.5px;font-weight:700;line-height:1.25'>{b}</div></div><div style='font-size:13px;color:var(--mute);margin-top:1px'>{c}</div></div>"
        for a, b, c in kpis
    )
    body = f"""<div class='row' style='align-items:stretch;flex:1'>
<div class='col' style='flex:1.4;justify-content:space-between'>
<div class='card'><div style='display:flex;justify-content:space-between'><div class='eyebrow'>Bags left behind · flood scenario · {RUNS} runs combined</div><span class='chip sim'>SIMULATED</span></div>
<div style='margin-top:12px;font-size:15.5px;font-weight:600'>Capacity shared equally between flights (today's baseline — an assumption)</div><div style='display:flex;align-items:center;gap:12px'><div class='bar' style='width:78%;background:#8da2c0'></div><b style='font-size:21px'>{n(top)}</b></div>
<div style='margin-top:10px;font-size:15.5px;font-weight:600'>Served in the order One TrustX recommends</div><div style='display:flex;align-items:center;gap:12px'><div class='bar' style='width:{w2:.1f}%;background:var(--red)'></div><b style='font-size:21px'>{n(FLOOD["bags_missed_total_priority"])}</b></div></div>
<div class='card dark' style='font-size:15.5px;line-height:1.6'><b style='color:#ff8d97'>NOT MEASURABLE YET — we will measure it in the prototype phase</b><br>People's coordination time: controllers run the same scenario with and without the screen; time from first signal to an owner accepting the task.<br>Flight delay minutes: needs a rule for holding flights, or comparison with historical data.</div></div>
<div class='col' style='flex:1.1;gap:8px;justify-content:space-between'>{kp}</div></div>"""
    return slide(
        7,
        "Expected Impact",
        "Impact we expect — <em>and can measure</em>",
        None,
        body,
        f"{RUNS} simulated runs per scenario on synthetic data — not airport results. The reduction depends on the assumed baseline (equal sharing); if handlers already prioritise well, the gain is smaller. Ground truth comes from the same simulation.",
    )


def s8():
    ph = [
        (
            "1",
            "Validate with experts",
            "Thresholds, hold-close time, how handlers prioritise today, whether BRS exports per-stage data.",
        ),
        (
            "2",
            "Refine scenarios",
            "Add inbound-bag backlog as in the real incident; Normal · Staff shortage · Sorter fault · Flood.",
        ),
        (
            "3",
            "Test with users",
            "Controllers use the screen; measure coordination time, false alerts and usefulness of advice.",
        ),
        (
            "4",
            "Shadow mode",
            "Anonymised historical data, read-only, compared with what actually happened.",
        ),
    ]
    cards = "".join(
        f"<div class='card' style='flex:1;border-top:6px solid {'var(--green)' if i == 3 else 'var(--red)'}'><div style='font-family:Montserrat;font-weight:800;font-size:34px;color:{'var(--green)' if i == 3 else 'var(--red)'}'>{a}</div><h3 style='font-size:19px;margin:2px 0 6px'>{b}</h3><div style='font-size:15px;color:var(--mute);line-height:1.5'>{c}</div></div>"
        for i, (a, b, c) in enumerate(ph)
    )
    vision = ["Baggage", "Turnaround", "Gate", "Passenger", "Cargo"]
    vf = "<span class='arr'>→</span>".join(
        f"<div class='node {'hot' if i == 0 else ''}' style='padding:9px 6px'><b>{v}</b></div>"
        for i, v in enumerate(vision)
    )
    body = f"""<div class='row' style='align-items:stretch'>{cards}</div>
<div class='card'><div class='eyebrow' style='margin-bottom:8px'>Vision — expand only after the value is proven</div><div class='flow'>{vf}</div></div>
<div class='quote' style='color:#fff'>Start with baggage, where every minute and every handoff matters.<br><span>Then grow into a trusted data layer for the Future Aviation Hub.</span></div>"""
    return slide(
        8,
        "Next Step / Development Plan",
        "Plan for the <em>prototype phase</em>",
        None,
        body,
        "Dates other than the 22 Oct 2026 pitch will follow the SKY Innovation Spark organisers' announcements.",
    )


def build(output: Path):
    page = f"""<!doctype html><html lang='en'><head><meta charset='utf-8'><title>One TrustX · Preliminary Pitch</title>
<link href='https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Montserrat:wght@700;800&display=swap' rel='stylesheet'>
<style>{CSS}</style></head><body style='background:#071428'>{"".join(f() for f in (s1, s2, s3, s4, s5, s6, s7, s8))}</body></html>"""
    output.write_text(page)
    print(output)


if __name__ == "__main__":
    build(ROOT / "docs/onetrustx_PreliminaryPitch_EN.html")
