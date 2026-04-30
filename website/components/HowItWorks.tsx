const steps = [
  {
    n: "01",
    title: "Install the desktop agent",
    body: "Download the Windows installer (macOS coming soon). It runs as a tray app and opens a local WebSocket on your LAN.",
  },
  {
    n: "02",
    title: "Open the app on your phone",
    body: "Web app — no install needed. Add to home screen for one-tap launch. Enter your desktop's local IP, shown in the tray icon.",
  },
  {
    n: "03",
    title: "Pick a terminal, hold to speak",
    body: "Tap the window you want to control. It glows green. Hold the mic button, speak, release. Text appears, Enter fires, agent runs.",
  },
];

export function HowItWorks() {
  return (
    <section id="how" className="border-t border-white/5 py-28">
      <div className="mx-auto max-w-6xl px-6">
        <div className="mx-auto max-w-2xl text-center">
          <p className="mb-4 font-mono text-[11px] uppercase tracking-widest text-[#22d3ee]/80">
            How it works
          </p>
          <h2 className="text-balance text-4xl font-medium tracking-tight sm:text-[52px] sm:leading-[1.1]">
            Set up in 60 seconds
          </h2>
          <p className="mt-4 text-lg text-white/60">
            One desktop install, one phone tap. Done.
          </p>
        </div>

        <div className="mt-20 grid grid-cols-1 gap-12 md:grid-cols-3">
          {steps.map((s) => (
            <div key={s.n} className="relative">
              <div className="font-mono text-sm tracking-widest text-[#22d3ee]">
                {s.n}
              </div>
              <div className="mt-3 h-px w-12 bg-white/20" />
              <h3 className="mt-6 text-xl font-medium text-white">{s.title}</h3>
              <p className="mt-3 text-[15px] leading-relaxed text-white/60">
                {s.body}
              </p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
