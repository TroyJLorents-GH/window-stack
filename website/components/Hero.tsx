export function Hero() {
  return (
    <section className="relative overflow-hidden">
      <div className="relative mx-auto flex max-w-6xl flex-col items-center px-6 pt-28 pb-28 text-center sm:pt-36 sm:pb-40">
        <span className="mb-10 inline-flex items-center gap-2 rounded-full border border-white/10 bg-white/[0.03] px-4 py-1.5 font-mono text-[11px] uppercase tracking-widest text-white/70">
          <span className="h-1.5 w-1.5 rounded-full bg-[#22d3ee] shadow-[0_0_6px_#22d3ee]" />
          For Claude Code, Cursor, Codex
        </span>

        <h1 className="text-balance text-[44px] font-normal leading-[1.05] tracking-tight sm:text-[76px] sm:leading-[1]">
          Stop typing.
          <br />
          <span className="text-[#22d3ee]">Start talking.</span>
        </h1>

        <p className="mt-8 max-w-xl text-pretty text-lg leading-relaxed text-white/70 sm:text-xl">
          Push-to-talk voice and drag-and-drop window layouts for your AI agent
          terminals. Speak into your phone — text pastes and runs on your
          desktop. Hands-free coding from anywhere in the house.
        </p>

        <div className="mt-12 flex flex-col items-center gap-3 sm:flex-row">
          <a
            href="#download"
            className="inline-flex h-12 items-center justify-center rounded-md bg-[#22d3ee] px-7 text-sm font-medium text-[#0d0d0d] shadow-[0_0_24px_rgba(34,211,238,0.35)] transition hover:bg-[#67e8f9]"
          >
            Get Window Commander
          </a>
          <a
            href="#how"
            className="inline-flex h-12 items-center justify-center rounded-md border border-white/10 bg-white/[0.03] px-7 text-sm font-medium text-white transition hover:border-white/20 hover:bg-white/[0.06]"
          >
            How it works
          </a>
        </div>

        <div className="mt-20 w-full max-w-5xl">
          <div className="relative overflow-hidden rounded-xl border border-white/10 bg-[#1a1a1a] shadow-[0_36px_96px_-24px_rgba(0,0,0,0.75),inset_0_0_0_1px_rgba(255,255,255,0.04)]">
            <div className="flex aspect-video items-center justify-center bg-[radial-gradient(ellipse_at_center,_rgba(34,211,238,0.08),_transparent_60%)] text-white/40">
              <div className="text-center">
                <div className="mb-3 text-5xl text-[#22d3ee]/80">▶</div>
                <p className="font-mono text-xs uppercase tracking-widest">
                  Demo · phone PTT → terminal
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
