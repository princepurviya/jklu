import { useRef } from "react";
import { motion, useScroll, useTransform, useInView } from "framer-motion";

const showcaseData = [
  {
    id: "01",
    title: "Damage Detection",
    subtitle: "Surface Analysis",
    description:
      "Our AI engine actively scans artifact surfaces to detect microscopic cracks, erosion, and structural stress points. By identifying these issues early, curators can intervene before irreversible damage occurs.",
    image: "/images/damage-detection.jpg",
    features: ["Sub-millimeter precision", "Material-agnostic scanning", "Historical baseline comparison"],
  },
  {
    id: "02",
    title: "AI Surveillance",
    subtitle: "24/7 Monitoring",
    description:
      "Transform standard museum security feeds into intelligent monitoring systems. Utilizing state-of-the-art computer vision to track exhibit integrity continuously without blind spots or fatigue.",
    image: "/images/ai-monitoring.jpg",
    features: ["Integrates with existing CCTV", "Low-latency processing", "Multi-angle analysis"],
  },
  {
    id: "03",
    title: "Real-Time Alerts",
    subtitle: "Instant Notifications",
    description:
      "When anomalies are detected, the system immediately generates bounding boxes highlighting the precise area of concern, classifying the damage type, and alerting the conservation team.",
    image: "/images/ai-alerts.jpg",
    features: ["Confidence score ranking", "Mobile dashboard alerts", "Automated incident logging"],
  },
  {
    id: "04",
    title: "Artifact Preservation",
    subtitle: "Heritage Protection",
    description:
      "The ultimate goal is long-term preservation. By shifting from reactive restoration to proactive conservation, we help museums protect invaluable cultural heritage for future generations.",
    image: "/images/preservation.jpg",
    features: ["Predictive degradation modeling", "Conservation priority queuing", "Digital twin integration"],
  },
];

/* ── Section Header ── */
function Header() {
  const ref = useRef(null);
  const isInView = useInView(ref, { once: true, amount: 0.5 });

  return (
    <motion.div
      ref={ref}
      initial={{ opacity: 0, y: 40 }}
      animate={isInView ? { opacity: 1, y: 0 } : { opacity: 0, y: 40 }}
      transition={{ duration: 0.8, ease: [0.16, 1, 0.3, 1] }}
      className="layout-container text-center mb-16 sm:mb-24"
    >
      <div className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-[#1a1a24] border border-[#2a2a35] mb-6">
        <span className="w-2 h-2 rounded-full bg-[#c9a84c] animate-pulse" />
        <span className="text-xs font-medium tracking-widest uppercase text-[#c9a84c]">
          Intelligent Workflow
        </span>
      </div>
      <h2 className="text-4xl sm:text-5xl md:text-6xl font-bold text-white mb-6 tracking-tight">
        AI-Powered Exhibit <span className="text-[#c9a84c] italic pr-2">Monitoring</span>
      </h2>
      <p className="max-w-4xl mx-auto text-lg text-[#8a8a9a] leading-relaxed text-center ">
        A comprehensive deep-learning solution designed specifically for the unique environment and challenges of preserving historical artifacts.
      </p>
    </motion.div>
  );
}

/* ── Individual Feature Row ── */
function FeatureRow({ item }) {
  const containerRef = useRef(null);
  const { scrollYProgress } = useScroll({
    target: containerRef,
    offset: ["start end", "end start"],
  });

  // Parallax effect for the image
  const imageY = useTransform(scrollYProgress, [0, 1], ["-10%", "10%"]);
  
  const textRef = useRef(null);
  const textInView = useInView(textRef, { once: true, amount: 0.4 });

  return (
    <div 
      ref={containerRef}
      className="relative layout-container layout-grid py-10 sm:py-16"
    >
      {/* ── Text Content ── */}
      <motion.div 
        ref={textRef}
        initial={{ opacity: 0, y: 24 }}
        animate={textInView ? { opacity: 1, y: 0 } : { opacity: 0, y: 24 }}
        transition={{ duration: 0.8, ease: [0.16, 1, 0.3, 1] }}
        className="w-full max-w-2xl lg:max-w-[34rem]"
      >
        <div className="flex items-baseline gap-4 mb-4">
          <span className="text-5xl sm:text-7xl font-light text-[#1a1a24] tracking-tighter" style={{ WebkitTextStroke: "1px rgba(201,168,76,0.3)" }}>
            {item.id}
          </span>
          <span className="text-sm font-semibold tracking-[0.2em] uppercase text-[#c9a84c]">
            {item.subtitle}
          </span>
        </div>
        
        <h3 className="text-3xl sm:text-4xl font-bold text-white mb-6">
          {item.title}
        </h3>
        
        <p className="text-[#a0a0b0] text-lg leading-relaxed mb-8">
          {item.description}
        </p>

        <ul className="space-y-4">
          {item.features.map((feat, i) => (
            <motion.li 
              key={i}
              initial={{ opacity: 0, y: 10 }}
              animate={textInView ? { opacity: 1, y: 0 } : {}}
              transition={{ duration: 0.5, delay: 0.3 + (i * 0.1) }}
              className="flex items-center gap-3 text-[#d0d0e0]"
            >
              <div className="flex-shrink-0 w-5 h-5 rounded-full bg-[#c9a84c]/10 flex items-center justify-center border border-[#c9a84c]/20">
                <svg className="w-3 h-3 text-[#c9a84c]" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M5 13l4 4L19 7" />
                </svg>
              </div>
              <span className="text-sm sm:text-base">{feat}</span>
            </motion.li>
          ))}
        </ul>
      </motion.div>

      {/* ── Image Content ── */}
      <motion.div 
        initial={{ opacity: 0, scale: 0.9 }}
        animate={textInView ? { opacity: 1, scale: 1 } : {}}
        transition={{ duration: 1, ease: [0.16, 1, 0.3, 1] }}
        className="w-full max-w-3xl h-[360px] sm:h-[460px] lg:h-[560px] relative rounded-3xl overflow-hidden group"
      >
        {/* Decorative corner accents */}
        <div className="absolute top-0 left-0 w-8 h-8 border-t-2 border-l-2 border-[#c9a84c]/50 rounded-tl-3xl z-20 pointer-events-none" />
        <div className="absolute bottom-0 right-0 w-8 h-8 border-b-2 border-r-2 border-[#c9a84c]/50 rounded-br-3xl z-20 pointer-events-none" />
        
        {/* Glow behind image */}
        <div className="absolute inset-4 bg-[#c9a84c] rounded-[40px] blur-[80px] opacity-10 group-hover:opacity-20 transition-opacity duration-700 z-0" />

        <div className="absolute inset-0 z-10 overflow-hidden rounded-2xl border border-white/[0.05] bg-[#0a0a0f]">
          <motion.img
            style={{ y: imageY, scale: 1.15 }}
            src={item.image}
            alt={item.title}
            className="w-full h-full object-cover opacity-80 mix-blend-lighten transition-opacity duration-700 group-hover:opacity-100 group-hover:mix-blend-normal"
          />
          {/* Subtle gradient overlay */}
          <div className="absolute inset-0 bg-gradient-to-tr from-[#050508]/80 via-transparent to-[#050508]/40" />
        </div>
      </motion.div>
    </div>
  );
}

/* ── Main Component ── */
export default function LandingScrollShowcase() {
  return (
    <section
      id="showcase"
      className="relative w-full py-20 sm:py-28 overflow-hidden"
      style={{ background: "linear-gradient(160deg, #060609 0%, #0b0d1a 35%, #080e14 65%, #06080d 100%)" }}
    >
      {/* Background ambient light */}
      <div className="absolute inset-0 pointer-events-none">
         <div className="absolute top-[20%] left-[-10%] w-[500px] h-[500px] rounded-full bg-[#c9a84c] opacity-[0.02] blur-[150px]" />
         <div className="absolute bottom-[20%] right-[-10%] w-[600px] h-[600px] rounded-full bg-blue-500 opacity-[0.02] blur-[150px]" />
      </div>

      <Header />

      <div className="relative flex flex-col gap-6 sm:gap-10">
        {/* Connecting line down the middle (desktop only) */}
        <div className="hidden lg:block absolute left-1/2 top-0 bottom-0 w-[1px] bg-gradient-to-b from-transparent via-white/[0.05] to-transparent -translate-x-1/2 z-0" />
        
        {showcaseData.map((item) => (
          <FeatureRow key={item.id} item={item} />
        ))}
      </div>
    </section>
  );
}
