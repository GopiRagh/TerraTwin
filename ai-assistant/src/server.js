
const express = require("express");
const cors = require("cors");

const { generateAIResponse } = require("./services/geminiService");
const { compareEarthAnalogs } = require("./services/terraTwinService");
const { detectQuestionIntent } = require("./services/questionRouter");

const app = express();

app.use(cors());
app.use(express.json({ limit: "1mb" }));

// Health check
app.get("/api/health", (req, res) => {
    res.json({
        status: "success",
        message: "TerraTwin AI backend is running"
    });
});

// Main AI chat endpoint
app.post("/api/chat", async (req, res) => {
    try {
        const { message, history = [] } = req.body;

        if (
            typeof message !== "string" ||
            !message.trim()
        ) {
            return res.status(400).json({
                status: "error",
                message: "Please provide a valid message."
            });
        }

        if (
            !Array.isArray(history) ||
            history.length > 8 ||
            !history.every((item) =>
                item &&
                ["user", "assistant"].includes(item.role) &&
                typeof item.content === "string" &&
                item.content.length <= 4000
            )
        ) {
            return res.status(400).json({
                status: "error",
                message: "Conversation history must contain up to eight valid chat messages."
            });
        }

        const recentHistory = history.slice(-8);

        // Step 1: Understand the question
        const intent = detectQuestionIntent(message);

        // Step 2: Ask for clarification if location is missing
        if (intent.type === "clarification") {
            return res.json({
                status: "success",
                intent: "clarification",
                reply: intent.message
            });
        }

        // Step 3: Handle general questions
        if (intent.type === "general") {
            const reply = await generateAIResponse(message, "", recentHistory);

            return res.json({
                status: "success",
                intent: "general",
                reply
            });
        }

        // Step 4: Fetch actual Python comparison results
        const comparison = await compareEarthAnalogs(
            intent.planet,
            intent.location
        );

        // Step 5: Pass actual results to Gemini
        const context = JSON.stringify(comparison.data);

        const reply = await generateAIResponse(
            message,
            context,
            recentHistory
        );

        // Step 6: Return the final response
        return res.json({
            status: "success",
            intent: "comparison",
            analysis_id: comparison.analysis_id,
            reply,
            comparison: comparison.data
        });

    } catch (error) {
        console.error("Chat API error:", error.message);

        return res.status(500).json({
            status: "error",
            message: error.message || "Unable to process your request."
        });
    }
});

// Handle malformed JSON requests
app.use((error, req, res, next) => {
    if (
        error instanceof SyntaxError &&
        error.status === 400 &&
        "body" in error
    ) {
        return res.status(400).json({
            status: "error",
            message: "Invalid JSON request body."
        });
    }

    console.error("Server error:", error.message);

    return res.status(500).json({
        status: "error",
        message: "Internal server error."
    });
});

// Start server
const PORT = process.env.PORT || 5001;

app.listen(PORT, () => {
    console.log(
        `TerraTwin AI server running at http://localhost:${PORT}`
    );
});
