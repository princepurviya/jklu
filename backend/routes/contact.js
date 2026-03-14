import express from "express";
import Contact from "../models/Contact.js";

const router = express.Router();

// POST /api/contact
router.post("/", async (req, res, next) => {
  try {
    const { name, email, subject, message } = req.body;
    if (!name || !email || !message) {
      return res.status(400).json({
        success: false,
        message: "Name, email and message are required",
      });
    }
    const contact = await Contact.create({
      name: name.trim(),
      email: email.trim(),
      subject: subject?.trim() || "",
      message: message.trim(),
    });
    res.status(201).json({
      success: true,
      message: "Thank you for contacting us. We will get back to you soon.",
      id: contact._id,
    });
  } catch (err) {
    next(err);
  }
});

export default router;
