import "./globals.css";
import Link from "next/link";
import type { ReactNode } from "react";

export const metadata = {
  title: "LLM Data Analytics",
  description: "Local-first data analyst copilot",
};

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="en">
      <body>
        <div className="min-h-screen bg-slate-950 text-slate-100">
          <header className="border-b border-slate-800">
            <div className="mx-auto flex max-w-6xl items-center justify-between px-6 py-4">
              <div>
                <Link href="/" className="text-lg font-semibold text-white">
                  LLM Data Analytics
                </Link>
                <p className="text-xs text-slate-400">Local-first analyst copilot</p>
              </div>
              <nav className="flex items-center gap-4 text-sm text-slate-300">
                <Link href="/" className="hover:text-white">
                  Dashboard
                </Link>
                <Link href="/settings" className="hover:text-white">
                  Settings
                </Link>
              </nav>
            </div>
          </header>
          <main className="mx-auto max-w-6xl px-6 py-8">{children}</main>
        </div>
      </body>
    </html>
  );
}
