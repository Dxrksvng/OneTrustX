"""Render a Thai Markdown report to a styled HTML file with diagrams.

Print it to PDF with ``frontend/scripts/print-pdf.mjs`` (Chromium shapes Thai text correctly;
the ReportLab renderer in ``render_data_pdf.py`` does not).

Diagram placeholders in the Markdown look like ``[[diagram:name]]`` on their own line.
"""

import argparse
import json
import re
from pathlib import Path

import markdown

ROOT = Path(__file__).resolve().parents[1]
EVALUATION = ROOT / "backend/app/baggage_evaluation.json"


def chain(steps, cls=""):
    cells = "<span class='arrow'>→</span>".join(
        f"<div class='node {kind}'><b>{title}</b><small>{note}</small></div>"
        for title, note, kind in steps
    )
    return f"<div class='chain {cls}'>{cells}</div>"


def cause_chain():
    steps = [
        ("ฝนหนัก", "116 มม. ใน 25 ก.ย.", "real"),
        ("ถนนน้ำท่วม", "CAAT ประกาศ 26 ก.ย.", "real"),
        ("พนักงานมาไม่ได้", "รถขนกระเป๋าเสียซ้ำ", "real"),
        ("กำลังจัดการลด", "ไม่มีตัวเลขเผยแพร่", "assume"),
        ("กระเป๋าค้างสะสม", "กว่า 10,000 ใบ", "real"),
        ("เที่ยวบินได้รับผล", "ลดเที่ยวบิน งดรับ cargo", "real"),
    ]
    legend = "<p class='legend'><i class='dot real'></i>มีแหล่งข่าวหรือข้อมูลจริงรองรับ <i class='dot assume'></i>ไม่มีตัวเลขเผยแพร่ ทีมต้องสมมติ</p>"
    return figure(
        chain(steps) + legend,
        "ลำดับเหตุของเหตุการณ์สุวรรณภูมิ ปลาย ก.ย. 2026 ที่ใช้เป็นแม่แบบสถานการณ์",
    )


def positioning():
    body = """
    <div class='pos'>
      <div class='col'>
        <div class='box sky'><b>BRS / BHS</b><small>จำนวนสแกนรายขั้น</small><em>SKY มีอยู่แล้ว</em></div>
        <div class='box sky'><b>AODB</b><small>เวลาออก เวลาจอด gate</small><em>SKY มีอยู่แล้ว</em></div>
        <div class='box opt'><b>Ground handler</b><small>กำลังคน รถขนกระเป๋า</small><em>ส่วนเสริม ใช้บอกสาเหตุ</em></div>
      </div>
      <div class='arrow big'>→</div>
      <div class='core'>
        <span>ONE TRUSTX</span>
        <ol><li>ปกติหรือไม่</li><li>ติดที่ขั้นไหน</li><li>กระทบเที่ยวบินไหน กี่ใบ</li><li>ทำอะไรก่อน ก่อนกี่โมง</li></ol>
      </div>
      <div class='arrow big'>→</div>
      <div class='col'>
        <div class='box user'><b>ผู้ควบคุมงานกระเป๋า</b><small>อนุมัติ ปฏิเสธ หรือแก้คำแนะนำ</small></div>
        <div class='box user'><b>Airline OCC</b><small>ตัดสินใจรอหรือส่งกระเป๋าตาม</small></div>
      </div>
    </div>"""
    return figure(body, "One TrustX อยู่เหนือระบบเดิม อ่านข้อมูลอย่างเดียว และให้คนเป็นผู้ตัดสินใจ")


def results():
    data = json.loads(EVALUATION.read_text())["scenarios"]
    names = {
        "BAG-NORMAL": "ปกติ",
        "BAG-FLOOD-STAFF": "น้ำท่วม คนมาไม่ได้",
        "BAG-BHS-FAULT": "เครื่องคัดแยกขัดข้อง",
        "BAG-LATE-INBOUND": "ขาเข้าช้า",
        "BAG-STALE-FEED": "ข้อมูลสแกนขาด",
    }
    top = max(r["bags_missed_plan_policy"]["median"] for r in data.values()) or 1
    rows = ""
    for key, label in names.items():
        plan, prio = (
            data[key]["bags_missed_plan_policy"]["median"],
            data[key]["bags_missed_priority_policy"]["median"],
        )
        rows += f"""<div class='bar-row'><span class='bar-label'>{label}</span><div class='bars'>
          <div class='bar plan' style='width:{max(plan / top * 100, 0.6):.1f}%'></div><b>{plan:g}</b>
          <div class='bar prio' style='width:{max(prio / top * 100, 0.6):.1f}%'></div><b>{prio:g}</b></div></div>"""
    legend = "<p class='legend'><i class='dot plan'></i>แบ่งกำลังเท่ากันทุกเที่ยวบิน (สมมติฐาน) <i class='dot prio'></i>จัดลำดับตามคำแนะนำ</p>"
    return figure(
        f"<div class='barchart'>{rows}</div>{legend}",
        "กระเป๋าที่ตกเที่ยวบิน ค่ากลางจากการจำลอง 30 รอบต่อสถานการณ์ (ผลจำลอง ไม่ใช่ผลสนามบินจริง)",
    )


def before_after():
    pairs = [
        ("จุดขาย", "แพลตฟอร์มคิวผู้โดยสาร และความจริงร่วมของหลายฝ่าย", "กระเป๋าค้างสะสมช่วงเหตุผิดปกติ เรื่องเดียว"),
        ("หน้ากระเป๋า", "ไม่มี มีแต่สถานะเที่ยวบิน TT401 เที่ยวเดียว", "6 ขั้น 5 สถานการณ์ คำนวณจากการสแกน"),
        ("สถานะปกติ", "แสดงไม่ได้", "แสดงได้ และไม่เตือนผิดใน 30 รอบ"),
        ("ข้อมูลกระเป๋า", "4 แถว เวลาเดียว", "ราว 8,000 รายการสแกน"),
        ("ที่มาของค่า", "อธิบายในเอกสาร ไม่ผูกกับโค้ด", "ทุกค่ามีประเภทและลิงก์ มีเทสต์บังคับ"),
        ("ตัวเลขผล", "61% / 78% / 74% / 50% จากอัตราส่วนที่ตั้งไว้", "ผลจากแบบจำลองการไหล มีต่ำสุดและสูงสุด"),
        ("ตำแหน่งในระบบ", "ไฟล์ที่ไม่ได้ต่อเข้าเมนู", "เมนู Baggage ในแถบนำทางหลัก"),
    ]
    rows = "".join(
        f"<div class='ba-row'><span>{k}</span><div class='old'>{a}</div><div class='new'>{b}</div></div>"
        for k, a, b in pairs
    )
    head = "<div class='ba-row head'><span></span><div>บน GitHub · 28 ก.ย. 2026</div><div>ปัจจุบัน · 8 ต.ค. 2026</div></div>"
    return figure(f"<div class='ba'>{head}{rows}</div>", "สิ่งที่เปลี่ยนจากเวอร์ชันบน GitHub")


def data_layers():
    body = """
    <div class='layers'>
      <div class='layer l1'><b>ชั้นที่ 1 · ข้อมูลจริงสาธารณะ</b><span>ฝนรายชั่วโมงที่ BKK · เวลาปิดรับกระเป๋าของสายการบิน · จุดสแกนตาม IATA 753 · สถิติผู้โดยสารและเที่ยวบิน</span></div>
      <div class='layer l2'><b>ชั้นที่ 2 · รูปแบบจากเหตุการณ์จริงและค่าอ้างอิง</b><span>ลำดับเหตุของเหตุการณ์ ก.ย. 2026 · SITA: 39% ของกรณีผิดพลาดเกิดที่ transfer</span></div>
      <div class='layer l3'><b>ชั้นที่ 3 · สมมติฐานของทีม (ประกาศชัด)</b><span>กำลังคนเหลือ 55% · กระเป๋า 0.9 ใบต่อคน · เกณฑ์เวลารอ · เวลาปิดห้องเก็บสัมภาระ</span></div>
      <div class='down'>↓ รวมไว้ใน baggage_calibration.json พร้อมประเภทและลิงก์ ↓</div>
      <div class='layer l4'><b>ข้อมูลปฏิบัติการจำลอง</b><span>เที่ยวบิน กระเป๋า และการสแกน สร้างจากค่าข้างบนด้วยเลขสุ่มที่ทำซ้ำได้</span></div>
    </div>"""
    return figure(
        body, "ข้อมูลสามชั้น: ของจริงกำหนดโครง สมมติฐานถูกประกาศ ข้อมูลปฏิบัติการเป็นของจำลองทั้งหมด"
    )


def process():
    lane = (
        lambda title,
        steps,
        cls: f"<div class='lane {cls}'><span class='lane-title'>{title}</span>{chain([(s, n, k) for s, n, k in steps], 'tight')}</div>"
    )
    body = (
        lane(
            "ขาออก",
            [
                ("Check-in", "รับกระเป๋า", "scan"),
                ("Screening", "อัตโนมัติ", ""),
                ("Sorting", "อัตโนมัติ", ""),
                ("Loading", "ใช้คน", "manual"),
                ("ออกเดินทาง", "ปิดห้องสัมภาระ −20 นาที", "end"),
            ],
            "",
        )
        + lane(
            "ต่อเครื่อง",
            [
                ("เครื่องจอด", "ขาเข้า", "end"),
                ("Transfer", "ใช้คน", "manual"),
                ("Sorting", "รวมกับขาออก", ""),
                ("Loading", "ใช้คน", "manual"),
                ("ออกเดินทาง", "เที่ยวบินต่อ", "end"),
            ],
            "",
        )
        + lane(
            "ขาเข้า",
            [
                ("เครื่องจอด", "ขาเข้า", "end"),
                ("Arrival", "ใช้คน", "manual"),
                ("สายพานรับกระเป๋า", "คืนผู้โดยสาร", "scan"),
            ],
            "",
        )
        + "<p class='legend'><i class='dot manual'></i>ขั้นที่ใช้คน กำลังลดเมื่อพนักงานมาไม่ได้ <i class='dot scan'></i>จุดสแกนตาม IATA 753 ทุกลูกศรคือจุดเปลี่ยนมือ</p>"
    )
    return figure(f"<div class='lanes'>{body}</div>", "เส้นทางกระเป๋าสามแบบในแบบจำลอง")


def architecture():
    body = """
    <div class='arch'>
      <div class='arch-row two'>
        <div class='box today'><b>วันนี้ · ข้อมูลจำลอง</b><small>baggage_flow.simulate()</small></div>
        <div class='box future'><b>อนาคต · ระบบจริง</b><small>BRS/BHS · AODB · Ground handler (อ่านอย่างเดียว)</small></div>
      </div>
      <div class='down'>↓ รายการสแกนรวม + ตารางบิน ↓</div>
      <div class='box core2'><b>baggage_flow.assess()</b><small>สถานะรายขั้น · คอขวด · เที่ยวบินเสี่ยง · คำแนะนำ</small></div>
      <div class='down'>↓</div>
      <div class='arch-row two'>
        <div class='box'><b>FastAPI</b><small>/api/trustx/baggage/*</small></div>
        <div class='box'><b>React</b><small>หน้า /baggage</small></div>
      </div>
      <div class='down'>↓</div>
      <div class='box user'><b>ผู้ควบคุมงานอนุมัติ</b><small>ระบบไม่สั่งการอุปกรณ์ใด</small></div>
    </div>"""
    return figure(
        body, "สถาปัตยกรรม: ตัวประเมินรับข้อมูลรูปแบบเดียวกันไม่ว่าจากแบบจำลองหรือระบบจริง"
    )


def platform():
    mods = [("Overview", "คิวตอนนี้และล่วงหน้า", ""), ("Baggage", "เรื่องหลักของรอบนี้", "hero"), ("Future Flow", "แผนที่แรงกดดัน", ""),
            ("Operations", "จัดลำดับสถานการณ์", ""), ("Simulator", "เทียบมาตรการ", ""), ("Flights", "เที่ยวบิน", ""),
            ("Performance", "ผลประเมิน", ""), ("Journey", "มุมผู้โดยสาร", "")]
    cells = "".join(f"<div class='mod {k}'><b>{n}</b><small>{d}</small></div>" for n, d, k in mods)
    base = "<div class='base'>ฐานร่วม: ข้อมูลติดป้ายที่มา · ระบบแนะนำ คนตัดสินใจ · บันทึกการตัดสินใจ · แจ้งเมื่อข้อมูลไม่สด</div>"
    return figure(f"<div class='platform'><span class='plat-title'>ONE TRUSTX · ระบบกลาง</span><div class='mods'>{cells}</div>{base}</div>",
                  "One TrustX เป็นระบบกลางหลายโมดูล รอบนี้เน้นโมดูล Baggage")


def loop():
    steps = [("รับข้อมูล", "จากระบบเดิม หรือข้อมูลจำลอง", ""), ("ตรวจและติดป้าย", "ที่มา ความสด ประเภท", ""), ("คำนวณ", "พยากรณ์ หาคอขวด", ""),
             ("เปรียบเทียบ", "ทางเลือกและผลกระทบ", ""), ("แนะนำ", "พร้อมเหตุผล", ""), ("คนตัดสินใจ", "อนุมัติ ปฏิเสธ แก้ไข", "scan"), ("บันทึกและวัดผล", "ย้อนตรวจได้", "")]
    return figure(chain(steps), "ลำดับการทำงานที่ทุกโมดูลใช้ร่วมกัน")


def original_frame():
    layers = [
        ("1 · Data Integration Layer", "สแกนรายขั้น + ตารางบิน + กระเป๋าที่คาดไว้ + กำลังคน → รูปแบบเดียว", "l2"),
        ("2 · Trusted Shared Event Ledger", "ป้ายที่มา เวลาเกิดเหตุและเวลาที่ได้รับ ตรวจความสด ไม่ตัดสินจากข้อมูลที่ขาด", "l1"),
        ("3 · Common Operation State", "สถานะเดียวของ 6 ขั้น: กระเป๋าที่รอ เวลารอ สถานะรวม", "l4"),
        ("4 · AI Decision Intelligence", "Detect คอขวด · Predict เที่ยวบินเสี่ยง · Recommend ลำดับ · Coordinate ผู้รับผิดชอบและเส้นตาย", "l3"),
    ]
    who = "".join(f"<div class='box sky'><b>{n}</b><small>{d}</small></div>" for n, d in [
        ("Baggage Operator", "BRS / BHS"), ("Airport", "AODB"), ("Airline", "DCS · เที่ยวบินต่อ"), ("Ground Handler", "คน · รถขนกระเป๋า")])
    stack = "<div class='down'>↓</div>".join(f"<div class='layer {c}'><b>{n}</b><span>{d}</span></div>" for n, d, c in layers)
    body = f"<div class='pos'><div class='col' style='flex:.55'>{who}</div><div class='arrow big'>→</div><div class='layers' style='flex:1.6'>{stack}</div><div class='arrow big'>→</div><div class='col' style='flex:.55'><div class='box user'><b>คนตัดสินใจ</b><small>อนุมัติ ปฏิเสธ แก้ไข</small></div></div></div>"
    return figure(body, "สี่ชั้นเดิมของ One TrustX จากสไลด์รอบแรก ใช้กับข้อมูลกระเป๋า")


def data_map():
    groups = [("1 · ข้อมูลจริงสาธารณะ", "Open-Meteo · IATA · SITA · CAAT · CBP · BTS · ข่าวเหตุการณ์", "ใช้เป็นบริบทและตัวเทียบ", "l1"),
              ("2 · สมมติฐานของทีม", "กำลังคน อัตราให้บริการ เกณฑ์ ผังอาคาร", "ประกาศไว้ทุกค่า", "l3"),
              ("3 · ข้อมูลปฏิบัติการจำลอง", "สแกนกระเป๋า เที่ยวบิน คิว ผู้โดยสาร", "สร้างจาก 1 และ 2 ทำซ้ำได้", "l2"),
              ("4 · ผลคำนวณ", "พยากรณ์ คอขวด คำแนะนำ เวลาปลอดภัย", "ที่เห็นบนหน้าจอ", "l4")]
    cells = "<span class='arrow'>→</span>".join(
        f"<div class='layer {c}' style='flex:1'><b>{n}</b><span>{d}</span><span style='opacity:.75'>{u}</span></div>" for n, d, u, c in groups)
    return figure(f"<div class='chain'>{cells}</div>", "ข้อมูลสี่กลุ่มของทั้งระบบ: ของจริงและสมมติฐานเป็นตัวตั้ง ข้อมูลปฏิบัติการและผลเป็นของจำลอง")


DIAGRAMS = {
    "data-map": data_map,
    "original-frame": original_frame,
    "loop": loop,"platform": platform, 
    "cause-chain": cause_chain,
    "positioning": positioning,
    "results": results,
    "before-after": before_after,
    "data-layers": data_layers,
    "process": process,
    "architecture": architecture,
}


def figure(body, caption, cls="diagram"):
    return f"<figure class='{cls}'>{body}<figcaption>{caption}</figcaption></figure>"


CSS = """
@page { size: A4; margin: 17mm 15mm 18mm; }
* { box-sizing: border-box; }
:root { --ink:#16242f; --muted:#5b6b78; --line:#d9e2e7; --brand:#0f3d5c; --accent:#b8862f; --ok:#1f6f5c; --bad:#a3423b; --soft:#f3f6f8; }
html { font-family: 'IBM Plex Sans Thai', 'Noto Sans Thai', sans-serif; font-size: 10.2pt; line-height: 1.72; color: var(--ink); -webkit-print-color-adjust: exact; print-color-adjust: exact; }
body { margin: 0; }
code, pre { font-family: 'IBM Plex Mono', monospace; font-size: 8.4pt; }
code { background: var(--soft); padding: 1px 4px; border-radius: 3px; }
pre { background: #10212d; color: #e6eef3; padding: 11px 13px; border-radius: 8px; line-height: 1.55; white-space: pre-wrap; break-inside: avoid; }
pre code { background: none; padding: 0; color: inherit; }
.cover { height: 258mm; display: flex; flex-direction: column; justify-content: space-between; padding: 22mm 14mm; color: #fff; border-radius: 10px;
  background: linear-gradient(150deg, #0b2233 0%, #0f3d5c 55%, #1b6a78 100%); break-after: page; }
.cover small { letter-spacing: 3px; font-size: 8.5pt; opacity: .8; }
.cover h1 { font-size: 40pt; line-height: 1.1; margin: 0 0 6mm; font-weight: 700; letter-spacing: -.5px; }
.cover h2 { font-size: 15pt; font-weight: 400; line-height: 1.5; margin: 0; color: #dbe9ef; border: 0; padding: 0; }
.cover .meta { font-size: 9.5pt; line-height: 1.8; color: #cfe0e8; }
.cover .tag { display: inline-block; border: 1px solid rgba(255,255,255,.45); border-radius: 99px; padding: 2px 12px; font-size: 8.5pt; margin-top: 5mm; }
h2 { font-size: 16pt; color: var(--brand); margin: 9mm 0 3mm; padding-bottom: 2mm; border-bottom: 2px solid var(--brand); line-height: 1.35; break-after: avoid; }
h3 { font-size: 11.6pt; color: var(--brand); margin: 6mm 0 2mm; break-after: avoid; }
p { margin: 0 0 2.6mm; }
ul, ol { margin: 0 0 3mm; padding-left: 6mm; }
li { margin-bottom: .8mm; }
hr { border: 0; margin: 0; break-after: page; }
hr:first-of-type { break-after: auto; margin-bottom: 4mm; }
.lead { background: var(--soft); border-radius: 8px; padding: 4mm 5mm; }
blockquote { margin: 3mm 0; padding: 3mm 5mm; border-left: 4px solid var(--accent); background: #fbf6ea; border-radius: 0 6px 6px 0; font-weight: 500; }
blockquote p { margin: 0; }
a { color: #0d5c8a; text-decoration: none; }
table { width: 100%; border-collapse: collapse; margin: 2mm 0 4.5mm; font-size: 8.8pt; line-height: 1.5; }
th { background: var(--brand); color: #fff; text-align: left; padding: 5px 7px; font-weight: 600; }
td { padding: 5px 7px; border-bottom: 1px solid var(--line); vertical-align: top; }
tr:nth-child(even) td { background: #f8fafb; }
tr { break-inside: avoid; }
figure { margin: 4mm 0 5mm; break-inside: avoid; }
figure img { width: 100%; border: 1px solid var(--line); border-radius: 6px; display: block; }
figcaption { font-size: 8.3pt; color: var(--muted); margin-top: 1.6mm; text-align: center; }
figure.diagram { background: var(--soft); border: 1px solid var(--line); border-radius: 10px; padding: 5mm 4mm 3mm; }
.chain { display: flex; align-items: stretch; gap: 1.2mm; }
.chain .node { flex: 1; background: #fff; border: 1px solid var(--line); border-top: 3px solid var(--brand); border-radius: 6px; padding: 2.2mm 1.6mm; text-align: center; display: flex; flex-direction: column; justify-content: center; }
.node b { font-size: 8.6pt; line-height: 1.3; } .node small { font-size: 7.1pt; color: var(--muted); line-height: 1.3; margin-top: .8mm; }
.node.assume { border-top-color: var(--accent); border-style: dashed; border-top-style: solid; }
.node.manual { border-top-color: var(--bad); } .node.scan { border-top-color: var(--ok); } .node.end { border-top-color: #8796a1; background: #eef2f4; }
.arrow { align-self: center; color: var(--muted); font-size: 11pt; } .arrow.big { font-size: 20pt; color: var(--brand); }
.legend { font-size: 7.8pt; color: var(--muted); margin: 3mm 0 0; text-align: center; }
.dot { display: inline-block; width: 8px; height: 8px; border-radius: 2px; margin: 0 4px 0 10px; background: var(--brand); }
.dot.assume, .dot.prio { background: var(--accent); } .dot.manual { background: var(--bad); } .dot.scan { background: var(--ok); } .dot.plan { background: #8796a1; }
.pos { display: flex; align-items: center; gap: 2.5mm; } .pos .col { flex: 1; display: flex; flex-direction: column; gap: 2mm; }
.box { background: #fff; border: 1px solid var(--line); border-radius: 7px; padding: 2.4mm 3mm; display: flex; flex-direction: column; }
.box b { font-size: 9pt; } .box small { font-size: 7.6pt; color: var(--muted); line-height: 1.35; } .box em { font-size: 7pt; font-style: normal; color: var(--ok); margin-top: .6mm; }
.box.opt { border-style: dashed; } .box.opt em { color: var(--accent); } .box.user { border-left: 4px solid var(--ok); }
.core { flex: 1.15; background: linear-gradient(150deg, #0b2233, #0f3d5c); color: #fff; border-radius: 9px; padding: 4mm; }
.core span { letter-spacing: 2.5px; font-size: 8pt; opacity: .8; } .core ol { margin: 2mm 0 0; padding-left: 5mm; font-size: 9pt; line-height: 1.7; }
.barchart { display: flex; flex-direction: column; gap: 2.4mm; padding: 0 2mm; }
.bar-row { display: flex; align-items: center; gap: 3mm; } .bar-label { width: 36mm; font-size: 8.4pt; text-align: right; }
.bars { flex: 1; display: grid; grid-template-columns: 1fr auto; row-gap: 1mm; column-gap: 2mm; align-items: center; }
.bar { height: 3.6mm; border-radius: 2px; background: #8796a1; justify-self: start; } .bar.prio { background: var(--accent); } .bars b { font-size: 8pt; width: 10mm; }
.ba { display: flex; flex-direction: column; gap: 1.4mm; } .ba-row { display: grid; grid-template-columns: 27mm 1fr 1fr; gap: 2mm; align-items: stretch; font-size: 8.4pt; }
.ba-row span { align-self: center; font-weight: 600; } .ba-row div { border-radius: 6px; padding: 1.8mm 2.6mm; line-height: 1.4; }
.ba-row .old { background: #fbeeed; border: 1px solid #efcfcc; color: #6d2f2a; } .ba-row .new { background: #e7f4ef; border: 1px solid #c3e2d7; color: #184f41; }
.ba-row.head div { font-weight: 600; color: var(--muted); padding: 0 2.6mm; font-size: 7.8pt; }
.layers { display: flex; flex-direction: column; gap: 1.6mm; } .layer { border-radius: 7px; padding: 2.4mm 4mm; display: flex; flex-direction: column; color: #fff; }
.layer b { font-size: 9pt; } .layer span { font-size: 7.9pt; opacity: .92; line-height: 1.45; }
.l1 { background: #1f6f5c; } .l2 { background: #2c6f93; } .l3 { background: #9a6f22; } .l4 { background: #0f3d5c; }
.down { text-align: center; font-size: 8pt; color: var(--muted); margin: .6mm 0; }
.lanes { display: flex; flex-direction: column; gap: 2.6mm; } .lane { display: flex; align-items: center; gap: 2.5mm; }
.lane-title { width: 17mm; font-size: 8.4pt; font-weight: 600; color: var(--brand); } .lane .chain { flex: 1; }
.arch { display: flex; flex-direction: column; gap: .6mm; max-width: 135mm; margin: 0 auto; } .arch-row.two { display: grid; grid-template-columns: 1fr 1fr; gap: 3mm; }
.part { height: 250mm; display: flex; flex-direction: column; justify-content: center; padding: 0 12mm; border-left: 6px solid var(--accent); break-before: page; break-after: page; }
.part span { letter-spacing: 3px; font-size: 8.5pt; color: var(--muted); }
.part h1 { font-size: 30pt; color: var(--brand); margin: 3mm 0 4mm; line-height: 1.25; }
.part p { font-size: 12.5pt; color: var(--muted); max-width: 130mm; line-height: 1.7; }
.part + hr { display: none; }
hr:has(+ .part) { display: none; }
.box.today { border-left: 4px solid var(--accent); } .box.future { border-style: dashed; } .box.core2 { background: #0f3d5c; border: 0; } .box.core2 b { color: #fff; } .box.core2 small { color: #cfe0e8; }
.platform { background: linear-gradient(150deg, #0b2233, #0f3d5c); border-radius: 9px; padding: 4mm; color: #fff; }
.plat-title { letter-spacing: 2.5px; font-size: 8pt; opacity: .8; }
.mods { display: grid; grid-template-columns: repeat(4, 1fr); gap: 2mm; margin: 3mm 0; }
.mod { background: rgba(255,255,255,.09); border: 1px solid rgba(255,255,255,.18); border-radius: 6px; padding: 2.2mm 2.6mm; display: flex; flex-direction: column; }
.mod b { font-size: 9pt; } .mod small { font-size: 7.4pt; opacity: .8; line-height: 1.35; }
.mod.hero { background: #c58a2a; border-color: #e3b25c; } .mod.hero small { opacity: 1; }
.base { font-size: 7.8pt; background: rgba(255,255,255,.06); border-radius: 6px; padding: 2mm 3mm; text-align: center; }
"""


def build(source: Path, output: Path):
    text = source.read_text()
    title = re.search(r"^# (.+)$", text, re.M).group(1)
    subtitle = re.search(r"^## (.+)$", text, re.M).group(1)
    byline = re.search(r"^\*\*(.+)\*\*$", text, re.M).group(1)
    body = text.split("\n", text[: text.index(byline)].count("\n") + 1)[
        -1
    ]  # drop title block; cover replaces it
    html = markdown.markdown(body, extensions=["tables", "fenced_code", "sane_lists"])
    html = re.sub(
        r"<p>\[\[diagram:([a-z-]+)\]\]</p>", lambda m: DIAGRAMS[m.group(1)](), html
    )
    html = re.sub(
        r'<p><img alt="([^"]*)" src="([^"]+)" /></p>',
        lambda m: figure(f'<img src="{m.group(2)}" alt="">', m.group(1), "shot"),
        html,
    )
    html = re.sub(
        r"<p>\[\[part:([^|\]]+)\|([^\]]+)\]\]</p>",
        lambda m: f"<section class='part'><span>ONE TRUSTX</span><h1>{m.group(1)}</h1><p>{m.group(2)}</p></section>",
        html,
    )
    missing = re.findall(r"\[\[diagram:[^\]]+\]\]", html)
    if missing:
        raise SystemExit(f"Unknown diagram placeholder: {missing}")
    cover = f"""<section class='cover'><div><small>SKY INNOVATION SPARK 2026 · PRELIMINARY ROUND</small></div>
      <div><h1>{title}</h1><h2>{subtitle}</h2><span class='tag'>ต้นแบบ · ข้อมูลจำลอง · ไม่ใช่ผลของสนามบินจริง</span></div>
      <div class='meta'>{byline}</div></section>"""
    page = f"""<!doctype html><html lang='th'><head><meta charset='utf-8'><title>{title}</title>
<link rel='preconnect' href='https://fonts.googleapis.com'><link rel='preconnect' href='https://fonts.gstatic.com' crossorigin>
<link href='https://fonts.googleapis.com/css2?family=IBM+Plex+Sans+Thai:wght@400;500;600;700&family=IBM+Plex+Mono:wght@400;500&display=swap' rel='stylesheet'>
<style>{CSS}</style></head><body>{cover}{html}</body></html>"""
    output.write_text(page)
    print(output)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--source", type=Path, default=ROOT / "docs/onetrustx-system-report-th.md"
    )
    parser.add_argument(
        "--output", type=Path, default=ROOT / "docs/onetrustx-system-report-th.html"
    )
    args = parser.parse_args()
    build(args.source, args.output)
