// Solomon Browser Companion Config
// Export object avoids process.env in the browser context to ensure portability.

export const config = {
    // Configurable backend URL
    backendUrl: "http://127.0.0.0:18789",

    // Poll less often when inactive
    pollIntervalActiveMs: 2000,
    pollIntervalInactiveMs: 15000,

    // Debounce page scans
    scanDebounceMs: 1000,

    // Runtime guardrails
    forbiddenActions: [
        "wagering",
        "trading",
        "purchasing",
        "banking",
        "automatic_promotion"
    ]
};
