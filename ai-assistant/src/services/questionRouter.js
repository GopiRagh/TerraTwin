
function detectQuestionIntent(message) {
    const text = message.trim();

    const planetMatch = text.match(/\b(moon|mars)\b/i);

    if (!planetMatch) {
        return { type: "general" };
    }

    const planet = planetMatch[1].toLowerCase();

    
    const patterns = [
        /(?:is\s+)?similar\s+to\s+(.+?)\s+(?:on|in)\s+(?:the\s+)?(?:moon|mars)\b/i,

        /(?:compare|analyze|analyse|find|show|identify|rank|discover)\s+(?:the\s+)?(.+?)\s+(?:on|in)\s+(?:the\s+)?(?:moon|mars)\b/i,

        /(?:for|of)\s+(.+?)\s+(?:on|in)\s+(?:the\s+)?(?:moon|mars)\b/i
];


    let location = null;

    for (const pattern of patterns) {
        const match = text.match(pattern);

        if (match && match[1]) {
            location = match[1].trim();
            break;
        }
    }

    if (location) {
        location = location
            .replace(/^(?:(?:the|best|closest)\s+)?(?:(?:earth|terrestrial)\s+)?analogs?\s*/i, "")
            .replace(/^(?:for|of)\s+/i, "")
            .replace(/[?.!,]+$/, "")
            .trim();
    }

    if (!location || location.length < 2) {
        return {
            type: "clarification",
            planet,
            message: `Which specific location on ${planet} would you like me to compare with Earth analogs?`
        };
    }

    return {
        type: "comparison",
        planet,
        location
    };
}

module.exports = {
    detectQuestionIntent
};
