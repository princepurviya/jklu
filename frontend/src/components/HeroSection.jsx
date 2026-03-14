import { useState } from "react";
import { motion } from "framer-motion";

const fadeUp = (delay = 0) => ({
  initial: { opacity: 0, y: 30 },
  animate: { opacity: 1, y: 0, transition: { duration: 0.8, delay, ease: [0.22, 1, 0.36, 1] } },
});

export default function HeroSection() {
  const [starting, setStarting] = useState(false);

  const handleStartSystem = () => {
    if (starting) return;
    setStarting(true);
    window.location.href = "http://localhost:8501";
    setTimeout(() => setStarting(false), 1000);
  };

  return (
    <section
      className="relative min-h-screen flex items-center justify-center overflow-hidden pt-10 sm:pt-16 md:pt-24 pb-16 md:pb-24"
      style={{ background: "linear-gradient(135deg, #0a0a0f 0%, #0d0b1e 40%, #091018 70%, #0a0a0f 100%)" }}
    >
      {/* ── background effects ── */}
      <div className="absolute inset-0 pointer-events-none">
        {/* radial glows */}
        <div className="absolute top-1/3 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[700px] h-[700px] rounded-full opacity-40"
          style={{ background: "radial-gradient(circle, rgba(201,168,76,0.07) 0%, transparent 55%)" }}
        />
        <div className="absolute bottom-0 right-0 w-[500px] h-[500px] rounded-full opacity-30"
          style={{ background: "radial-gradient(circle, rgba(201,168,76,0.05) 0%, transparent 60%)" }}
        />

        {/* subtle grid overlay */}
        <div className="absolute inset-0 opacity-[0.015]"
          style={{
            backgroundImage: `linear-gradient(rgba(201,168,76,0.5) 1px, transparent 1px), linear-gradient(90deg, rgba(201,168,76,0.5) 1px, transparent 1px)`,
            backgroundSize: "60px 60px",
          }}
        />

        {/* floating particles */}
        {[...Array(5)].map((_, i) => (
          <motion.div
            key={i}
            className="absolute w-1 h-1 rounded-full bg-[#c9a84c]/30"
            style={{
              top: `${20 + i * 15}%`,
              left: `${10 + i * 20}%`,
            }}
            animate={{
              y: [0, -30, 0],
              opacity: [0.2, 0.6, 0.2],
            }}
            transition={{
              duration: 3 + i,
              repeat: Infinity,
              ease: "easeInOut",
              delay: i * 0.5,
            }}
          />
        ))}
      </div>

      <div className="relative w-full max-w-4xl mx-auto text-center px-6">
        {/* badge */}
        <motion.div {...fadeUp(0)} className="mb-4">
          <span className="inline-flex items-center gap-2.5 px-6 py-2.5 rounded-full text-xs sm:text-sm font-semibold tracking-[0.14em] uppercase bg-[#c9a84c]/[0.08] text-[#c9a84c] border border-[#c9a84c]/15">
            <span className="w-1.5 h-1.5 rounded-full bg-[#c9a84c] animate-pulse" />
            AI-Powered Exhibit Monitoring
          </span>
        </motion.div>

        {/* title */}
        <motion.h1
          {...fadeUp(0.15)}
          className="text-4xl sm:text-6xl lg:text-[4.8rem] font-extrabold text-white leading-[1.1] tracking-tight"
        >
          <span className="block">Protecting Heritage</span>
          <span className="block mt-2 text-3xl sm:text-5xl lg:text-[4.3rem] leading-[1.1]">with{" "}
            <span className="bg-gradient-to-r from-[#c9a84c] via-[#e8c547] to-[#d4a843] bg-clip-text text-transparent">
              Artificial Intelligence
            </span>
          </span>
        </motion.h1>

        {/* subtitle */}
        <div className="mt-6 mb-8 sm:mb-12 flex justify-center">
          <motion.p
            {...fadeUp(0.3)}
            className="w-full max-w-[680px] text-base sm:text-lg lg:text-[1.16rem] text-[#8a8480] leading-[1.7] px-4"
          >
            Advanced computer vision monitors museum exhibits 24/7, detecting
            damage, misplacement, and structural deterioration before it&#39;s too
            late.
          </motion.p>
        </div>

        <motion.div {...fadeUp(0.45)} className="flex justify-center">
          <button
            type="button"
            onClick={handleStartSystem}
            disabled={starting}
            className="inline-flex items-center justify-center min-w-[180px] px-8 py-3.5 rounded-full bg-gradient-to-r from-[#c9a84c] to-[#e8c547] text-[#0a0a0f] font-bold text-sm tracking-wide shadow-lg shadow-[#c9a84c]/20 hover:shadow-xl hover:shadow-[#c9a84c]/30 hover:-translate-y-0.5 transition-all duration-300"
          >
            {starting ? "Starting..." : "Start System"}
          </button>
        </motion.div>
      </div>

      {/* scroll indicator */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 1.5, duration: 1 }}
        className="absolute bottom-10 left-1/2 -translate-x-1/2"
      >
        <div className="w-7 h-11 rounded-full border-2 border-white/15 flex justify-center pt-2.5">
          <motion.div
            animate={{ y: [0, 9, 0] }}
            transition={{ duration: 1.6, repeat: Infinity, ease: "easeInOut" }}
            className="w-1.5 h-1.5 rounded-full bg-[#c9a84c]"
          />
        </div>
      </motion.div>
    </section>
  );
}
