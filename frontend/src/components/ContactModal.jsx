import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { api } from "../api/client.js";

export default function ContactModal({ isOpen, onClose }) {
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [subject, setSubject] = useState("");
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");
  const [success, setSuccess] = useState(false);
  const [submitting, setSubmitting] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    setSubmitting(true);
    try {
      await api.contact({ name, email, subject, message });
      setSuccess(true);
      setName("");
      setEmail("");
      setSubject("");
      setMessage("");
      setTimeout(() => {
        setSuccess(false);
        onClose();
      }, 1500);
    } catch (err) {
      setError(err.message || "Failed to send message");
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <AnimatePresence>
      {isOpen && (
        <>
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black/60 backdrop-blur-sm z-50"
            onClick={onClose}
          />
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.95 }}
            className="fixed left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2 w-full max-w-md max-h-[90vh] overflow-y-auto rounded-2xl border border-white/10 bg-[#12121a] p-6 sm:p-8 shadow-2xl z-50"
          >
            <div className="flex justify-between items-center mb-6">
              <h2 className="text-xl font-bold text-white">Contact Us</h2>
              <button
                type="button"
                onClick={onClose}
                className="p-2 rounded-lg text-[#8a8480] hover:text-white hover:bg-white/10 transition-colors"
                aria-label="Close"
              >
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>
            {success ? (
              <div className="py-8 text-center">
                <div className="inline-flex w-12 h-12 rounded-full bg-[#c9a84c]/20 items-center justify-center mb-4">
                  <svg className="w-6 h-6 text-[#c9a84c]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                  </svg>
                </div>
                <p className="text-white font-medium">Message sent successfully.</p>
                <p className="text-sm text-[#8a8480] mt-1">We will get back to you soon.</p>
              </div>
            ) : (
              <form onSubmit={handleSubmit} className="space-y-4">
                {error && (
                  <div className="rounded-lg bg-red-500/10 border border-red-500/20 text-red-400 text-sm px-4 py-2">
                    {error}
                  </div>
                )}
                <div>
                  <label className="block text-sm font-medium text-[#a0998a] mb-1">Name *</label>
                  <input
                    type="text"
                    value={name}
                    onChange={(e) => setName(e.target.value)}
                    required
                    className="w-full rounded-lg border border-white/10 bg-white/5 px-4 py-3 text-white placeholder-[#6b6560] focus:border-[#c9a84c]/50 focus:outline-none focus:ring-1 focus:ring-[#c9a84c]/30"
                    placeholder="Your name"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-[#a0998a] mb-1">Email *</label>
                  <input
                    type="email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    required
                    className="w-full rounded-lg border border-white/10 bg-white/5 px-4 py-3 text-white placeholder-[#6b6560] focus:border-[#c9a84c]/50 focus:outline-none focus:ring-1 focus:ring-[#c9a84c]/30"
                    placeholder="you@example.com"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-[#a0998a] mb-1">Subject</label>
                  <input
                    type="text"
                    value={subject}
                    onChange={(e) => setSubject(e.target.value)}
                    className="w-full rounded-lg border border-white/10 bg-white/5 px-4 py-3 text-white placeholder-[#6b6560] focus:border-[#c9a84c]/50 focus:outline-none focus:ring-1 focus:ring-[#c9a84c]/30"
                    placeholder="Inquiry subject"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-[#a0998a] mb-1">Message *</label>
                  <textarea
                    value={message}
                    onChange={(e) => setMessage(e.target.value)}
                    required
                    rows={4}
                    className="w-full rounded-lg border border-white/10 bg-white/5 px-4 py-3 text-white placeholder-[#6b6560] focus:border-[#c9a84c]/50 focus:outline-none focus:ring-1 focus:ring-[#c9a84c]/30 resize-none"
                    placeholder="Your message"
                  />
                </div>
                <button
                  type="submit"
                  disabled={submitting}
                  className="w-full py-3 rounded-lg bg-gradient-to-r from-[#c9a84c] to-[#e8c547] text-[#0a0a0f] font-bold hover:opacity-90 disabled:opacity-60 transition-opacity"
                >
                  {submitting ? "Sending…" : "Send message"}
                </button>
              </form>
            )}
          </motion.div>
        </>
      )}
    </AnimatePresence>
  );
}
