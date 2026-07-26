const CONFIG = {
    backendUrl: "http://localhost:8000" // Configure via environment or storage
};

function pollApi() {
    fetch(`${CONFIG.backendUrl}/api/live_picks`)
        .then(res => res.json())
        .then(data => console.log(data))
        .catch(err => console.error(err));
}
