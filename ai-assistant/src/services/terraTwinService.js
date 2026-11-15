
require("dotenv").config();

const TERRATWIN_API_URL =
    process.env.TERRATWIN_API_URL || "http://127.0.0.1:8000";

async function compareEarthAnalogs(targetPlanet, targetLocation) {
    if (!["moon", "mars"].includes(targetPlanet.toLowerCase())) {
        throw new Error("Target planet must be Moon or Mars.");
    }

    if (!targetLocation || !targetLocation.trim()) {
        throw new Error("Target location is required.");
    }

    try {
        const response = await fetch(
            `${TERRATWIN_API_URL}/api/analyze/compare`,
            {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    target_planet: targetPlanet.toLowerCase(),
                    target_location: targetLocation.trim()
                }),
                signal: AbortSignal.timeout(30000)
            }
        );

        const result = await response.json();

        if (!response.ok) {
            throw new Error(
                result.detail || "TerraTwin comparison failed."
            );
        }

        return result;

    } catch (error) {
        if (error.name === "TimeoutError") {
            throw new Error("TerraTwin backend request timed out.");
        }

        if (error.name === "TypeError") {
            throw new Error(
                "Unable to connect to the TerraTwin Python backend."
            );
        }

        throw error;
    }
}

module.exports = {
    compareEarthAnalogs
};
