export function Footer() {
  return (
    <footer className="border-t border-white/5 py-12">
      <div className="mx-auto flex max-w-6xl flex-col items-center justify-between gap-4 px-6 sm:flex-row">
        <div className="flex items-center gap-3">
          <span className="inline-block h-2 w-2 rounded-full bg-[#22d3ee] shadow-[0_0_6px_#22d3ee]" />
          <span className="font-mono text-xs uppercase tracking-widest text-white/60">
            Window Commander
          </span>
        </div>
        <div className="flex items-center gap-6 font-mono text-xs uppercase tracking-widest text-white/40">
          <a
            href="https://github.com/troy/window-commander"
            className="transition hover:text-white"
          >
            GitHub
          </a>
          <a href="https://x.com/troy" className="transition hover:text-white">
            X
          </a>
          <a href="/privacy" className="transition hover:text-white">
            Privacy
          </a>
          <span className="text-white/20">
            © {new Date().getFullYear()}
          </span>
        </div>
      </div>
    </footer>
  );
}
