import { useLanguage, setLanguage } from "../i18n";
import { useEffect } from "react";
import {
  ArrowRight,
  ShieldCheck,
  Route,
  SlidersHorizontal,
  Plane,
} from "lucide-react";
export default function Landing() {
  const language = useLanguage();
  const t = (en: string, th: string) => (language === "th" ? th : en);
  useEffect(() => {
    document.documentElement.lang = language;
    document.title =
      language === "th"
        ? "One TrustX | คาดการณ์และวางแผนการเดินทางในสนามบิน"
        : "One TrustX | Airport decision intelligence";
    try {
      localStorage.setItem("timetwin-language", language);
    } catch {
      /* Storage is optional. */
    }
  }, [language]);
  return (
    <div className="landing">
      <header className="landing-nav">
        <a href="/" className="landing-brand">
        <Plane /> <span>ONE <b>TRUSTX</b></span>
        </a>
        <nav>
          <div
            className="landing-language"
            role="group"
            aria-label={t("Language", "ภาษา")}
          >
            <button
              type="button"
              lang="th"
              aria-pressed={language === "th"}
              onClick={() => setLanguage("th")}
            >
              ไทย
            </button>
            <button
              type="button"
              lang="en"
              aria-pressed={language === "en"}
              onClick={() => setLanguage("en")}
            >
              English
            </button>
          </div>
          <a href="#approach">{t("Our approach", "แนวทางของเรา")}</a>
          <a href="/journey">
            {t("Passenger journey", "การเดินทางของผู้โดยสาร")}
          </a>
          <a className="landing-button" href="/overview">
            {t("Operations centre", "ศูนย์ปฏิบัติการ")} <ArrowRight size={16} />
          </a>
        </nav>
      </header>
      <main>
        <section className="landing-hero executive-hero">
          <div className="hero-copy">
            <span className="eyebrow">
              {t(
                "ONE TRUSTX \u00b7 DECISION INTELLIGENCE",
                "ONE TRUSTX · ข้อมูลเพื่อการตัดสินใจ",
              )}
            </span>
            <h1>
              {t("See disruption before", "มองเห็นปัญหาล่วงหน้า")}
              <br />
              {t("it reaches", "ก่อนส่งผลกระทบ")}
              <br />
              {t("the passenger.", "ถึงผู้โดยสาร")}
            </h1>
            <p>
              {t(
                "Predict passenger flow, simulate operational decisions and protect every minute of the airport journey.",
                "คาดการณ์การไหลของผู้โดยสาร จำลองทางเลือกในการปฏิบัติงาน และรักษาทุกนาทีของการเดินทางในสนามบิน",
              )}
            </p>
            <div className="hero-actions">
              <a className="landing-button" href="/overview">
                {t("Explore Platform", "สำรวจแพลตฟอร์ม")}{" "}
                <ArrowRight size={18} />
              </a>
              <a className="hero-secondary" href="/demo">
                {t("View Demo Scenario \u2192", "ชมสถานการณ์จำลอง →")}
              </a>
            </div>
          </div>
          <aside className="hero-brief">
            <span className="eyebrow">
              {t("ONE TRUSTX DEMONSTRATION", "การสาธิต ONE TRUSTX")}
            </span>
            <h2>
              {t("One airport.", "สนามบินเดียวกัน")}
              <br />
              {t("Connected decisions.", "เชื่อมโยงทุกการตัดสินใจ")}
            </h2>
            <dl>
              <div>
                <dt>{t("Operational data", "ข้อมูลปฏิบัติการ")}</dt>
                <dd>{t("Synthetic", "ข้อมูลสังเคราะห์")}</dd>
              </div>
              <div>
                <dt>{t("Public context", "ข้อมูลสาธารณะประกอบ")}</dt>
                <dd>
                  {t(
                    "Airport \u00b7 Weather \u00b7 Aircraft",
                    "สนามบิน · สภาพอากาศ · อากาศยาน",
                  )}
                </dd>
              </div>
              <div>
                <dt>{t("Decision authority", "ผู้มีอำนาจตัดสินใจ")}</dt>
                <dd>{t("Human operator", "เจ้าหน้าที่ผู้ปฏิบัติงาน")}</dd>
              </div>
            </dl>
            <a href="/future">
              {t("Explore the forecast \u2192", "สำรวจการคาดการณ์ →")}
            </a>
          </aside>
          <small className="hero-asset-note">
            {t(
              "AI-generated airport illustration \u00b7 Not an actual airport or deployment",
              "ภาพสนามบินสร้างด้วย AI · ไม่ใช่ภาพสนามบินจริงหรือการติดตั้งใช้งานจริง",
            )}
          </small>
        </section>
        <section className="landing-principles" id="approach">
          <div>
            <span className="eyebrow">
              {t("A CONNECTED DECISION LAYER", "เชื่อมข้อมูลสู่การตัดสินใจ")}
            </span>
            <h2>
              {t("Clarity before", "เห็นภาพชัดเจน")}
              <br />
              {t("the next departure.", "ก่อนเที่ยวบินถัดไป")}
            </h2>
          </div>
          {[
            {
              icon: ShieldCheck,
              title: t("Anticipate pressure", "คาดการณ์ความหนาแน่น"),
              text: t(
                "Explore the next 15, 30 and 60 minutes. See forecast ranges and the assumptions behind them.",
                "ดูแนวโน้มในอีก 15, 30 และ 60 นาที พร้อมช่วงคาดการณ์และสมมติฐานที่ใช้",
              ),
              href: "/future",
            },
            {
              icon: SlidersHorizontal,
              title: t("Test the response", "ทดลองแนวทางรับมือ"),
              text: t(
                "Compare lane capacity and passenger redirection before an operator accepts an action.",
                "เปรียบเทียบความสามารถในการให้บริการและการเปลี่ยนเส้นทางผู้โดยสาร ก่อนเจ้าหน้าที่อนุมัติ",
              ),
              href: "/simulator",
            },
            {
              icon: Route,
              title: t("Protect passenger time", "รักษาเวลาของผู้โดยสาร"),
              text: t(
                "Recalculate the remaining journey when the gate or security route changes.",
                "คำนวณการเดินทางที่เหลือใหม่เมื่อประตูขึ้นเครื่องหรือเส้นทางผ่านจุดตรวจเปลี่ยนแปลง",
              ),
              href: "/journey",
            },
          ].map(({ icon: Icon, title, text, href }) => (
            <a key={title} href={href}>
              <Icon />
              <h3>{title}</h3>
              <p>{text}</p>
              <ArrowRight size={18} />
            </a>
          ))}
        </section>
        <section className="landing-difference">
          <span className="eyebrow">
            {t(
              "EXISTING INTELLIGENCE → DECISION LAYER",
              "ข้อมูลระบบเดิม → ชั้นการตัดสินใจ",
            )}
          </span>
          <h2>
            {t(
              "A decision simulator for the Future Aviation Hub.",
              "ระบบจำลองการตัดสินใจเพื่อศูนย์กลางการบินแห่งอนาคต",
            )}
          </h2>
          <p>
            {t(
                "One TrustX does not replace existing passenger-flow intelligence. It adds a prescriptive decision and simulation layer on top of it.",
                "One TrustX ไม่ได้แทนที่ระบบข้อมูลการไหลผู้โดยสารเดิม แต่เพิ่มชั้นจำลองทางเลือกและแนะนำการตัดสินใจไว้ด้านบน",
            )}
          </p>
          <p>
            {t(
              "Existing airport intelligence → Predict → Simulate alternatives → Compare → Human approval → Passenger re-plan → Measure",
              "ข้อมูลสนามบินเดิม → คาดการณ์ → จำลองทางเลือก → เปรียบเทียบ → เจ้าหน้าที่อนุมัติ → วางแผนผู้โดยสารใหม่ → วัดผล",
            )}
          </p>
          <a href="/integration">
            {t("Explore system integration →", "สำรวจการเชื่อมต่อระบบ →")}
          </a>
        </section>
        <section className="landing-close">
          <span className="eyebrow">
            {t("EXPLAINABLE BY DESIGN", "ออกแบบให้ตรวจสอบและอธิบายได้")}
          </span>
          <h2>
            {t("From airport intelligence", "จากข้อมูลเชิงลึกของสนามบิน")}
            <br />
            {t("to informed action.", "สู่การลงมืออย่างมีข้อมูล")}
          </h2>
          <p>
            {t("Public context", "ข้อมูลสาธารณะประกอบ")}.{" "}
            {t("Synthetic", "ข้อมูลสังเคราะห์")} operational scenarios.
            Traceable decisions.
          </p>
          <a className="landing-button" href="/overview">
            {t("Enter the operations centre", "เข้าสู่ศูนย์ปฏิบัติการ")}{" "}
            <ArrowRight size={18} />
          </a>
        </section>
      </main>
      <footer>
        {t(
          "One TrustX \u00b7 Decision support MVP",
          "One TrustX · ระบบต้นแบบสนับสนุนการตัดสินใจ",
        )}{" "}
        <a href="/app/sources">
          {t("Data sources & limitations", "แหล่งข้อมูลและข้อจำกัด")}
        </a>
      </footer>
    </div>
  );
}
