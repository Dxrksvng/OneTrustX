# One TrustX — รายงานส่งต่อทีม

วันที่ตรวจ: 13 กันยายน 2026

## ลิงก์ทดลอง

- เว็บสาธารณะ: https://selected-enquiries-celebrities-golf.trycloudflare.com
- เดโมนำทาง: https://selected-enquiries-celebrities-golf.trycloudflare.com/demo
- หน้า Operations: https://selected-enquiries-celebrities-golf.trycloudflare.com/overview
- Passenger: https://selected-enquiries-celebrities-golf.trycloudflare.com/journey
- แหล่งข้อมูล: https://selected-enquiries-celebrities-golf.trycloudflare.com/sources
- เครื่องเจ้าของ: http://localhost:8080

นี่คือ public preview ผ่าน Cloudflare Quick Tunnel ไม่ใช่ production hosting
ถาวร ต้องเปิด Mac, Docker Desktop และ container ไว้ ลิงก์อาจเปลี่ยนเมื่อ tunnel
เริ่มใหม่ ไม่ต้องสมัครบัญชีเพื่อทดลอง ข้อมูลและการอนุมัติทั้งหมดเป็นเดโมสังเคราะห์
ทุกคนใช้สถานการณ์เดียวกัน กรุณาผลัดกันกด Reset/Accept ระหว่างการนำเสนอ

## ทดลองใน 3 นาที

1. เปิด `/demo` แล้วกด **Start / restart guided demo**
2. ระบบเริ่มสถานการณ์ปกติ เพิ่ม demand และแสดงคิวอนาคต
3. หน้าด้านขวาเปลี่ยนไปที่ Forecast และ Simulator ตามขั้นตอนจริง
4. เปรียบเทียบ No Action, Open A5, Redirect 20%, Combined
5. ระบบบันทึกการยอมรับคำแนะนำในเดโมที่ผู้ใช้เริ่มเอง
6. รีเซ็ตเป็นกรณีผู้โดยสารเพื่อสาธิต Safe Time 34 → 11 เมื่อ C8 → E7
7. จบที่ Performance; ดูผลคำนวณและข้อจำกัด

ใช้ Pause/Resume/Next step เมื่อต้องการเล่าเอง เดโมจะเก็บ Audit แม้กด Reset
หากขึ้น DATA STALE ให้กด Reset demo เพื่อเริ่มชุดจำลองใหม่ ไม่ใช่ refresh เซนเซอร์จริง

## ทดลองด้วยตนเอง

- `/overview`: Reset demo → Start peak event → Compare interventions
- `/future`: Current/+15/+30/+60 และเลือก checkpoint เพื่อดูช่วงคาดการณ์
- Presentation tools: เปิด Future Slider หรือเปิดการเคลื่อนไหวเส้นทาง
- `/simulator`: เลือกกลยุทธ์ → ตรวจ baseline/proposed → ใส่เหตุผล → Submit recommendation
- Presentation tools ใน Simulator: ลาก Before/After เพื่อเล่าผลกระทบ
- `/operations`: Investigate Security A → Analyse options
- `/flights`: ค้นหา TT401 → ดู timeline ที่ระบุ PLANNED/SYNTHETIC
- `/passenger-flow`: เปลี่ยน horizon และดูปริมาณเข้าแต่ละ checkpoint
- `/performance`: แยก operational outcome กับ model quality
- `/journey`: Reset demo → Simulate gate change → Safe Time และเส้นทางเปลี่ยน
- `/app/audit`: ตรวจเหตุผล การยอมรับ/ปฏิเสธ/override และบันทึกผลจำลอง
- Ask One TrustX: explanation layer แบบ deterministic ไม่ต้องมี cloud LLM

## ข้อมูลที่ใช้

REAL_PUBLIC: OurAirports, Open-Meteo, OpenSky caches ดึงเมื่อ 12 กันยายน 2026
เวลา 17:07 UTC; เป็นข้อมูลประกอบ ไม่ใช่ข้อมูลคิวจริง

SYNTHETIC: เที่ยวบิน TT401–TT404, ผู้โดยสารนิรนาม 580 ราย, คิว, เลน, พนักงาน,
สัมภาระ, งานภาคพื้น, สถานะเกต

SIMULATED: การพยากรณ์ ผลเปรียบเทียบ Passenger Minutes Saved และ Safe Time
ASSUMPTION: ผัง terminal, throughput, heuristic confidence และ risk budget

Simulated MVP Result — Not actual airport performance.

ภาพสนามบินกลางคืนและภาพ terminal twin เป็นภาพ AI-generated ของสนามบินสมมติ
ไม่ได้เป็นภาพ/แผนผังสำรวจของสุวรรณภูมิ ตัวเลข reference ไม่ได้ถูกนำมาอ้างเป็นผลจริง

## ข้อจำกัดที่ต้องบอกกรรมการ

- เป็น decision-support MVP ไม่มีการสั่งงานอุปกรณ์สนามบินจริง
- Demo auth ไม่ใช่ production SSO; public preview ไม่มีข้อมูลส่วนบุคคล
- Confidence ยังเป็น heuristic และยังไม่ผ่าน calibration จริง
- เป้าหมายความแม่นยำบาง horizon ยังไม่ผ่าน; ไม่มีการ promote ML
- ไม่พบ dataset ปฏิบัติการอื่นในโฟลเดอร์ที่ย้ายมา นอกเหนือจาก public caches และ synthetic CSV
- รูปประกอบใกล้ mood reference แต่ไม่ใช่ exact asset; operational map เป็น overlay บนภาพสมมติ
- คนเปิดหลายหน้าหรือหลายคนพร้อมกันแชร์ state; stale/version guards ป้องกันการยอมรับที่ล้าสมัย
- การปิด Mac/Docker จะทำให้ public preview หยุด ต้องย้าย backend/PostgreSQL ไป host ถาวรก่อนใช้เป็น production

## การดูแลเดโม

โฟลเดอร์: `/Users/jswvn/Desktop/missj/my-exp/HACKTHON/sky ict/onetrustx`

```bash
cd '/Users/jswvn/Desktop/missj/my-exp/HACKTHON/sky ict/onetrustx'
docker compose --env-file .env -f infra/docker-compose.yml up -d
# ดู URL หลัง tunnel restart
docker logs airport-timetwin-share 2>&1 | rg 'trycloudflare.com'
# ปิดการแชร์สาธารณะ โดยไม่ลบข้อมูล
docker stop airport-timetwin-share
# เปิดการแชร์อีกครั้ง (URL อาจเปลี่ยน)
docker start airport-timetwin-share
```

ไม่มีการส่ง .env หรือ credentials ให้ผู้ทดลอง การแชร์ source ให้ใช้ Git และไม่ส่ง
.env, database files, node_modules หรือ .venv

## วิธีแจ้งปัญหา

ส่ง URL ของหน้า ขั้นตอนที่กด ผลที่คาดหวัง ผลที่เห็น screenshot และเวลาที่พบ
ระบุว่ามีคนอื่นกด Reset/Submit พร้อมกันหรือไม่

## ผลตรวจส่งมอบ

- Frontend build และ lint ผ่าน
- Backend 18 tests และ frontend unit 2 tests ผ่านในงานรอบนี้
- Browser suite ล่าสุด 13 tests ผ่านหลังคืนพื้นที่ดิสก์และตรวจ database recovery
- ทดสอบผ่าน public URL เพิ่ม 2 tests: reset/predict/compare/accept/passenger/audit และ landing/forecast/copilot ผ่าน
- `/health` และ `/team-report.html` ผ่าน public URL ตอบ HTTP 200
- PostgreSQL migration อยู่ที่ 001 (head)
- คืนพื้นที่จาก unused Docker build cache 5.559 GB; ไม่ลบฐานข้อมูลหรือ volumes
