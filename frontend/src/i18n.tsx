import { useSyncExternalStore } from "react";
import translations from "./locales/th.json";
let language: "en" | "th" = "en";
try {
  language = localStorage.getItem("onetrustx-language") === "th" ? "th" : "en";
} catch {
  /* optional storage */
}
const listeners = new Set<() => void>();
export function setLanguage(next: "en" | "th") {
  language = next;
  document.documentElement.lang = next;
  try {
    localStorage.setItem("onetrustx-language", next);
  } catch {
    /* optional storage */
  }
  listeners.forEach((fn) => fn());
}
export function useLanguage() {
  return useSyncExternalStore(
    (fn) => {
      listeners.add(fn);
      return () => {
        listeners.delete(fn);
      };
    },
    () => language,
  );
}
const dictionary: Record<string, string> = translations;
const phrases = Object.keys(dictionary).sort((a, b) => b.length - a.length);
export function translate(value: string): string {
  if (language === "en") return value;
  const clean = value.replace(/\s+/g, " ").trim();
  if (dictionary[clean]) return dictionary[clean];
  // Dynamic labels retain identifiers and numbers; translate their known copy fragments.
  let output = value;
  for (const key of phrases)
    if (key.length > 3 && output.includes(key))
      output = output.split(key).join(dictionary[key]);
  return output;
}
export function text<T>(value: T): T {
  return (typeof value === "string" ? translate(value) : value) as T;
}
export function LanguageSwitch() {
  const lang = useLanguage();
  return (
    <div
      className="landing-language"
      role="group"
      aria-label={lang === "th" ? "ภาษา" : "Language"}
    >
      <button
        type="button"
        lang="th"
        aria-pressed={lang === "th"}
        onClick={() => setLanguage("th")}
      >
        ไทย
      </button>
      <button
        type="button"
        lang="en"
        aria-pressed={lang === "en"}
        onClick={() => setLanguage("en")}
      >
        English
      </button>
    </div>
  );
}
window.addEventListener("storage", (e) => {
  if (e.key === "onetrustx-language")
    setLanguage(e.newValue === "th" ? "th" : "en");
});
document.documentElement.lang = language;

export function registerTranslation(en: string, th: string) {
  dictionary[en.replace(/\s+/g, " ").trim()] = th;
}
