import coreWebVitals from "eslint-config-next/core-web-vitals";
import typescript from "eslint-config-next/typescript";

/**
 * Next.js 16 `eslint-config-next` artıq **yerli flat config** massivi
 * ixrac edir (eslintrc / FlatCompat yoxdur — FlatCompat ESLint 9.39 ilə
 * "Converting circular structure to JSON" xətası verir).
 *
 * @type {import("eslint").Linter.Config[]}
 */
const eslintConfig = [
  {
    ignores: [
      ".next/**",
      "node_modules/**",
      "out/**",
      "build/**",
      "next-env.d.ts",
      // Python yardımcı skriptləri ESLint-in iş dairəsində deyil
      "scripts/**",
    ],
  },
  ...coreWebVitals,
  ...typescript,
  {
    rules: {
      // Next-in `<img>` tövsiyəsi bu layihədə bilərəkdən keçilir:
      // loqo URLs-ləri DB-dən gəlir, `next/image` optimallaşdırması
      // uzaq hostları qeydə almaq məcburiyyəti yaradır.
      "@next/next/no-img-element": "off",
      // `<a>` yerine `next/link` istifadəsi məcburi deyil
      "@next/next/no-html-link-for-pages": "off",
    },
  },
];

export default eslintConfig;
