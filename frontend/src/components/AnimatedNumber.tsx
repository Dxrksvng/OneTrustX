import { text } from "../i18n";
import { useEffect, useRef, useState } from "react";
export default function AnimatedNumber({ value }: { value: number }) {
  const [shown, setShown] = useState(value);
  const previous = useRef(value);
  useEffect(() => {
    const start = previous.current;
    previous.current = value;
    if (window.matchMedia("(prefers-reduced-motion: reduce)").matches) {
      setShown(value);
      return;
    }
    let frame = 0;
    const began = performance.now();
    const tick = (now: number) => {
      const fraction = Math.min(1, (now - began) / 600);
      setShown(start + (value - start) * (1 - Math.pow(1 - fraction, 3)));
      if (fraction < 1) frame = requestAnimationFrame(tick);
    };
    frame = requestAnimationFrame(tick);
    return () => cancelAnimationFrame(frame);
  }, [value]);
  return <span aria-label={String(value)}>{text(Math.round(shown))}</span>;
}
