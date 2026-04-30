# Window Commander PWA — Mobile App Rebuild Spec

## Why PWA over Expo native

| Concern | Expo native | PWA |
|---|---|---|
| Install friction | App Store / TestFlight / Apple Dev $99/yr | Visit URL → Add to Home Screen |
| Distribution | Apple/Google review (1-7 days) | `git push` → live in seconds |
| Mic recording | `expo-av` Audio.Recording | `MediaRecorder` API (works iOS Safari 14.5+) |
| WebSocket | `WebSocket` polyfill | Native `WebSocket` |
| File access | `expo-file-system` | `Blob` / `FormData` |
| Background recording | Yes | No (PWAs sleep on backgrounding) |
| iOS Action Button binding | Yes (Shortcuts) | No |
| Update mechanism | EAS Update (OTA) | Refresh page |
| Cost | $99/yr Apple + $25 Google | $0 |

**Verdict:** PWA wins for MVP. Native iOS only needed if Action Button binding becomes a key UX. Could ship both later — same WS protocol, two clients.

## Tech stack

- **Framework:** Next.js 16 (matches website, monorepo-friendly)
- **Routing:** App Router, single SPA route at `/`
- **Recording:** `MediaRecorder` API → audio/webm or audio/mp4
- **Transport:** Native `WebSocket` to `ws://<desktop-ip>:8000/ws`
- **State:** React `useState` + `useReducer` (no need for Redux/Zustand at this size)
- **Styling:** Tailwind 4 (already on website)
- **PWA shell:** `next-pwa` plugin OR hand-rolled service worker + manifest.json
- **Hosting:** Vercel (subdomain `app.windowcommander.app`)

## Repo structure

```
window-commander/
  desktop/            ← unchanged (Python FastAPI server)
  mobile/             ← OLD Expo app (keep until PWA ships, then delete)
  website/            ← marketing landing page (NEW, just shipped)
  pwa/                ← NEW mobile web app
    app/
      page.tsx        ← single-page app
      manifest.json
      icons/
    components/
      ConnectScreen.tsx     ← enter desktop IP
      MinimapScreen.tsx     ← live monitor minimap, drag windows
      VoiceButton.tsx       ← PTT, MediaRecorder
      WindowList.tsx        ← list of detected windows
    hooks/
      useWindowCommander.ts ← WS connection + state
      useRecorder.ts        ← MediaRecorder wrapper
    services/
      websocket.ts          ← reconnecting WS client
    lib/
      protocol.ts           ← WS message types (shared schema)
    public/
      sw.js                 ← service worker for PWA install
```

## WebSocket protocol — UNCHANGED

Desktop server.py expects same JSON messages. PWA sends/receives identical schema. This is the value of the existing protocol — both clients (Expo native, PWA) speak it.

```typescript
// outgoing
{ action: "list_windows" }
{ action: "focus_window", hwnd: number, process_name?: string }
{ action: "apply_layout", layout: "2x2" | "split" | ..., windows: number[] }
{ action: "voice_transcribe", audio: string /* base64 */, format: "webm" | "mp4" }

// incoming
{ type: "windows", windows: Window[] }
{ type: "voice_result", success: boolean, text: string, injected_to?: number }
{ type: "error", message: string }
```

## Critical iOS Safari quirks

These bit hard — bake into V1:

1. **Mic permission:** Must be triggered by direct user gesture (button tap). Cannot prompt on page load.
2. **MediaRecorder MIME:** iOS Safari only supports `audio/mp4`. Android Chrome supports `audio/webm;codecs=opus`. Detect with `MediaRecorder.isTypeSupported()` and pick best, send format to server.
3. **AudioContext autoplay:** Don't initialize until user gesture, or it's suspended.
4. **PWA install prompt:** iOS doesn't trigger `beforeinstallprompt`. Show manual instructions banner: "Tap Share → Add to Home Screen."
5. **Service worker scope:** Must be served from root. Cannot scope to subpath without manifest tricks.
6. **Backgrounding:** When user puts phone in pocket or switches apps, JS pauses. WebSocket dies, MediaRecorder stops. Reconnect on `visibilitychange` event.
7. **Wake lock:** Use `navigator.wakeLock` API to keep screen awake during active session (so PTT button stays alive).
8. **HTTPS required:** Mic API + service worker need HTTPS. Vercel handles this. For local desktop WS though, browser will block `wss://` connecting to `ws://`. Options:
   - **A:** PWA over HTTP only (lose service worker, lose install prompt — bad)
   - **B:** Tunnel desktop server via Tailscale or Cloudflare Tunnel (extra setup)
   - **C:** Generate self-signed cert on desktop, accept warning (annoying)
   - **D:** Recommended — desktop server runs HTTPS with mkcert-generated cert installed in iOS trust store. One-time setup script.

This HTTPS-to-localhost issue is the biggest PWA blocker. Solve it before anything else.

## Backend changes

`desktop/server.py` needs minor updates:

1. Accept multiple audio formats (`webm`, `mp4`, existing `m4a`). Whisper API supports all.
2. Optional: add HTTPS support via `uvicorn --ssl-keyfile --ssl-certfile`.
3. Add CORS headers for the PWA origin (Vercel domain).
4. Heartbeat ping/pong every 20s to keep WS alive on iOS.

## Build phases

**Phase 1 — bare PWA (1-2 days)**
- [ ] Scaffold `pwa/` folder with Next.js
- [ ] manifest.json + icons + service worker
- [ ] ConnectScreen + WS connect
- [ ] WindowList + focus action
- [ ] VoiceButton with MediaRecorder + base64 send
- [ ] Verify end-to-end on iPhone in dev (over LAN, accept cert warning)

**Phase 2 — distribution (1 day)**
- [ ] Deploy to Vercel
- [ ] Custom domain `app.windowcommander.app`
- [ ] mkcert script for desktop HTTPS
- [ ] Add to Home Screen banner with iOS-specific instructions
- [ ] Wake lock for active sessions

**Phase 3 — polish (1-2 days)**
- [ ] Minimap drag-and-drop window layouts
- [ ] Visual feedback (matching desktop overlay colors on phone UI)
- [ ] Reconnect on visibilitychange
- [ ] Offline page

**Phase 4 — sunset Expo app**
- [ ] Verify PWA covers all current Expo features
- [ ] Delete `mobile/` folder
- [ ] Update website download links

## Cost estimate

- Vercel hobby tier: $0
- Domain: $12/yr
- mkcert + self-signed: $0
- TOTAL: $12/yr to ship

vs Expo native:
- Apple Developer: $99/yr
- Google Play one-time: $25
- EAS build minutes: free tier OK for low volume
- TOTAL: $99/yr + Apple review hassle

## Open questions before starting

1. Will the HTTPS-to-localhost solution actually work for non-technical users? If mkcert install is too hard, consider mandatory cloud relay (extra latency, privacy tradeoff).
2. Does iOS PWA backgrounding kill the experience? Test before committing.
3. Does the lack of Action Button binding matter, or is "open PWA → tap mic" fast enough?

These three answers determine whether PWA is the right call or whether we go native after all.
