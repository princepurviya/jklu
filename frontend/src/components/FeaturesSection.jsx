import { useRef } from "react";
import { motion, useInView } from "framer-motion";

const features = [
  {
    icon: (
      <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
      </svg>
    ),
    title: "Deep Learning Models",
    description:
      "YOLO, Faster R-CNN, and SSD models trained on real-world damage datasets for high-accuracy detection.",
  },
  {
    icon: (
      <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M13 10V3L4 14h7v7l9-11h-7z" />
      </svg>
    ),
    title: "Real-Time Processing",
    description:
      "Process images instantly and receive bounding-box annotations with class labels and confidence scores.",
  },
  {
    icon: (
      <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
      </svg>
    ),
    title: "Heritage Protection",
    description:
      "Early detection of cracks, potholes, and structural damage helps preserve cultural and historical sites.",
  },
];

const containerVariants = {
  hidden: {},
  visible: {
    transition: { staggerChildren: 0.2, delayChildren: 0.1 },
  },
};

const itemVariants = {
  hidden: { opacity: 0, y: 40, scale: 0.95 },
  visible: {
    opacity: 1,
    y: 0,
    scale: 1,
    transition: { type: "spring", stiffness: 100, damping: 16 },
  },
};

export default function FeaturesSection() {
  const ref = useRef(null);
  const isInView = useInView(ref, { once: true, amount: 0.2 });

  return (
    <section
      id="features"
      ref={ref}
      className="relative w-full py-24 sm:py-32 lg:py-36"
      style={{ background: "linear-gradient(145deg, #0e0e16 0%, #0a0d1f 40%, #0c1218 70%, #0e0e16 100%)" }}
    >
      {/* background decoration */}
      <div className="absolute inset-0 pointer-events-none overflow-hidden">
        <div
          className="absolute bottom-[-200px] left-1/2 -translate-x-1/2 w-[800px] h-[800px] rounded-full opacity-20"
          style={{ background: "radial-gradient(circle, rgba(201,168,76,0.05) 0%, transparent 55%)" }}
        />
      </div>

      <div className="relative layout-container">
        {/* header */}
        <motion.div
          initial="hidden"
          animate={isInView ? "visible" : "hidden"}
          variants={containerVariants}
          className="text-center mb-20 sm:mb-24"
        >
          <motion.span
            variants={itemVariants}
            className="inline-block px-5 py-2 rounded-full text-[11px] font-semibold tracking-[0.2em] uppercase bg-[#c9a84c]/[0.08] text-[#c9a84c] border border-[#c9a84c]/15 mb-7"
          >
            Technology
          </motion.span>

          <motion.h2
            variants={itemVariants}
            className="text-3xl sm:text-4xl lg:text-5xl font-extrabold text-white mb-5 leading-[1.1] tracking-tight"
          >
            Built with Cutting-Edge{" "}
            <span className="bg-gradient-to-r from-[#c9a84c] to-[#e8c547] bg-clip-text text-transparent">
              Technology
            </span>
          </motion.h2>

          <motion.div variants={itemVariants} className="flex justify-center px-2 sm:px-6 mt-2">
            <p className="w-full max-w-[760px] text-[#8a8480] text-center leading-relaxed px-6 py-5 rounded-2xl border border-white/[0.07] bg-white/[0.02]">
              Powered by state-of-the-art deep learning architectures trained on
              diverse real-world datasets.
            </p>
          </motion.div>
        </motion.div>

        {/* feature cards */}
        <motion.div
          initial="hidden"
          animate={isInView ? "visible" : "hidden"}
          variants={containerVariants}
          className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 items-stretch gap-8 lg:gap-10"
        >
          {features.map((feat) => (
            <motion.div
              key={feat.title}
              variants={itemVariants}
              className="group relative h-full p-8 rounded-3xl border border-white/[0.06] bg-gradient-to-b from-white/[0.03] to-transparent hover:border-[#c9a84c]/15 transition-all duration-500"
            >
              <div className="w-14 h-14 rounded-2xl bg-[#c9a84c]/[0.08] flex items-center justify-center text-[#c9a84c] mb-6 group-hover:bg-[#c9a84c]/[0.12] transition-colors duration-300">
                {feat.icon}
              </div>
              <h3 className="text-lg font-bold text-white mb-3 tracking-wide">
                {feat.title}
              </h3>
              <p className="text-sm text-[#8a8480] leading-relaxed min-h-[88px]">
                {feat.description}
              </p>
            </motion.div>
          ))}
        </motion.div>
      </div>

      {/* footer */}
      <div className="relative layout-container mt-24 sm:mt-28 lg:mt-32 pt-14 pb-14 border-t border-white/[0.06]">
        <div className="flex flex-col items-center justify-center gap-5 text-center">
          <div className="flex flex-wrap justify-center gap-6 sm:gap-8">
            {["Privacy Policy", "Terms of Service", "Contact Us"].map((link) => (
              <a key={link} href="#" className="text-xs font-semibold tracking-wider text-[#8a8480] uppercase hover:text-[#c9a84c] transition-colors">
                {link}
              </a>
            ))}
          </div>
          <p className="text-xs text-[#8a8480]/40">
            © 2026 Museum AI Platform — Protecting Heritage with Intelligence
          </p>
        </div>
      </div>
    </section>
  );
}
