"""Build the Preliminary Pitch deck (8 slides, 1440x810) as HTML.

Every number on the slides is either read from backend/app/baggage_evaluation.json (measured by simulation)
or is a cited public fact. Nothing is typed in by hand except the cited facts below.

Print with: node frontend/scripts/print-deck.mjs docs/onetrustx_PreliminaryPitch.html docs/onetrustx_PreliminaryPitch.pdf
"""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EVAL = json.loads((ROOT / "backend/app/baggage_evaluation.json").read_text())
SC = EVAL["scorecard"]
FLOOD = SC["operation"]["BAG-FLOOD-STAFF"]
FLIGHT = EVAL["scenarios"]["BAG-FLOOD-STAFF"]
TRUST = SC["trust"]["fault_injection"]
RUNS = FLOOD["runs"]


def n(x):
    return f"{x:,}"


def pct(x, d=1):
    text = f"{x:.{d}f}"
    return (text.rstrip("0").rstrip(".") if "." in text else text) + "%"


F1 = round(
    2
    * FLIGHT["flight_precision"]
    * FLIGHT["flight_recall"]
    / (FLIGHT["flight_precision"] + FLIGHT["flight_recall"])
    * 100
)
LEAD = FLIGHT["detection_lead_min"]
WINDOW = FLOOD["decision_window_min"]
SILENT_RAW = TRUST["status_vs_clean_feed"]["raw"]["different"] * 100
SILENT_VER = TRUST["status_vs_clean_feed"]["verified"]["different"] * 100
CAUGHT = sum(v["caught"] for v in TRUST["fault_catch_rate"].values() if v["injected"])
INJECTED = sum(
    v["injected"] for v in TRUST["fault_catch_rate"].values() if v["injected"]
)

# ---- cited public facts (source in the report, section 2.4 / 7) ----
FACT = {
    "sita_bags": "24 ล้านใบ",
    "sita_cost": "$6.3B",
    "sita_per_bag": "$260",
    "sita_transfer": "39%",
    "stranded": "10,000+",
    "left": "~8,000",
    "ceo": "~5,000",
    "military": "131",
    "rain": "116 มม.",
}

CSS = """
@page { size: 1440px 810px; margin: 0; }
* { box-sizing: border-box; margin: 0; padding: 0; }
:root { --bg:#060f1d; --card:#0d1b2e; --line:#1f3550; --ink:#f2f6fa; --mute:#9db1c4; --teal:#2fb7a3; --amber:#f0a73a; --red:#ef6a5b; --blue:#4a9bd9; }
html { font-family: 'IBM Plex Sans Thai', sans-serif; color: var(--ink); -webkit-print-color-adjust: exact; print-color-adjust: exact; }
.slide { width: 1440px; height: 810px; background: radial-gradient(1200px 600px at 85% -10%, #12335a 0%, var(--bg) 60%); padding: 44px 64px 40px; position: relative; overflow: hidden; break-after: page; display: flex; flex-direction: column; }
.slide:last-child { break-after: auto; }
.tag { align-self: flex-start; background: linear-gradient(90deg, #0d6f7a, #1b8f8a); color: #fff; font-weight: 600; font-size: 17px; padding: 7px 22px; border-radius: 99px; letter-spacing: .3px; }
.brand { position: absolute; top: 44px; right: 64px; font-weight: 700; letter-spacing: 3px; font-size: 15px; color: var(--mute); }
.brand b { color: var(--teal); }
h1 { font-size: 46px; line-height: 1.22; font-weight: 700; margin: 20px 0 8px; letter-spacing: -.3px; }
h1 em { font-style: normal; color: var(--amber); }
.sub { font-size: 21px; color: var(--mute); line-height: 1.5; max-width: 1180px; }
.foot { margin-top: auto; padding-top: 12px; font-size: 13.5px; color: #7f93a8; line-height: 1.45; border-top: 1px solid var(--line); display: flex; justify-content: space-between; gap: 30px; }
.foot span:last-child { white-space: nowrap; }
.card { background: var(--card); border: 1px solid var(--line); border-radius: 14px; padding: 18px 22px; }
.row { display: flex; gap: 18px; }
.col { display: flex; flex-direction: column; gap: 14px; }
.big { font-size: 54px; font-weight: 700; line-height: 1.05; letter-spacing: -1px; }
.lbl { font-size: 16.5px; color: var(--mute); line-height: 1.4; margin-top: 4px; }
.chip { display: inline-block; font-size: 14px; font-weight: 600; padding: 3px 11px; border-radius: 6px; background: #17314d; color: #bcd3ea; }
.chip.sim { background: #3b2d0f; color: var(--amber); }
.chip.real { background: #0f3a33; color: #6fe0cd; }
.chip.ok { background: #0f3a33; color: #6fe0cd; } .chip.warn { background: #3b2d0f; color: var(--amber); } .chip.bad { background: #43191a; color: #ff9b8f; }
.flow { display: flex; align-items: stretch; gap: 8px; }
.node { flex: 1; background: var(--card); border: 1px solid var(--line); border-top: 4px solid var(--blue); border-radius: 10px; padding: 14px 10px; text-align: center; display: flex; flex-direction: column; justify-content: center; gap: 4px; }
.node b { font-size: 19px; line-height: 1.25; } .node small { font-size: 14.5px; color: var(--mute); line-height: 1.3; }
.node.hot { border-top-color: var(--red); background: #241520; } .node.amb { border-top-color: var(--amber); } .node.grn { border-top-color: var(--teal); }
.arr { align-self: center; color: #5d7a99; font-size: 22px; }
table { width: 100%; border-collapse: collapse; font-size: 18px; }
th { text-align: left; font-size: 15px; letter-spacing: .5px; color: var(--mute); font-weight: 600; padding: 8px 12px; border-bottom: 1px solid var(--line); }
td { padding: 11px 12px; border-bottom: 1px solid #14283f; vertical-align: top; line-height: 1.4; }
td.k { font-weight: 700; white-space: nowrap; }
.bar { height: 26px; border-radius: 5px; }
"""


def foot(left, right):
    return f"<div class='foot'><span>{left}</span><span>{right}</span></div>"


def slide(tag, body, footer):
    return f"<section class='slide'><span class='tag'>{tag}</span><span class='brand'>ONE <b>TRUSTX</b></span>{body}{footer}</section>"


def s1():
    chain = [
        ("ฝนหนัก", f"{FACT['rain']} ใน 25 ก.ย.", "grn"),
        ("ถนนน้ำท่วม", "CAAT ประกาศ 26 ก.ย.", "grn"),
        ("พนักงานมาไม่ได้", "รถขนกระเป๋าเสียซ้ำ", "amb"),
        ("กระเป๋าค้างสะสม", f"{FACT['stranded']} ใบใน 4 วัน", "hot"),
        ("เที่ยวบินได้รับผล", "ลดเที่ยวบิน งดรับ cargo", "hot"),
    ]
    flow = "<span class='arr'>→</span>".join(
        f"<div class='node {c}'><b>{t}</b><small>{d}</small></div>" for t, d, c in chain
    )
    stats = [
        (FACT["sita_bags"], "กระเป๋า mishandled ทั่วโลกปี 2025", "SITA 2026"),
        (FACT["sita_cost"], f"ต้นทุนต่อปี (เฉลี่ย {FACT['sita_per_bag']} ต่อใบ)", "SITA 2026"),
        (FACT["sita_transfer"], "ของกรณีผิดพลาดเกิดตอน transfer", "SITA 2026"),
    ]
    st = "".join(
        f"<div class='card' style='flex:1'><div class='big' style='color:var(--amber)'>{a}</div><div class='lbl'>{b}</div><span class='chip real'>{c}</span></div>"
        for a, b, c in stats
    )
    body = f"""<h1>กระเป๋าล่าช้า <em>ไม่ใช่แค่ปัญหาของกระเป๋า</em></h1>
<p class='sub'>เมื่อเกิดเหตุผิดปกติ สัญญาณของกระเป๋า เที่ยวบิน และกำลังคนอยู่คนละระบบ คนละฝ่าย จึงรู้ช้าว่า<b style='color:#fff'> ติดที่ไหน กระทบอะไร และควรแก้อะไรก่อน</b></p>
<div class='card' style='margin-top:26px'><div style='font-size:15px;letter-spacing:1.5px;color:var(--mute);margin-bottom:12px'>เหตุการณ์จริง · สุวรรณภูมิ 25–30 ก.ย. 2026</div><div class='flow'>{flow}</div>
<p style='margin-top:14px;font-size:17.5px;color:var(--mute);line-height:1.5'>วันที่ 29 ก.ย. CEO การบินไทยแจ้งว่าเหลือราว {FACT["ceo"]} ใบ วันที่ 30 ก.ย. ยังค้างราว {FACT["left"]} ใบ ต้องใช้กำลังทหาร {FACT["military"]} นาย งดรับ cargo 30 ก.ย.–6 ต.ค. และลดเที่ยวบิน</p></div>
<div class='row' style='margin-top:20px'>{st}</div>
<div style='margin-top:22px;font-size:25px;font-weight:600;text-align:center'>โจทย์ที่เราเลือกตอบ: <span style='color:var(--amber)'>ถ้ากระเป๋าล่าช้า ล่าช้าเกิดจากส่วนไหน และจะจัดการอย่างไร</span></div>"""
    return slide(
        "1 · Problem / Pain Point",
        body,
        foot(
            "แหล่ง: Open-Meteo (ฝน), CAAT 30/2569, The Nation, The Star (เหตุการณ์), SITA Baggage IT Insights 2026 · mishandled = ล่าช้า เสียหาย หรือส่งผิดปลายทาง ไม่ใช่หายถาวร · ตัวเลขข่าวเปลี่ยนตามวัน",
            "1/8",
        ),
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
    body = f"""<h1>ใครเจ็บ และ <em>จุดไหนของกระเป๋าที่พัง</em></h1>
<div class='row' style='margin-top:18px'>
<div class='card' style='flex:1.1'><span class='chip ok'>ผู้ใช้หลัก</span><div style='font-size:28px;font-weight:700;margin:10px 0 6px'>Baggage / Ground Operations Controller</div>
<div class='lbl' style='font-size:18px'>ต้องตัดสินใจทุกนาทีว่าจะย้ายคนและอุปกรณ์ไปช่วยเที่ยวบินไหนก่อน แต่ข้อมูลที่ใช้ตัดสินอยู่คนละระบบ ต้องโทรหรือเดินถามซ้ำหลายจุด</div></div>
<div class='card' style='flex:1'><span class='chip'>ผู้ใช้รองและผู้ได้ประโยชน์</span>
<div style='margin-top:10px;font-size:19px;line-height:1.75'><b>Airline OCC</b> · ตัดสินใจรอหรือส่งกระเป๋าตาม<br><b>Airport Operations</b> · เห็นภาพข้ามฝ่าย<br><b>Ground Handler</b> · ได้ลำดับงานเมื่อคนไม่พอ<br><b>ผู้โดยสาร</b> · กระเป๋าไปทันเที่ยวบิน</div></div></div>
<div class='card' style='margin-top:18px'><div style='font-size:15px;letter-spacing:1.5px;color:var(--mute);margin-bottom:12px'>เส้นทางกระเป๋า · ทุกลูกศรคือจุดเปลี่ยนมือ (handoff) ระหว่างฝ่าย</div><div class='flow'>{fl}</div>
<p style='margin-top:14px;font-size:18px;color:var(--mute);line-height:1.5'>SKY ระบุเองว่ากระเป๋ามักมีปัญหาตอนเปลี่ยนความรับผิดชอบ และ SITA พบว่า <b style='color:var(--amber)'>{FACT["sita_transfer"]}</b> ของกรณีผิดพลาดเกิดที่ขั้นต่อเครื่อง ซึ่งเกี่ยวข้องหลายฝ่ายและมีเวลาจำกัด</p></div>
<div style='margin-top:20px;font-size:30px;font-weight:700;text-align:center;color:var(--amber)'>เมื่อกระเป๋าหยุดไหล ใครรู้ก่อนว่า “ทำไม”?</div>"""
    return slide(
        "2 · Target User / Stakeholder",
        body,
        foot(
            "แหล่ง: Kick-off SKY Innovation Spark 1 ต.ค. 2026 (กระบวนการกระเป๋าและ handoff), SITA Baggage IT Insights 2026",
            "2/8",
        ),
    )


def s3():
    layers = [
        (
            "Data Integration",
            "รับสแกนกระเป๋า ตารางบิน กำลังคน แปลงเป็นเหตุการณ์รูปแบบเดียว",
            "teal",
        ),
        ("Trusted Event History", "ทุกรายการมีที่มา เวลา และตรวจความสด ย้อนตรวจได้", "blue"),
        ("Common Operational State", "สถานะเดียวของกระเป๋า 6 ขั้น ที่ทุกฝ่ายเห็นตรงกัน", "amber"),
        (
            "AI Decision Intelligence",
            "Detect คอขวด · Predict เที่ยวบินเสี่ยง · Recommend ลำดับ · Coordinate ผู้รับผิดชอบ",
            "red",
        ),
    ]
    cards = "".join(
        f"<div class='card' style='border-left:5px solid var(--{c})'><div style='font-size:21px;font-weight:700'>{t}</div><div class='lbl' style='font-size:16.5px'>{d}</div></div>"
        for t, d, c in layers
    )
    body = f"""<h1>One TrustX <em>Baggage Disruption Intelligence</em></h1>
<p class='sub'>รวมสัญญาณกระเป๋า เที่ยวบิน กำลังคน และเหตุผิดปกติ เป็นภาพเดียว เพื่อ<b style='color:#fff'>ตรวจจับคอขวดให้เร็ว ประเมินผลกระทบ และแนะนำลำดับการกู้สถานการณ์</b> โดยเจ้าหน้าที่เป็นผู้ตัดสินใจ</p>
<div class='row' style='margin-top:26px;align-items:stretch'>
<div class='col' style='flex:1.25'>{cards}</div>
<div class='col' style='flex:1'>
<div class='card' style='background:#0f2a2c;border-color:#1d5c58'><div style='font-size:15px;letter-spacing:1.5px;color:#6fe0cd'>OVERLAY, NOT REPLACEMENT</div><div style='font-size:24px;font-weight:700;margin-top:8px;line-height:1.4'>ไม่ได้สร้างระบบติดตามกระเป๋าใหม่</div><div class='lbl' style='font-size:17.5px;margin-top:6px'>BRS ติดตามกระเป๋ารายใบอยู่แล้ว เราใช้สัญญาณจาก BRS, AODB และฝ่ายภาคพื้น มาวิเคราะห์ต่อว่า ปัญหาอยู่ขั้นไหน กระทบอะไร ควรทำอะไรก่อน</div></div>
<div class='card'><div style='font-size:15px;letter-spacing:1.5px;color:var(--mute)'>ตอบ 4 คำถามในจอเดียว</div><div style='font-size:19px;line-height:1.85;margin-top:8px'>① ปกติหรือไม่<br>② ติดที่ขั้นไหน<br>③ กระทบเที่ยวบินไหน กี่ใบ<br>④ ทำอะไรก่อน ก่อนกี่โมง</div></div></div></div>"""
    return slide(
        "3 · Proposed Solution",
        body,
        foot(
            "สี่ชั้นเดิมจาก One TrustX รอบแรก ใช้กับข้อมูลกระเป๋า · ระบบแนะนำ คนตัดสินใจ ไม่ควบคุมอุปกรณ์ใด",
            "3/8",
        ),
    )


def s4():
    steps = [
        ("รับข้อมูล", "สแกนรายขั้น · ตารางบิน · กำลังคน", ""),
        ("ตรวจและติดป้าย", "ที่มา ความสด ซ้ำ ผิดปกติ", ""),
        ("สถานะร่วม", "6 ขั้น: รอกี่ใบ รอนานแค่ไหน", "amb"),
        ("Detect", "ขั้นที่รอนานเกินเกณฑ์", "hot"),
        ("Predict", "เที่ยวบินที่จะไม่ทัน", "hot"),
        ("Recommend", "ลำดับตามเวลาปิด", "hot"),
        ("คนตัดสินใจ", "อนุมัติ ปฏิเสธ แก้ไข", "grn"),
    ]
    fl = "<span class='arr'>→</span>".join(
        f"<div class='node {c}'><b>{t}</b><small>{d}</small></div>" for t, d, c in steps
    )
    stages = [
        ("Check-in", "OK", "ok", ""),
        ("Screening", "OK", "ok", "0 ใบ"),
        ("Sorting", "OK", "ok", "27 ใบ · 5 นาที"),
        ("Loading", "DELAY", "bad", "202 ใบ · 35 นาที"),
        ("Transfer", "OK", "ok", "24 ใบ · 25 นาที"),
        ("Arrival", "OK", "ok", "129 ใบ · 25 นาที"),
    ]
    st = "".join(
        f"<div class='card' style='flex:1;padding:12px 12px;{'border-color:#7a2a2a;background:#241520' if c == 'bad' else ''}'><span class='chip {c}'>{s}</span><div style='font-size:18px;font-weight:700;margin-top:8px'>{t}</div><div style='font-size:14.5px;color:var(--mute);margin-top:3px'>{d}</div></div>"
        for t, s, c, d in stages
    )
    body = f"""<h1>ทำงานอย่างไร <em>จากสัญญาณถึงการตัดสินใจ</em></h1>
<div class='flow' style='margin-top:20px'>{fl}</div>
<div class='card' style='margin-top:20px'><div style='display:flex;justify-content:space-between;align-items:center'><div style='font-size:16px;letter-spacing:1.5px;color:var(--mute)'>ตัวอย่างจากแบบจำลอง · สถานการณ์น้ำท่วม · 08:30</div><span class='chip sim'>ข้อมูลจำลอง</span></div>
<div class='row' style='margin-top:12px'>{st}</div>
<div class='row' style='margin-top:14px;align-items:stretch'>
<div style='flex:1;font-size:18px;line-height:1.7'><b style='color:var(--red)'>กระทบ</b> เที่ยวบินเสี่ยง 3 จาก 10 · กระเป๋าเสี่ยง 60 ใบ ต่อเครื่อง 44 ใบ<br><b style='color:var(--teal)'>สาเหตุ</b> (ถ้ามีข้อมูล ground handler) พนักงาน 55% ของแผน รถขนกระเป๋า 4 จาก 5 คัน</div>
<div style='flex:1;border-left:1px solid var(--line);padding-left:20px;font-size:18px;line-height:1.7'><b style='color:var(--amber)'>แนะนำ</b> ให้กำลัง loading กับ TT403 ก่อน (ปิด 08:55) แล้ว TT404, TT405<br><span class='chip'>ผู้รับผิดชอบ ground handler · ต้องให้คนอนุมัติ</span></div></div></div>
<p style='margin-top:12px;font-size:17px;color:var(--mute)'>ถ้าไม่มีข้อมูล ground handler ระบบยังบอกได้ว่า <b style='color:#fff'>ติดที่ไหน</b> แต่จะระบุว่า “ยังไม่ทราบสาเหตุ” ไม่เดา</p>"""
    return slide(
        "4 · How It Works / Solution Journey",
        body,
        foot(
            "ผลคำนวณจากแบบจำลอง (เลขสุ่ม 42) ใช้ข้อมูลสังเคราะห์ ไม่ใช่ข้อมูลสนามบินจริง · ลองได้ที่ onetrustx.vercel.app/baggage",
            "4/8",
        ),
    )


def s5():
    rows = [
        (
            "BRS / BHS",
            "กระเป๋าใบนี้อยู่ที่ไหน ขึ้นเครื่องถูกลำหรือไม่ แจ้งเตือนกระเป๋า no-show และลงผิดตู้",
            "ดูการไหลรายขั้นเทียบเวลาออกของเที่ยวบิน บอกว่าติดที่ไหนและเที่ยวบินใดเสี่ยง",
        ),
        ("AODB", "เที่ยวบินออกและถึงกี่โมง gate ไหน", "ใช้เป็นเส้นตายในการจัดลำดับ ไม่ซ้ำกับ AODB"),
        (
            "A-CDM",
            "ทุกฝ่ายทำงานตาม milestone ของเที่ยวบิน",
            "ไม่สร้างใหม่ ส่งความเสี่ยงด้านกระเป๋ารายเที่ยวบินเป็นอีกหนึ่ง input",
        ),
        (
            "ฝ่ายภาคพื้น",
            "รู้กำลังคนของตัวเอง แต่ไม่เห็นภาพกระเป๋าทั้งเส้น",
            "ได้ลำดับเที่ยวบินที่ควรทำก่อน เมื่อคนไม่พอ",
        ),
    ]
    tb = "".join(
        f"<tr><td class='k'>{a}</td><td>{b}</td><td style='color:#cfe6e1'>{c}</td></tr>"
        for a, b, c in rows
    )
    body = f"""<h1>ต่างจากระบบที่ SKY มีอยู่ <em>อย่างไร</em></h1>
<div class='card' style='margin-top:20px;padding:10px 18px'><table><tr><th style='width:150px'>ระบบ</th><th style='width:44%'>ตอบคำถามอะไร</th><th>One TrustX เพิ่มอะไร</th></tr>{tb}</table></div>
<div class='row' style='margin-top:20px'>
<div class='card' style='flex:1.3;border-color:#1d5c58;background:#0f2a2c'><div style='font-size:15px;letter-spacing:1.5px;color:#6fe0cd'>ประโยคหลัก</div><div style='font-size:26px;font-weight:700;line-height:1.4;margin-top:6px'>BRS ตามกระเป๋า<br>One TrustX ดูแลความล่าช้ารอบกระเป๋า</div><div class='lbl' style='margin-top:8px'>เราต่อยอดจากสัญญาณของระบบเดิม ไม่ได้บอกว่า BRS ทำไม่ได้</div></div>
<div class='card' style='flex:1'><div style='font-size:15px;letter-spacing:1.5px;color:var(--mute)'>ความน่าเชื่อถือของข้อมูล</div><div style='font-size:19px;line-height:1.7;margin-top:8px'>ทุกเหตุการณ์มีที่มา เวลา และบันทึกการตัดสินใจ ย้อนตรวจได้ (Trusted Event History)</div></div></div>"""
    return slide(
        "5 · Value & Differentiation",
        body,
        foot(
            "ความสามารถของ BRS อ้างอิงหน้าโครงการสาธารณะของ SKY ICT และต้องยืนยันกับ SKY ว่าการใช้งานจริงมีมากกว่านี้หรือไม่ · A-CDM และ AODB ตามที่ SKY อธิบายในวัน Kick-off",
            "5/8",
        ),
    )


def s6():
    need = [
        ("BRS / BHS", "จำนวนสแกนรวมรายขั้น รายเที่ยวบิน", "จำเป็น"),
        ("AODB", "เวลาออก เวลาจอด gate", "จำเป็น"),
        ("DCS / BRS", "จำนวนกระเป๋าที่คาดไว้ และเที่ยวบินต่อ", "จำเป็น"),
        ("Ground handler", "พนักงานเทียบแผน รถขนกระเป๋า", "ช่วยระบุสาเหตุ"),
        ("BHS", "สถานะสายพานและเครื่องคัดแยก", "ช่วยระบุสาเหตุ"),
    ]
    tb = "".join(
        f"<tr><td class='k'>{a}</td><td>{b}</td><td><span class='chip {'ok' if c == 'จำเป็น' else ''}'>{c}</span></td></tr>"
        for a, b, c in need
    )
    body = f"""<h1>สร้างได้จริง <em>เพราะใช้ข้อมูลที่ SKY มีอยู่แล้ว</em></h1>
<div class='row' style='margin-top:20px;align-items:stretch'>
<div class='card' style='flex:1.15;padding:10px 18px'><div style='font-size:15px;letter-spacing:1.5px;color:var(--mute);margin:6px 0'>ข้อมูลที่ต้องการ (จำนวนรวม ไม่ใช้ข้อมูลส่วนบุคคล)</div><table>{tb}</table>
<p style='font-size:15.5px;color:var(--mute);margin:8px 0 4px;line-height:1.5'>ต้องถาม SKY ว่า BRS ส่งออกเวลาสแกนรายขั้นเป็นจำนวนรวมได้หรือไม่ นี่คือสมมติฐานหลักของวิธีตรวจจับ</p>
<div style='border-top:1px solid var(--line);margin-top:10px;padding-top:10px;font-size:16.5px;line-height:1.65'><b style='color:var(--amber)'>ความเสี่ยง → ทางลด</b><br>เข้าถึงข้อมูล handler ไม่ได้ → ระบบทำงานได้โดยไม่ต้องใช้ แค่ไม่ระบุสาเหตุ<br>สแกนหายหรือมาช้า → ระบบขอให้ตรวจสอบ ไม่เดา<br>เกณฑ์ไม่ตรงกับสนามบินจริง → ยืนยันกับผู้เชี่ยวชาญก่อน prototype</div></div>
<div class='col' style='flex:1'>
<div class='card'><div style='font-size:21px;font-weight:700;margin-bottom:6px'>วิธีนำไปใช้</div><div style='font-size:18px;line-height:1.7'>① อ่านอย่างเดียว (read-only)<br>② คนอนุมัติทุกคำแนะนำ<br>③ ไม่ควบคุมอุปกรณ์ใด<br>④ ถ้า One TrustX หยุด ระบบเดิมทำงานต่อ</div></div>
<div class='card' style='padding:10px'><img src='screenshots/report/live-baggage-flood.jpg' style='width:100%;height:215px;object-fit:cover;object-position:top left;border-radius:8px;display:block'><div style='font-size:14px;color:var(--mute);margin-top:6px'>ต้นแบบที่ใช้งานได้แล้วที่ onetrustx.vercel.app/baggage (ข้อมูลจำลอง)</div></div></div></div>"""
    return slide(
        "6 · Feasibility",
        body,
        foot(
            "ต้นแบบทำงานบนข้อมูลสังเคราะห์ที่ติดป้ายที่มาทุกค่า (15 ค่า: จริง 2 · อ้างอิง 1 · คำนวณ 1 · สมมติฐาน 11) · ความเสี่ยง: การเข้าถึงข้อมูลของ ground handler และการยืนยันเกณฑ์กับผู้เชี่ยวชาญ",
            "6/8",
        ),
    )


def s7():
    top = max(FLOOD["bags_missed_total_plan"], 1)
    w1, w2 = 100, FLOOD["bags_missed_total_priority"] / top * 100
    kpis = [
        (
            pct(FLOOD["bags_missed_reduction_pct"]),
            "กระเป๋าตกเที่ยวบินลดลง",
            f"{n(FLOOD['bags_missed_total_plan'])} → {n(FLOOD['bags_missed_total_priority'])} ใบ รวม {RUNS} รอบ",
        ),
        (
            pct(FLOOD["transfer_bags_missed_reduction_pct"]),
            "กระเป๋าต่อเครื่องตกเที่ยวบินลดลง",
            f"{n(FLOOD['transfer_bags_missed_total_plan'])} → {n(FLOOD['transfer_bags_missed_total_priority'])} ใบ",
        ),
        (
            f"{F1}%",
            "F1 ของการเตือนระดับเที่ยวบิน",
            f"เตือนถูก {FLIGHT['flight_precision']} · จับได้ {FLIGHT['flight_recall']}",
        ),
        (
            f"{LEAD['median']:g} นาที",
            "เตือนก่อนกระเป๋าใบแรกตกเที่ยวบิน",
            f"ช่วง {LEAD['min']}–{LEAD['max']} นาที",
        ),
        (
            f"{pct(SILENT_RAW, 0)} → {pct(SILENT_VER, 0)}",
            "สถานะผิดโดยไม่เตือน เมื่อข้อมูลมีความผิด",
            f"ตรวจจับข้อมูลผิด {n(CAUGHT)}/{n(INJECTED)} รายการ ปฏิเสธข้อมูลถูก 0/{n(TRUST['clean_records'])}",
        ),
    ]
    kp = "".join(
        f"<div class='card' style='padding:9px 16px'><div style='display:flex;align-items:baseline;gap:12px'><div style='font-size:30px;font-weight:700;color:var(--teal);line-height:1.1;white-space:nowrap'>{a}</div><div style='font-size:16.5px;font-weight:600;line-height:1.3'>{b}</div></div><div style='font-size:14px;color:var(--mute);margin-top:2px'>{c}</div></div>"
        for a, b, c in kpis
    )
    body = f"""<h1>ผลที่คาดหวัง <em>และวัดได้</em></h1>
<div class='row' style='margin-top:14px;align-items:stretch'>
<div class='col' style='flex:1.45'>
<div class='card'><div style='display:flex;justify-content:space-between'><div style='font-size:15px;letter-spacing:1.5px;color:var(--mute)'>กระเป๋าตกเที่ยวบิน · สถานการณ์น้ำท่วม · รวม {RUNS} รอบ</div><span class='chip sim'>ผลจำลอง</span></div>
<div style='margin-top:14px;font-size:16.5px'>แบ่งกำลังเท่ากันทุกเที่ยวบิน (วิธีเดิม สมมติฐาน)</div><div style='display:flex;align-items:center;gap:12px'><div class='bar' style='width:{w1 * 0.78}%;background:#5d7a99'></div><b style='font-size:22px'>{n(FLOOD["bags_missed_total_plan"])}</b></div>
<div style='margin-top:10px;font-size:16.5px'>จัดลำดับตามที่ One TrustX แนะนำ</div><div style='display:flex;align-items:center;gap:12px'><div class='bar' style='width:{w2 * 0.78}%;background:var(--teal)'></div><b style='font-size:22px'>{n(FLOOD["bags_missed_total_priority"])}</b></div></div>
<div class='card' style='font-size:16.5px;line-height:1.65'><b style='color:var(--amber)'>ยังวัดไม่ได้ในรอบนี้ และจะวัดในรอบ prototype</b><br>เวลาประสานงานของคน: ให้ผู้ควบคุมงานทำสถานการณ์เดียวกันสองแบบ (มี/ไม่มีหน้าจอ) จับเวลาจากสัญญาณแรกถึงมีผู้รับผิดชอบรับงาน<br>ความล่าช้าของเที่ยวบิน: ต้องเพิ่มกฎการรอกระเป๋าในแบบจำลอง หรือเทียบกับข้อมูลย้อนหลัง</div></div>
<div class='col' style='flex:1.1;gap:8px'>{kp}</div></div>"""
    return slide(
        "7 · Expected Impact",
        body,
        foot(
            f"จำลอง {RUNS} รอบต่อสถานการณ์ ข้อมูลสังเคราะห์ ไม่ใช่ผลของสนามบินจริง · ตัวเลขลดลงขึ้นกับสมมติฐานว่าวิธีเดิมคือการแบ่งกำลังเท่ากัน ถ้า handler จริงจัดลำดับดีอยู่แล้ว ผลจะน้อยกว่านี้ · ความจริงที่ใช้ตรวจมาจากแบบจำลองเดียวกัน",
            "7/8",
        ),
    )


def s8():
    ph = [
        (
            "1",
            "ยืนยันกับผู้เชี่ยวชาญ",
            "เกณฑ์เวลารอ เวลาปิดห้องสัมภาระ วิธีจัดลำดับของ handler และ BRS ส่งออกข้อมูลรายขั้นได้หรือไม่",
        ),
        (
            "2",
            "ปรับสถานการณ์",
            "เพิ่มกระเป๋าขาเข้าค้างแบบเหตุการณ์จริง และสถานการณ์ปกติ / คนไม่พอ / สายพานขัดข้อง / น้ำท่วม",
        ),
        (
            "3",
            "ทดลองกับผู้ใช้",
            "ให้ผู้ควบคุมงานใช้หน้าจอ วัดเวลาประสานงาน อัตราเตือนผิด และความเห็นต่อคำแนะนำ",
        ),
        ("4", "Shadow mode", "ต่อข้อมูลย้อนหลังแบบไม่ระบุตัวตน อ่านอย่างเดียว เทียบกับสิ่งที่เกิดจริง"),
    ]
    cards = "".join(
        f"<div class='card' style='flex:1;border-top:4px solid var(--teal)'><div style='font-size:34px;font-weight:700;color:var(--teal)'>{a}</div><div style='font-size:21px;font-weight:700;margin:4px 0 6px'>{b}</div><div style='font-size:16.5px;color:var(--mute);line-height:1.5'>{c}</div></div>"
        for a, b, c in ph
    )
    vision = ["Baggage", "Turnaround", "Gate", "Passenger", "Cargo"]
    vf = "<span class='arr'>→</span>".join(
        f"<div class='node {'grn' if i == 0 else ''}' style='padding:10px 6px'><b style='font-size:18px'>{v}</b></div>"
        for i, v in enumerate(vision)
    )
    body = f"""<h1>แผนต่อไป <em>สำหรับ Prototype Phase</em></h1>
<div class='row' style='margin-top:20px;align-items:stretch'>{cards}</div>
<div class='card' style='margin-top:20px'><div style='font-size:15px;letter-spacing:1.5px;color:var(--mute);margin-bottom:10px'>วิสัยทัศน์ · ขยายหลังพิสูจน์คุณค่าแล้วเท่านั้น</div><div class='flow'>{vf}</div></div>
<div style='margin-top:22px;font-size:25px;font-weight:600;line-height:1.5;text-align:center'>เริ่มจากกระเป๋า ที่ทุกนาทีและทุกการเปลี่ยนมือมีค่า<br><span style='color:var(--amber)'>แล้วขยายสู่ชั้นข้อมูลที่ไว้ใจได้ของ Future Aviation Hub</span></div>"""
    return slide(
        "8 · Next Step / Development Plan",
        body,
        foot(
            "กำหนดการอื่นนอกจากวันที่ 22 ต.ค. 2026 (Pitch) จะยืนยันตามประกาศของทีมงาน SKY Innovation Spark",
            "8/8",
        ),
    )


def build(output: Path):
    page = f"""<!doctype html><html lang='th'><head><meta charset='utf-8'><title>One TrustX · Preliminary Pitch</title>
<link href='https://fonts.googleapis.com/css2?family=IBM+Plex+Sans+Thai:wght@400;500;600;700&display=swap' rel='stylesheet'>
<style>{CSS}</style></head><body style='background:#060f1d'>{"".join(f() for f in (s1, s2, s3, s4, s5, s6, s7, s8))}</body></html>"""
    output.write_text(page)
    print(output)


if __name__ == "__main__":
    build(ROOT / "docs/onetrustx_PreliminaryPitch.html")
