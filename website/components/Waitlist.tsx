"use client";

import { useState } from "react";

export function Waitlist() {
  const [email, setEmail] = useState("");
  const [status, setStatus] = useState<"idle" | "loading" | "success" | "error">(
    "idle"
  );

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault();
    setStatus("loading");
    try {
      const res = await fetch("/api/waitlist", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email }),
      });
      if (!res.ok) throw new Error("Failed");
      setStatus("success");
      setEmail("");
    } catch {
      setStatus("error");
    }
  }

  return (
    <section id="waitlist" className="border-t border-white/5 py-28">
      <div className="mx-auto max-w-2xl px-6 text-center">
        <p className="mb-4 font-mono text-[11px] uppercase tracking-widest text-[#22d3ee]/80">
          Early access
        </p>
        <h2 className="text-balance text-4xl font-medium tracking-tight sm:text-[52px] sm:leading-[1.1]">
          Get notified
        </h2>
        <p className="mt-4 text-lg text-white/60">
          We&apos;ll email you when macOS, native iOS, and the managed-key tier
          ship.
        </p>

        <form
          onSubmit={onSubmit}
          className="mt-10 flex flex-col items-stretch gap-3 sm:flex-row"
        >
          <input
            type="email"
            required
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            placeholder="you@example.com"
            disabled={status === "loading"}
            className="flex-1 rounded-md border border-white/10 bg-white/[0.03] px-4 py-3 text-[15px] text-white placeholder-white/40 outline-none transition focus:border-[#22d3ee]/50 focus:bg-white/[0.05] disabled:opacity-50"
          />
          <button
            type="submit"
            disabled={status === "loading"}
            className="inline-flex items-center justify-center rounded-md bg-[#22d3ee] px-7 py-3 text-sm font-medium text-[#0d0d0d] shadow-[0_0_24px_rgba(34,211,238,0.25)] transition hover:bg-[#67e8f9] disabled:opacity-50"
          >
            {status === "loading" ? "Adding..." : "Join waitlist"}
          </button>
        </form>

        {status === "success" && (
          <p className="mt-4 font-mono text-xs uppercase tracking-widest text-[#22d3ee]">
            You&apos;re in. Check your inbox.
          </p>
        )}
        {status === "error" && (
          <p className="mt-4 font-mono text-xs uppercase tracking-widest text-red-400">
            Something broke. Try again.
          </p>
        )}
      </div>
    </section>
  );
}
