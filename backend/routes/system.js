import express from "express";
import path from "path";
import { fileURLToPath } from "url";
import { spawn } from "child_process";

const router = express.Router();

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const repoRoot = path.resolve(__dirname, "../..");

let systemProcess = null;

router.post("/start", (req, res) => {
  try {
    if (systemProcess && !systemProcess.killed) {
      return res.json({
        success: true,
        status: "already_running",
        message: "System is already running",
        dashboardUrl: `http://localhost:${process.env.STREAMLIT_PORT || 8501}`,
      });
    }

    const port = String(process.env.STREAMLIT_PORT || 8501);
    const pythonCmd = process.env.PYTHON_CMD || "python";
    const args = [
      "-m",
      "streamlit",
      "run",
      "app.py",
      "--server.headless",
      "true",
      "--server.port",
      port,
    ];

    const child = spawn(pythonCmd, args, {
      cwd: repoRoot,
      detached: true,
      stdio: "ignore",
      shell: process.platform === "win32",
    });

    child.once("error", (err) => {
      console.error("Failed to start app.py:", err.message);
    });

    child.unref();
    systemProcess = child;

    return res.status(202).json({
      success: true,
      status: "started",
      message: "System start requested",
      dashboardUrl: `http://localhost:${port}`,
    });
  } catch (err) {
    return res.status(500).json({
      success: false,
      message: err.message || "Failed to start system",
    });
  }
});

export default router;
