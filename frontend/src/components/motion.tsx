"use client";

/**
 * Paylaşılan Framer Motion primitivləri.
 *
 * Tətbiq boyu "fade-in" və "slide-up" üçün tək mənbə — beləcə hər komponent
 * öz `initial`/`transition` obyektini təkrarlamır, tempo hər yerdə eyni olur.
 *
 * `prefers-reduced-motion` nəzərə alınır: istifadəçi hərəkəti azaltmayış
 * seçibsə, animasiyalar praktiki olaraq sıfırlanır (duration ~0).
 */
import { motion, useReducedMotion, type Variants } from "framer-motion";
import type { ComponentProps, ReactNode } from "react";

/* ── Tempo (8px ritmi + 160ms keçid) ─────────────────────────────────── */

export const EASE_OUT = [0.22, 1, 0.36, 1] as const;

export const DUR = {
  fast: 0.14,
  base: 0.22,
  slow: 0.38,
} as const;

/* ── Əsas variantlar ──────────────────────────────────────────────────── */

/** Sadə görünmə: yalnız opacity. */
export const fadeIn: Variants = {
  hidden: { opacity: 0 },
  show: { opacity: 1, transition: { duration: DUR.base, ease: EASE_OUT } },
};

/** Yuxarıdan sürüşmə — əsas "kontent gəlir" hissi. */
export const slideUp: Variants = {
  hidden: { opacity: 0, y: 12 },
  show: {
    opacity: 1,
    y: 0,
    transition: { duration: DUR.slow, ease: EASE_OUT },
  },
};

/** Sətirlərin ardıcıl (staggered) görünməsi. */
export const staggerList: Variants = {
  hidden: {},
  show: {
    transition: { staggerChildren: 0.045, delayChildren: 0.02 },
  },
};

export const staggerItem: Variants = {
  hidden: { opacity: 0, y: 8 },
  show: { opacity: 1, y: 0, transition: { duration: DUR.base, ease: EASE_OUT } },
};

/* ── Mikro-interaksiya presetləri (whileHover / whileTap) ──────────────── */

export const hoverLift = {
  y: -2,
  transition: { duration: DUR.fast, ease: EASE_OUT },
} as const;

export const hoverScale = {
  scale: 1.01,
  transition: { duration: DUR.fast, ease: EASE_OUT },
} as const;

export const tapScale = {
  scale: 0.98,
  transition: { duration: 0.1, ease: EASE_OUT },
} as const;

/* ── Hazır komponentlər ────────────────────────────────────────────────── */

/** Səhifə/sətir başlığı — avtomatik fade-in + slide-up. */
export function Reveal({
  children,
  className,
  delay = 0,
  ...rest
}: {
  children: ReactNode;
  className?: string;
  delay?: number;
} & Omit<ComponentProps<typeof motion.div>, "variants" | "children">) {
  const reduce = useReducedMotion();
  return (
    <motion.div
      className={className}
      initial={reduce ? false : { opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      transition={
        reduce
          ? { duration: 0 }
          : { duration: DUR.slow, ease: EASE_OUT, delay }
      }
      {...rest}
    >
      {children}
    </motion.div>
  );
}

/** Siyahının özələkini (fade + slide) — `staggerList` ilə işləyir. */
export function RevealItem({
  children,
  className,
  ...rest
}: {
  children: ReactNode;
  className?: string;
} & Omit<ComponentProps<typeof motion.div>, "variants" | "children">) {
  const reduce = useReducedMotion();
  return (
    <motion.div
      className={className}
      variants={reduce ? undefined : staggerItem}
      {...rest}
    >
      {children}
    </motion.div>
  );
}

/** `hover:scale-1.01` + `tap:scale-0.98` — kliklənən kartlar üçün. */
export function InteractiveCard({
  children,
  className,
  ...rest
}: {
  children: ReactNode;
  className?: string;
} & ComponentProps<typeof motion.div>) {
  const reduce = useReducedMotion();
  return (
    <motion.div
      className={`card card-hover ${className ?? ""}`}
      whileHover={reduce ? undefined : hoverScale}
      whileTap={reduce ? undefined : tapScale}
      transition={{ duration: DUR.fast, ease: EASE_OUT }}
      {...rest}
    >
      {children}
    </motion.div>
  );
}
