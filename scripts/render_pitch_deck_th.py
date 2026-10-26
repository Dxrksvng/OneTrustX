"""Thai Preliminary Pitch deck in the same SKY Innovation Spark theme as the English deck.

Theme and numbers are shared with render_pitch_deck_en (and through it, the measured evaluation file).
Print with: node frontend/scripts/print-deck.mjs docs/onetrustx_PreliminaryPitch.html docs/onetrustx_PreliminaryPitch.pdf
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import render_pitch_deck_en as en  # noqa: E402

ROOT, n, pct = en.ROOT, en.n, en.pct
FLOOD, FLIGHT, TRUST, RUNS = en.FLOOD, en.FLIGHT, en.TRUST, en.RUNS
F1, LEAD, SILENT_RAW, SILENT_VER = en.F1, en.LEAD, en.SILENT_RAW, en.SILENT_VER
CAUGHT, INJECTED = en.CAUGHT, en.INJECTED

FONT = "'IBM Plex Sans Thai', sans-serif"
CSS = (
    en.CSS.replace("'Inter', sans-serif", FONT).replace(
        "'Montserrat', sans-serif", FONT
    )
    + """
h1 { line-height: 1.3; text-transform: none; font-size: 46px; letter-spacing: 0; }
.card h3, .big, td.k, .quote { letter-spacing: 0; }
.eyebrow, th, .badge { text-transform: none; letter-spacing: .3px; }
.sub { line-height: 1.6; }
.lbl, td { line-height: 1.55; }
.body { justify-content: flex-start; gap: 18px; }
.quote { margin-top: auto; margin-bottom: 6px; }
"""
)


def foot(note, page):
    return en.foot(note, page)


def slide(num, tag, title, sub, body, note):
    return en.slide(num, tag, title, sub, body, note)


def s1():
    chain = [
        ("ฝนหนัก", "116 มม. ใน 25 ก.ย.", ""),
        ("ถนนน้ำท่วม", "CAAT ประกาศ 26 ก.ย.", ""),
        ("พนักงานมาไม่ได้", "รถขนกระเป๋าเสียซ้ำ", "amb"),
        ("กระเป๋าค้างสะสม", "10,000+ ใบใน 4 วัน", "hot"),
        ("เที่ยวบินได้รับผล", "ลดเที่ยวบิน งดรับ cargo", "hot"),
    ]
    flow = "<span class='arr'>→</span>".join(
        f"<div class='node {c}'><b>{t}</b><small>{d}</small></div>" for t, d, c in chain
    )
    stats = [
        ("24 ล้านใบ", "กระเป๋า mishandled ทั่วโลกปี 2025"),
        ("$6.3B", "ต้นทุนต่อปี (เฉลี่ย ~$260 ต่อใบ)"),
        ("39%", "ของกรณีผิดพลาดเกิดตอน transfer"),
    ]
    st = "".join(
        f"<div class='card' style='flex:1'><div class='big'>{a}</div><div class='lbl'>{b}</div><span class='chip src'>SITA 2026</span></div>"
        for a, b in stats
    )
    body = f"""<div class='card'><div class='eyebrow' style='margin-bottom:10px'>เหตุการณ์จริง · สุวรรณภูมิ 25–30 ก.ย. 2026</div><div class='flow'>{flow}</div>
<p style='margin-top:12px;font-size:16.5px;color:var(--mute);line-height:1.55'>วันที่ 29 ก.ย. CEO การบินไทยแจ้งว่าเหลือราว ~5,000 ใบ วันที่ 30 ก.ย. ยังค้างราว ~8,000 ใบ ใช้กำลังทหาร 131 นาย งดรับ cargo 30 ก.ย.–6 ต.ค. และลดเที่ยวบิน</p></div>
<div class='row'>{st}</div><div class='quote'>โจทย์ที่เราเลือกตอบ: <span>ถ้ากระเป๋าล่าช้า ติดที่ไหน เพราะอะไร และควรแก้อะไรก่อน</span></div>"""
    return slide(
        1,
        "ปัญหา / Pain Point",
        "กระเป๋าล่าช้า <em>ไม่ใช่แค่ปัญหาของกระเป๋า</em>",
        "เมื่อเกิดเหตุผิดปกติ สัญญาณของกระเป๋า เที่ยวบิน และกำลังคนอยู่คนละระบบ คนละฝ่าย จึง<b>รู้ช้าว่าติดที่ไหน กระทบอะไร และควรทำอะไรต่อ</b>",
        body,
        "แหล่ง: Open-Meteo (ฝน), CAAT 30/2569, The Nation, The Star (เหตุการณ์), SITA Baggage IT Insights 2026 · mishandled = ล่าช้า เสียหาย หรือส่งผิดปลายทาง ไม่ใช่หายถาวร · ตัวเลขข่าวเปลี่ยนตามวัน",
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
<div class='card red' style='flex:1.15'><span class='chip red'>ผู้ใช้หลัก</span><h3 style='margin:10px 0 6px;font-size:25px'>Baggage / Ground Operations Controller</h3>
<div class='lbl' style='font-size:17px'>ต้องตัดสินใจทุกนาทีว่าจะย้ายคนและอุปกรณ์ไปช่วยเที่ยวบินไหนก่อน แต่ข้อมูลอยู่คนละระบบ ต้องโทรหรือเดินถามซ้ำหลายจุด</div></div>
<div class='card' style='flex:1'><span class='chip'>ผู้ใช้รองและผู้ได้ประโยชน์</span>
<div style='margin-top:10px;font-size:17.5px;line-height:1.75'><b>Airline OCC</b> · ตัดสินใจรอหรือส่งกระเป๋าตาม<br><b>Airport Operations</b> · เห็นภาพข้ามฝ่าย<br><b>Ground handler</b> · ได้ลำดับงานเมื่อคนไม่พอ<br><b>ผู้โดยสาร</b> · กระเป๋าไปทันเที่ยวบิน</div></div></div>
<div class='card'><div class='eyebrow' style='margin-bottom:10px'>เส้นทางกระเป๋า — ทุกลูกศรคือจุดเปลี่ยนมือระหว่างฝ่าย</div><div class='flow'>{fl}</div>
<p style='margin-top:12px;font-size:16.5px;color:var(--mute);line-height:1.55'>SKY ระบุเองว่ากระเป๋ามักมีปัญหาตอนเปลี่ยนความรับผิดชอบ และ SITA พบว่า <b style='color:var(--red)'>39%</b> ของกรณีผิดพลาดเกิดที่ขั้นต่อเครื่อง ซึ่งเกี่ยวข้องหลายฝ่ายและมีเวลาจำกัด</p></div>
<div class='quote'>เมื่อกระเป๋าหยุดไหล <span>ใครรู้ก่อนว่า “ทำไม”?</span></div>"""
    return slide(
        2,
        "ผู้ใช้ / Stakeholder",
        "ใครเจ็บ และ <em>จุดไหนของกระเป๋าที่พัง</em>",
        None,
        body,
        "แหล่ง: Kick-off SKY Innovation Spark 1 ต.ค. 2026 (กระบวนการกระเป๋าและ handoff), SITA Baggage IT Insights 2026",
    )


def s3():
    layers = [
        ("Data Integration", "รับสแกนกระเป๋า ตารางบิน กำลังคน แปลงเป็นเหตุการณ์รูปแบบเดียว"),
        ("Trusted Event History", "ทุกรายการมีที่มา เวลา และตรวจความสด ย้อนตรวจได้"),
        ("Common Operational State", "สถานะเดียวของกระเป๋า 6 ขั้น ที่ทุกฝ่ายเห็นตรงกัน"),
        (
            "AI Decision Intelligence",
            "Detect คอขวด · Predict เที่ยวบินเสี่ยง · Recommend ลำดับ · Coordinate ผู้รับผิดชอบ",
        ),
    ]
    cards = "".join(
        f"<div class='card red' style='padding:12px 22px'><h3 style='font-size:19px'>{t}</h3><div class='lbl' style='font-size:15.5px;margin-top:2px'>{d}</div></div>"
        for t, d in layers
    )
    body = f"""<div class='row' style='align-items:stretch;flex:1'>
<div class='col' style='flex:1.25'>{cards}</div>
<div class='col' style='flex:1'>
<div class='card green'><div class='eyebrow' style='color:var(--green)'>Overlay, not replacement</div><h3 style='margin:8px 0 6px;font-size:23px'>ไม่ได้สร้างระบบติดตามกระเป๋าใหม่</h3><div class='lbl' style='font-size:16.5px;color:#2b3f66'>BRS ติดตามกระเป๋าอยู่แล้ว เราใช้สัญญาณจาก BRS, AODB และฝ่ายภาคพื้น มาวิเคราะห์ต่อว่าติดที่ไหน กระทบอะไร ควรทำอะไรก่อน</div></div>
<div class='card'><div class='eyebrow'>ตอบ 4 คำถามในจอเดียว</div><div style='font-size:18px;line-height:1.85;margin-top:8px;font-weight:600'>① ปกติหรือไม่<br>② ติดที่ขั้นไหน<br>③ กระทบเที่ยวบินไหน กี่ใบ<br>④ ทำอะไรก่อน ก่อนกี่โมง</div></div></div></div>"""
    return slide(
        3,
        "แนวทางที่เสนอ / Solution",
        "One TrustX: <em>Baggage Disruption Intelligence</em>",
        "รวมสัญญาณกระเป๋า เที่ยวบิน กำลังคน และเหตุผิดปกติ เพื่อ<b>ตรวจจับคอขวดให้เร็ว ประเมินผลกระทบ และแนะนำลำดับการกู้สถานการณ์</b> โดยเจ้าหน้าที่เป็นผู้ตัดสินใจ",
        body,
        "สี่ชั้นเดิมของ One TrustX จากรอบแรก ใช้กับข้อมูลกระเป๋า · ระบบแนะนำ คนตัดสินใจ ไม่ควบคุมอุปกรณ์ใดของสนามบิน",
    )


def s4():
    steps = [
        ("รับข้อมูล", "สแกน · ตารางบิน · กำลังคน", ""),
        ("ตรวจและติดป้าย", "ที่มา ความสด ข้อมูลซ้ำ", ""),
        ("สถานะร่วม", "6 ขั้น: รอกี่ใบ รอนานแค่ไหน", "amb"),
        ("Detect", "ขั้นที่รอเกินเกณฑ์", "hot"),
        ("Predict", "เที่ยวบินที่จะไม่ทัน", "hot"),
        ("Recommend", "ลำดับตามเวลาปิด", "hot"),
        ("คนตัดสินใจ", "อนุมัติ ปฏิเสธ แก้ไข", "grn"),
    ]
    fl = "<span class='arr'>→</span>".join(
        f"<div class='node {c}'><b>{t}</b><small>{d}</small></div>" for t, d, c in steps
    )
    stg = [
        ("Check-in", "OK", "ok", "จุดรับเข้า"),
        ("Screening", "OK", "ok", "0 ใบ"),
        ("Sorting", "OK", "ok", "27 ใบ · 5 นาที"),
        ("Loading", "DELAY", "red", "202 ใบ · 35 นาที"),
        ("Transfer", "OK", "ok", "24 ใบ · 25 นาที"),
        ("Arrival", "OK", "ok", "129 ใบ · 25 นาที"),
    ]
    st = "".join(
        f"<div style='flex:1;border-radius:12px;padding:10px 12px;{'background:var(--redsoft);border:1px solid #f3b4ba' if c == 'red' else 'background:#f3f6fb;border:1px solid var(--line)'}'><span class='chip {c}'>{s}</span><div style='font-weight:800;font-size:17px;margin-top:6px'>{t}</div><div style='font-size:13.5px;color:var(--mute)'>{d}</div></div>"
        for t, s, c, d in stg
    )
    body = f"""<div class='card dark' style='padding:4px 0'><div class='flow'>{fl}</div></div>
<div class='card'><div style='display:flex;justify-content:space-between;align-items:center'><div class='eyebrow'>ตัวอย่างจากแบบจำลอง · สถานการณ์น้ำท่วม · 08:30</div><span class='chip sim'>ข้อมูลจำลอง</span></div>
<div class='row' style='margin-top:10px;gap:10px'>{st}</div>
<div class='row' style='margin-top:12px'>
<div style='flex:1;font-size:16.5px;line-height:1.7'><b style='color:var(--red)'>กระทบ</b> เที่ยวบินเสี่ยง 3 จาก 10 · กระเป๋าเสี่ยง 60 ใบ ต่อเครื่อง 44 ใบ<br><b style='color:var(--green)'>สาเหตุ</b> (ถ้ามีข้อมูล ground handler) พนักงาน 55% ของแผน รถขนกระเป๋า 4 จาก 5 คัน</div>
<div style='flex:1;border-left:2px solid var(--line);padding-left:18px;font-size:16.5px;line-height:1.7'><b style='color:var(--red)'>แนะนำ</b> ให้กำลัง loading กับ TT403 ก่อน (ปิด 08:55) แล้ว TT404, TT405<br><span class='chip red'>ผู้รับผิดชอบ: GROUND HANDLER · ต้องให้คนอนุมัติ</span></div></div></div>
<div class='sub' style='font-size:16.5px'>ถ้าไม่มีข้อมูล ground handler ระบบยังบอกได้ว่า<b>ติดที่ไหน</b> แต่จะแจ้งว่า “ยังไม่ทราบสาเหตุ” ไม่เดา</div>"""
    return slide(
        4,
        "ทำงานอย่างไร / Solution Journey",
        "จากสัญญาณถึง <em>การตัดสินใจ</em>",
        None,
        body,
        "ผลคำนวณจากแบบจำลอง (เลขสุ่ม 42) ใช้ข้อมูลสังเคราะห์ ไม่ใช่ข้อมูลสนามบินจริง · ลองได้ที่ onetrustx.vercel.app/baggage",
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
        f"<tr><td class='k'>{a}</td><td>{b}</td><td>{c}</td></tr>" for a, b, c in rows
    )
    body = f"""<div class='card' style='padding:8px 20px'><table><tr><th style='width:150px'>ระบบ</th><th style='width:44%'>ตอบคำถามอะไร</th><th>One TrustX เพิ่มอะไร</th></tr>{tb}</table></div>
<div class='row' style='align-items:stretch'>
<div class='card green' style='flex:1.3'><div class='eyebrow' style='color:var(--green)'>ประโยคที่ต้องจำ</div><div style='font-weight:800;font-size:25px;line-height:1.45;margin-top:6px'>BRS ตามกระเป๋า<br>One TrustX ดูแลความล่าช้ารอบกระเป๋า</div><div class='lbl' style='margin-top:6px'>เราต่อยอดจากสัญญาณของระบบเดิม ไม่ได้บอกว่า BRS ทำไม่ได้</div></div>
<div class='card' style='flex:1'><div class='eyebrow'>ความน่าเชื่อถือของข้อมูล</div><div style='font-size:18px;line-height:1.6;margin-top:8px'>ทุกเหตุการณ์มีที่มา เวลา และบันทึกการตัดสินใจ ย้อนตรวจได้ตลอดเส้นทาง</div></div></div>"""
    return slide(
        5,
        "คุณค่าและความแตกต่าง / Value",
        "ต่างจากระบบที่ SKY มีอยู่ <em>อย่างไร</em>",
        None,
        body,
        "ความสามารถของ BRS อ้างอิงหน้าโครงการสาธารณะของ SKY ICT การใช้งานจริงอาจมีมากกว่านี้ ต้องยืนยันกับ SKY · A-CDM และ AODB ตามที่ SKY อธิบายในวัน Kick-off",
    )


def s6():
    need = [
        ("BRS / BHS", "จำนวนสแกนรวมรายขั้น รายเที่ยวบิน", "จำเป็น"),
        ("AODB", "เวลาออก เวลาจอด gate", "จำเป็น"),
        ("DCS / BRS", "จำนวนกระเป๋าที่คาดไว้ และเที่ยวบินต่อ", "จำเป็น"),
        ("Ground handler", "พนักงานเทียบแผน รถขนกระเป๋า", "สาเหตุ"),
        ("BHS", "สถานะสายพานและเครื่องคัดแยก", "สาเหตุ"),
    ]
    tb = "".join(
        f"<tr><td class='k'>{a}</td><td>{b}</td><td><span class='chip {'ok' if c == 'จำเป็น' else ''}'>{c}</span></td></tr>"
        for a, b, c in need
    )
    body = f"""<div class='row' style='align-items:stretch;flex:1'>
<div class='card' style='flex:1.15;padding:10px 20px'><div class='eyebrow' style='margin:6px 0'>ข้อมูลที่ต้องการ — จำนวนรวม ไม่ใช้ข้อมูลส่วนบุคคล</div><table>{tb}</table>
<p style='font-size:13.5px;color:var(--mute);margin:6px 0 2px;line-height:1.5'>ต้องยืนยันกับ SKY: BRS ส่งออกเวลาสแกนรายขั้นเป็นจำนวนรวมได้หรือไม่</p>
<div style='border-top:1px solid var(--line);margin-top:6px;padding-top:6px;font-size:14.5px;line-height:1.6'><b style='color:var(--red)'>ความเสี่ยง → ทางลด</b><br>ไม่มีข้อมูล handler → ยังทำงานได้ แต่ไม่ระบุสาเหตุ<br>สแกนหายหรือมาช้า → ขอให้ตรวจสอบ ไม่เดา<br>เกณฑ์ไม่ตรงสนามบินจริง → ยืนยันกับผู้เชี่ยวชาญก่อน</div></div>
<div class='col' style='flex:1'>
<div class='card'><h3 style='margin-bottom:6px'>วิธีนำไปใช้</h3><div style='font-size:17px;line-height:1.75'>① อ่านอย่างเดียว (read-only)<br>② คนอนุมัติทุกคำแนะนำ<br>③ ไม่ควบคุมอุปกรณ์ใด<br>④ ถ้า One TrustX หยุด ระบบเดิมทำงานต่อ</div></div>
<div class='card' style='padding:8px'><img src='screenshots/report/live-baggage-flood.jpg' style='width:100%;height:205px;object-fit:cover;object-position:top left;border-radius:12px;display:block'><div style='font-size:13px;color:var(--mute);margin:6px 8px 2px'>ต้นแบบที่ใช้งานได้: onetrustx.vercel.app/baggage (ข้อมูลจำลอง)</div></div></div></div>"""
    return slide(
        6,
        "ความเป็นไปได้ / Feasibility",
        "สร้างได้จริง <em>เพราะใช้ข้อมูลที่ SKY มีอยู่แล้ว</em>",
        None,
        body,
        "ต้นแบบทำงานบนข้อมูลสังเคราะห์ที่ติดป้ายที่มาทุกค่า (15 ค่า: จริง 2 · อ้างอิง 1 · คำนวณ 1 · สมมติฐาน 11) · ความเสี่ยงหลัก: การเข้าถึงข้อมูล ground handler และการยืนยันเกณฑ์กับผู้เชี่ยวชาญ",
    )


def s7():
    top = FLOOD["bags_missed_total_plan"]
    w2 = FLOOD["bags_missed_total_priority"] / top * 78
    kpis = [
        (
            pct(FLOOD["bags_missed_reduction_pct"]),
            "กระเป๋าตกเที่ยวบินลดลง",
            f"{n(top)} → {n(FLOOD['bags_missed_total_priority'])} ใบ รวม {RUNS} รอบ",
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
            f"ตรวจจับข้อมูลผิด {n(CAUGHT)}/{n(INJECTED)} รายการ · ปฏิเสธข้อมูลถูก 0/{n(TRUST['clean_records'])}",
        ),
    ]
    kp = "".join(
        f"<div class='card' style='padding:12px 18px'><div style='display:flex;align-items:baseline;gap:12px'><div style='font-weight:800;font-size:30px;color:var(--red);white-space:nowrap'>{a}</div><div style='font-size:15.5px;font-weight:700;line-height:1.35'>{b}</div></div><div style='font-size:13px;color:var(--mute);margin-top:1px'>{c}</div></div>"
        for a, b, c in kpis
    )
    body = f"""<div class='row' style='align-items:stretch;flex:1'>
<div class='col' style='flex:1.4;justify-content:space-between'>
<div class='card'><div style='display:flex;justify-content:space-between'><div class='eyebrow'>กระเป๋าตกเที่ยวบิน · สถานการณ์น้ำท่วม · รวม {RUNS} รอบ</div><span class='chip sim'>ผลจำลอง</span></div>
<div style='margin-top:12px;font-size:15.5px;font-weight:600'>แบ่งกำลังเท่ากันทุกเที่ยวบิน (วิธีเดิม — สมมติฐาน)</div><div style='display:flex;align-items:center;gap:12px'><div class='bar' style='width:78%;background:#8da2c0'></div><b style='font-size:21px'>{n(top)}</b></div>
<div style='margin-top:10px;font-size:15.5px;font-weight:600'>จัดลำดับตามที่ One TrustX แนะนำ</div><div style='display:flex;align-items:center;gap:12px'><div class='bar' style='width:{w2:.1f}%;background:var(--red)'></div><b style='font-size:21px'>{n(FLOOD["bags_missed_total_priority"])}</b></div></div>
<div class='card dark' style='font-size:15.5px;line-height:1.65'><b style='color:#ff8d97'>ยังวัดไม่ได้ในรอบนี้ — จะวัดในรอบ prototype</b><br>เวลาประสานงานของคน: ให้ผู้ควบคุมงานทำสถานการณ์เดียวกันสองแบบ (มี/ไม่มีหน้าจอ) จับเวลาจากสัญญาณแรกถึงมีผู้รับผิดชอบรับงาน<br>ความล่าช้าของเที่ยวบิน: ต้องเพิ่มกฎการรอกระเป๋าในแบบจำลอง หรือเทียบกับข้อมูลย้อนหลัง</div></div>
<div class='col' style='flex:1.1;gap:8px;justify-content:space-between'>{kp}</div></div>"""
    return slide(
        7,
        "ผลที่คาดหวัง / Impact",
        "ผลที่คาดหวัง <em>และวัดได้</em>",
        None,
        body,
        f"จำลอง {RUNS} รอบต่อสถานการณ์ ข้อมูลสังเคราะห์ ไม่ใช่ผลของสนามบินจริง · ตัวเลขลดลงขึ้นกับสมมติฐานว่าวิธีเดิมคือแบ่งกำลังเท่ากัน ถ้า handler จริงจัดลำดับดีอยู่แล้ว ผลจะน้อยกว่านี้ · ความจริงที่ใช้ตรวจมาจากแบบจำลองเดียวกัน",
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
        f"<div class='card' style='flex:1;border-top:6px solid {'var(--green)' if i == 3 else 'var(--red)'}'><div style='font-weight:800;font-size:34px;color:{'var(--green)' if i == 3 else 'var(--red)'}'>{a}</div><h3 style='font-size:19px;margin:2px 0 6px'>{b}</h3><div style='font-size:15px;color:var(--mute);line-height:1.6'>{c}</div></div>"
        for i, (a, b, c) in enumerate(ph)
    )
    vision = ["Baggage", "Turnaround", "Gate", "Passenger", "Cargo"]
    vf = "<span class='arr'>→</span>".join(
        f"<div class='node {'hot' if i == 0 else ''}' style='padding:9px 6px'><b>{v}</b></div>"
        for i, v in enumerate(vision)
    )
    body = f"""<div class='row' style='align-items:stretch'>{cards}</div>
<div class='card'><div class='eyebrow' style='margin-bottom:8px'>วิสัยทัศน์ — ขยายหลังพิสูจน์คุณค่าแล้วเท่านั้น</div><div class='flow'>{vf}</div></div>
<div class='quote' style='color:#fff'>เริ่มจากกระเป๋า ที่ทุกนาทีและทุกการเปลี่ยนมือมีค่า<br><span>แล้วขยายสู่ชั้นข้อมูลที่ไว้ใจได้ของ Future Aviation Hub</span></div>"""
    return slide(
        8,
        "แผนต่อไป / Development Plan",
        "แผนสำหรับ <em>Prototype Phase</em>",
        None,
        body,
        "กำหนดการอื่นนอกจากวันที่ 22 ต.ค. 2026 (Pitch) จะยืนยันตามประกาศของทีมงาน SKY Innovation Spark",
    )


def build(output: Path):
    page = f"""<!doctype html><html lang='th'><head><meta charset='utf-8'><title>One TrustX · Preliminary Pitch</title>
<link href='https://fonts.googleapis.com/css2?family=IBM+Plex+Sans+Thai:wght@400;500;600;700&display=swap' rel='stylesheet'>
<style>{CSS}</style></head><body style='background:#071428'>{"".join(f() for f in (s1, s2, s3, s4, s5, s6, s7, s8))}</body></html>"""
    output.write_text(page)
    print(output)


if __name__ == "__main__":
    build(ROOT / "docs/onetrustx_PreliminaryPitch.html")
