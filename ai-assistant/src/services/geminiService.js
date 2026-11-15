
const { ai, MODEL_NAME } = require("../config/gemini");

const SYSTEM_INSTRUCTION = `
You are TerraTwin AI, the research assistant for the
TerraTwin Earth Analog Discovery Platform.

Your responsibilities:
- Explain Earth analog discovery.
- Answer questions about Moon and Mars.
- Explain terrain and geographical characteristics.
- Interpret actual similarity rankings.
- Explain NASA datasets and planetary research.

STRICT RULES:
1. Use simple, professional and friendly language.
2. Never invent similarity scores, rankings or measurements.
3. When comparison data is supplied, use only its actual values.
4. Clearly explain the ranking and similarity score.
5. Mention important warnings and data limitations.
6. Do not claim that a comparison was performed if no results were supplied.
7. If information is unavailable, say so honestly.
8. Keep answers relevant to TerraTwin.
`;

async function generateAIResponse(userMessage, context = "", history = []) {
    if (!userMessage || typeof userMessage !== "string") {
        throw new Error("A valid user message is required.");
    }

    const recentConversation = history
        .slice(-8)
        .map(({ role, content }) => `${role === "assistant" ? "TERRATWIN AI" : "USER"}: ${content}`)
        .join("\n");

    const prompt = `
${SYSTEM_INSTRUCTION}

RECENT CONVERSATION:
${recentConversation || "This is the start of the conversation."}

ACTUAL TERRATWIN ANALYSIS DATA:
${context || "No live comparison data was provided."}

USER QUESTION:
${userMessage}
`;

    try {
        const response = await ai.models.generateContent({
            model: MODEL_NAME,
            contents: prompt
        });

        return response.text;
    } catch (error) {
        console.error("Gemini service error:", error.message);
        throw new Error("Unable to generate an AI response.");
    }
}

module.exports = {
    generateAIResponse
};
