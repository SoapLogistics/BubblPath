console.log("[SOLOMON] content.js initialized.");
function extractGitHub() {
    let context = { source: "github" };
    const titleEl = document.querySelector(".gh-header-title .js-issue-title");
    if (titleEl) context.title = titleEl.textContent.trim();
    const bodyEl = document.querySelector(".comment-body");
    if (bodyEl) context.body = bodyEl.textContent.trim();
    const diffEls = document.querySelectorAll(".diff-table tr");
    if (diffEls.length > 0) {
        context.diff = Array.from(diffEls).map(tr => tr.textContent.trim()).join("\n");
    }
    return context;
}
function extractContext() {
    const host = window.location.hostname;
    if (host.includes("casino") || host.includes("bet")) {
        return { error: "casino_blocked" };
    }
    if (host.includes("github.com")) {
        return extractGitHub();
    }
    return { title: document.title, url: window.location.href };
}
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    if (request.action === "extract_context") {
        sendResponse(extractContext());
    }
    return true;
});
