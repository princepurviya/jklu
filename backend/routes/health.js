import express from "express";
import mongoose from "mongoose";

const router = express.Router();

router.get("/", (req, res) => {
  res.json({
    success: true,
    message: "Museum AI API is running",
    timestamp: new Date().toISOString(),
    uptime: process.uptime(),
  });
});

router.get("/db", async (req, res) => {
  try {
    const state = mongoose.connection.readyState;
    const states = ["disconnected", "connected", "connecting", "disconnecting"];
    res.json({
      success: state === 1,
      db: states[state] || "unknown",
    });
  } catch (err) {
    res.status(500).json({ success: false, message: err.message });
  }
});

export default router;
