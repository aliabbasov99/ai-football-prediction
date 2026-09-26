import type { Metadata } from "next";
import "./globals.css";
import { Navbar } from "@/components/Navbar";
import { Footer } from "@/components/Footer";
import { CouponPanel } from "@/components/CouponPanel";
import { CouponProvider } from "@/context/CouponContext";

export const metadata: Metadata = {
  title: "AI Football Prediction",
  description:
    "7+ mənbədən əmsal və proqnoz məlumatlarını toplayan futbol analitika platforması",
};

export default function RootLayout({
  children,
}: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="az">
      <body className="flex min-h-screen flex-col antialiased">
        <CouponProvider>
          <Navbar />
          <main className="mx-auto w-full max-w-[1600px] flex-1 px-4 py-6">
            {children}
          </main>
          <Footer />
          <CouponPanel />
        </CouponProvider>
      </body>
    </html>
  );
}
