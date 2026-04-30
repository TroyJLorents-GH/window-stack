const features = [
  {
    title: "Push-to-talk voice",
    body: "Hold a button on your phone, speak. Whisper transcribes, the text auto-pastes into your selected terminal, and Enter fires automatically.",
  },
  {
    title: "Visual targeting",
    body: "Selected window glows green on your desktop. Red while listening. Blue while transcribing. You always know where the voice is going.",
  },
  {
    title: "Drag-and-drop layouts",
    body: "Phone shows a live minimap of your monitors. Drag windows into a 2x2 grid, side-by-side, or any custom layout — instantly.",
  },
  {
    title: "Multi-window cycle",
    body: "Cycle through open terminals from your phone. Orchestrate Claude Code, Cursor, and a server log all at once.",
  },
  {
    title: "Bring your own key",
    body: "Free tier uses your OpenAI key. About six tenths of a cent per minute. No middleman, no markup, no servers in between.",
  },
  {
    title: "Built for AI agents",
    body: "Designed for Claude Code, Cursor agent mode, Codex CLI, Aider — anywhere you'd otherwise be typing into a terminal all day.",
  },
];

export function Features() {
  return (
    <section className="border-t border-white/5 py-28">
      <div className="mx-auto max-w-6xl px-6">
        <div className="mx-auto max-w-2xl text-center">
          <p className="mb-4 font-mono text-[11px] uppercase tracking-widest text-[#22d3ee]/80">
            Features
          </p>
          <h2 className="text-balance text-4xl font-medium tracking-tight sm:text-[52px] sm:leading-[1.1]">
            Your terminal, hands-free
          </h2>
          <p className="mt-4 text-lg text-white/60">
            Built for the new generation of AI agent workflows.
          </p>
        </div>

        <div className="mt-20 grid grid-cols-1 gap-px overflow-hidden rounded-lg border border-white/10 bg-white/5 md:grid-cols-2 lg:grid-cols-3">
          {features.map((f) => (
            <div
              key={f.title}
              className="bg-[#0d0d0d] p-8 transition hover:bg-[#141414]"
            >
              <div className="mb-5 inline-flex h-8 w-8 items-center justify-center rounded-md border border-white/10 bg-white/[0.03]">
                <span className="h-1.5 w-1.5 rounded-full bg-[#22d3ee] shadow-[0_0_6px_#22d3ee]" />
              </div>
              <h3 className="text-lg font-medium text-white">{f.title}</h3>
              <p className="mt-3 text-[15px] leading-relaxed text-white/60">
                {f.body}
              </p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
