import { Nav } from "@/components/Nav";
import { Hero } from "@/components/Hero";
import { Features } from "@/components/Features";
import { HowItWorks } from "@/components/HowItWorks";
import { Download } from "@/components/Download";
import { Waitlist } from "@/components/Waitlist";
import { Footer } from "@/components/Footer";

export default function Home() {
  return (
    <>
      <Nav />
      <main className="flex flex-col flex-1">
        <Hero />
        <Features />
        <HowItWorks />
        <Download />
        <Waitlist />
        <Footer />
      </main>
    </>
  );
}
