import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "Window Commander — Voice control your terminal from your phone",
  description:
    "Phone-controlled window manager + push-to-talk voice for AI agent terminals. Hold a button on your phone, speak, watch the text appear and run in Claude Code, Cursor, or any terminal.",
  openGraph: {
    title: "Window Commander",
    description:
      "Phone-controlled window manager + voice for AI agent terminals.",
    type: "website",
  },
  metadataBase: new URL("https://windowcommander.app"),
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html
      lang="en"
      className={`${geistSans.variable} ${geistMono.variable} h-full antialiased`}
    >
      <body className="min-h-full flex flex-col bg-black text-zinc-100">
        {children}
      </body>
    </html>
  );
}
