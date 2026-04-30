export function Nav() {
  return (
    <header className="sticky top-0 z-50 border-b border-white/5 bg-[#0d0d0d]/80 backdrop-blur-md">
      <div className="mx-auto flex h-14 max-w-6xl items-center justify-between px-6">
        <a href="/" className="flex items-center gap-2.5">
          <span className="inline-block h-2 w-2 rounded-full bg-[#22d3ee] shadow-[0_0_6px_#22d3ee]" />
          <span className="font-mono text-xs uppercase tracking-widest text-white">
            Window Commander
          </span>
        </a>
        <nav className="hidden items-center gap-7 font-mono text-[11px] uppercase tracking-widest text-white/60 sm:flex">
          <a href="#how" className="transition hover:text-white">
            How it works
          </a>
          <a href="#download" className="transition hover:text-white">
            Download
          </a>
          <a
            href="https://github.com/troy/window-commander"
            className="transition hover:text-white"
          >
            GitHub
          </a>
        </nav>
        <a
          href="#download"
          className="inline-flex h-8 items-center rounded-md bg-[#22d3ee] px-3.5 text-xs font-medium text-[#0d0d0d] transition hover:bg-[#67e8f9]"
        >
          Get it
        </a>
      </div>
    </header>
  );
}
