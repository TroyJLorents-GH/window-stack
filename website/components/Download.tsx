const platforms = [
  {
    icon: "🖥",
    name: "Desktop — Windows",
    body: "Single .exe installer. Win10/11. Auto-launches on boot.",
    cta: "Download v0.1",
    href: "#",
    available: true,
  },
  {
    icon: "🍎",
    name: "Desktop — macOS",
    body: "Apple Silicon and Intel. Join the waitlist for beta access.",
    cta: "Notify me",
    href: "#waitlist",
    available: false,
  },
  {
    icon: "📱",
    name: "Mobile — iPhone & Android",
    body: "No App Store install. Open in Safari or Chrome → Add to Home Screen.",
    cta: "Open web app",
    href: "https://app.windowcommander.app",
    available: true,
  },
  {
    icon: "⌨️",
    name: "Source on GitHub",
    body: "Self-host, fork, contribute. MIT licensed.",
    cta: "View repo",
    href: "https://github.com/troy/window-commander",
    available: true,
  },
];

export function Download() {
  return (
    <section
      id="download"
      className="border-t border-white/5 bg-[#010101] py-28"
    >
      <div className="mx-auto max-w-5xl px-6 text-center">
        <p className="mb-4 font-mono text-[11px] uppercase tracking-widest text-[#22d3ee]/80">
          Download
        </p>
        <h2 className="text-balance text-4xl font-medium tracking-tight sm:text-[52px] sm:leading-[1.1]">
          Get Window Commander
        </h2>
        <p className="mt-4 text-lg text-white/60">
          Free during beta. Bring your own OpenAI key.
        </p>

        <div className="mt-16 grid grid-cols-1 gap-px overflow-hidden rounded-lg border border-white/10 bg-white/5 sm:grid-cols-2">
          {platforms.map((p) => (
            <a
              key={p.name}
              href={p.href}
              className="group flex flex-col items-start bg-[#0d0d0d] p-7 text-left transition hover:bg-[#141414]"
            >
              <div className="mb-5 flex w-full items-center justify-between">
                <span className="text-2xl">{p.icon}</span>
                {p.available ? (
                  <span className="font-mono text-[10px] uppercase tracking-widest text-[#22d3ee]">
                    Available
                  </span>
                ) : (
                  <span className="font-mono text-[10px] uppercase tracking-widest text-white/40">
                    Soon
                  </span>
                )}
              </div>
              <h3 className="text-lg font-medium text-white">{p.name}</h3>
              <p className="mt-2 text-[15px] leading-relaxed text-white/60">
                {p.body}
              </p>
              <div
                className={`mt-5 text-sm ${
                  p.available
                    ? "text-[#22d3ee] group-hover:text-[#67e8f9]"
                    : "text-white/50 group-hover:text-white/70"
                }`}
              >
                {p.cta} →
              </div>
            </a>
          ))}
        </div>
      </div>
    </section>
  );
}
